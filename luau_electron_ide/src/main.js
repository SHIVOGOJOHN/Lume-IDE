const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");
const fsp = require("fs/promises");
const os = require("os");
const https = require("https");
const { spawn } = require("child_process");

const APP_NAME = "Lume";
const DEFAULT_LUAU_EXE = "C:\\luau\\luau.exe";
const LUAU_RELEASE_API = "https://api.github.com/repos/luau-lang/luau/releases/latest";
let mainWindow = null;
let shellProcess = null;
let shellType = "PowerShell";
let shellCwd = process.cwd();
let shellOptionsCache = null;

function getStatePath() {
  return path.join(app.getPath("userData"), "ide-state.json");
}

function getRuntimeRoot() {
  return path.join(app.getPath("userData"), "runtime");
}

function requestJson(url) {
  return new Promise((resolve, reject) => {
    const request = https.get(
      url,
      {
        headers: {
          Accept: "application/vnd.github+json",
          "User-Agent": `${APP_NAME}/1.0`
        }
      },
      (response) => {
        let data = "";
        response.on("data", (chunk) => {
          data += chunk.toString();
        });
        response.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(error);
          }
        });
      }
    );
    request.on("error", reject);
  });
}

function downloadFile(url, destination) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(destination);
    const request = https.get(
      url,
      {
        headers: {
          "User-Agent": `${APP_NAME}/1.0`
        }
      },
      (response) => {
        if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
          file.close();
          fs.rmSync(destination, { force: true });
          downloadFile(response.headers.location, destination).then(resolve).catch(reject);
          return;
        }
        response.pipe(file);
        file.on("finish", () => file.close(resolve));
      }
    );
    request.on("error", (error) => {
      file.close();
      fs.rm(destination, { force: true }, () => reject(error));
    });
  });
}

function resolveExistingLuauPath(candidate) {
  const candidates = [
    candidate,
    DEFAULT_LUAU_EXE,
    path.join(path.dirname(app.getPath("exe")), "luau.exe"),
    path.join(getRuntimeRoot(), "luau.exe")
  ].filter(Boolean);
  for (const item of candidates) {
    if (fs.existsSync(item)) {
      return item;
    }
  }
  return null;
}

async function ensureLuauRuntime(candidatePath) {
  const existing = resolveExistingLuauPath(candidatePath);
  if (existing) {
    return existing;
  }
  await fsp.mkdir(getRuntimeRoot(), { recursive: true });
  const release = await requestJson(LUAU_RELEASE_API);
  const asset = (release.assets || []).find((entry) => {
    const name = String(entry.name || "").toLowerCase();
    return name.includes("windows") && name.endsWith(".zip");
  });
  if (!asset?.browser_download_url) {
    throw new Error("No Windows Luau runtime asset found.");
  }
  const archivePath = path.join(getRuntimeRoot(), "luau-runtime.zip");
  const extractDir = path.join(getRuntimeRoot(), "extract");
  await downloadFile(asset.browser_download_url, archivePath);
  await fsp.rm(extractDir, { recursive: true, force: true });
  await fsp.mkdir(extractDir, { recursive: true });
  await new Promise((resolve, reject) => {
    const child = spawn(
      "powershell.exe",
      [
        "-NoLogo",
        "-NoProfile",
        "-Command",
        `Expand-Archive -LiteralPath '${archivePath.replace(/'/g, "''")}' -DestinationPath '${extractDir.replace(/'/g, "''")}' -Force`
      ],
      { windowsHide: true }
    );
    child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`Expand-Archive failed with exit code ${code}`))));
    child.on("error", reject);
  });
  const exePath = findLuauExe(extractDir);
  if (!exePath) {
    throw new Error("Downloaded Luau archive did not contain luau.exe.");
  }
  const runtimePath = path.join(getRuntimeRoot(), "luau.exe");
  await fsp.copyFile(exePath, runtimePath);
  return runtimePath;
}

function findLuauExe(rootDir) {
  const stack = [rootDir];
  while (stack.length) {
    const current = stack.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(full);
      } else if (entry.name.toLowerCase() === "luau.exe") {
        return full;
      }
    }
  }
  return null;
}

function detectGitBash() {
  const candidates = [
    "C:\\Program Files\\Git\\bin\\bash.exe",
    "C:\\Program Files\\Git\\usr\\bin\\bash.exe",
    "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
    "C:\\Program Files (x86)\\Git\\usr\\bin\\bash.exe"
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) || null;
}

function getShellOptions() {
  if (shellOptionsCache) {
    return shellOptionsCache;
  }
  const options = [
    { label: "PowerShell", executable: "powershell.exe", args: ["-NoLogo"] },
    { label: "Command Prompt", executable: "cmd.exe", args: ["/Q"] }
  ];
  const gitBash = detectGitBash();
  if (gitBash) {
    options.push({ label: "Git Bash", executable: gitBash, args: ["--login", "-i"] });
  }
  shellOptionsCache = options;
  return options;
}

function resolveShell(type) {
  return getShellOptions().find((option) => option.label === type) || getShellOptions()[0];
}

function emit(channel, payload) {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send(channel, payload);
  }
}

function stopShell() {
  if (!shellProcess) {
    return;
  }
  shellProcess.removeAllListeners();
  shellProcess.kill();
  shellProcess = null;
}

function startShell({ type, cwd }) {
  stopShell();
  const resolved = resolveShell(type || shellType);
  shellType = resolved.label;
  shellCwd = cwd || shellCwd || process.cwd();
  shellProcess = spawn(resolved.executable, resolved.args, {
    cwd: shellCwd,
    env: { ...process.env, TERM: "xterm-256color" },
    windowsHide: true,
    stdio: "pipe"
  });

  shellProcess.stdout.on("data", (chunk) => emit("shell:data", { stream: "stdout", data: chunk.toString() }));
  shellProcess.stderr.on("data", (chunk) => emit("shell:data", { stream: "stderr", data: chunk.toString() }));
  shellProcess.on("exit", (code) => {
    emit("shell:exit", { code, shellType });
    shellProcess = null;
  });
  shellProcess.on("error", (error) => emit("shell:error", { message: error.message }));

  emit("shell:started", { shellType, cwd: shellCwd, options: getShellOptions().map(({ label }) => label) });
  return { shellType, cwd: shellCwd, options: getShellOptions().map(({ label }) => label) };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 980,
    minWidth: 1180,
    minHeight: 760,
    backgroundColor: "#0f1117",
    title: "Luau Electron IDE",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });
  mainWindow.loadFile(path.join(__dirname, "index.html"));
}

async function loadState() {
  const statePath = getStatePath();
  try {
    const raw = await fsp.readFile(statePath, "utf8");
    return JSON.parse(raw);
  } catch (_error) {
    return {};
  }
}

async function saveState(state) {
  const statePath = getStatePath();
  await fsp.mkdir(path.dirname(statePath), { recursive: true });
  await fsp.writeFile(statePath, JSON.stringify(state, null, 2), "utf8");
}

async function readDirectory(targetPath) {
  const entries = await fsp.readdir(targetPath, { withFileTypes: true });
  return entries
    .filter((entry) => !["node_modules", "__pycache__"].includes(entry.name))
    .sort((a, b) => {
      if (a.isDirectory() !== b.isDirectory()) {
        return a.isDirectory() ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    })
    .map((entry) => {
      const fullPath = path.join(targetPath, entry.name);
      return {
        name: entry.name,
        path: fullPath,
        kind: entry.isDirectory() ? "directory" : "file"
      };
    });
}

async function removePath(targetPath) {
  const stats = await fsp.stat(targetPath);
  if (stats.isDirectory()) {
    await fsp.rm(targetPath, { recursive: true, force: true });
    return;
  }
  await fsp.unlink(targetPath);
}

async function runLuau({ luauPath, filePath, content, projectRoot }) {
  const resolvedLuauPath = await ensureLuauRuntime(luauPath);
  let executionPath = filePath;
  let tempPath = null;
  if (!executionPath) {
    tempPath = path.join(os.tmpdir(), `luau-electron-${Date.now()}.luau`);
    await fsp.writeFile(tempPath, content || "", "utf8");
    executionPath = tempPath;
  }
  const cwd = filePath ? path.dirname(filePath) : projectRoot || process.cwd();

  return new Promise((resolve) => {
    const child = spawn(resolvedLuauPath, [executionPath], {
      cwd,
      windowsHide: true
    });
    let stdout = "";
    let stderr = "";
    let finished = false;
    const timeout = setTimeout(() => {
      if (finished) {
        return;
      }
      finished = true;
      child.kill();
      resolve({ stdout, stderr: `${stderr}\nTimed out after 30 seconds.`, code: -1, cwd, executionPath, luauPath: resolvedLuauPath });
    }, 30000);

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", (error) => {
      if (finished) {
        return;
      }
      finished = true;
      clearTimeout(timeout);
      resolve({ stdout, stderr: `${stderr}\n${error.message}`, code: -1, cwd, executionPath, luauPath: resolvedLuauPath });
    });
    child.on("close", async (code) => {
      if (finished) {
        return;
      }
      finished = true;
      clearTimeout(timeout);
      if (tempPath) {
        await fsp.rm(tempPath, { force: true });
      }
      resolve({ stdout, stderr, code, cwd, executionPath, luauPath: resolvedLuauPath });
    });
  });
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle("state:load", async () => loadState());
  ipcMain.handle("state:save", async (_event, state) => saveState(state));
  ipcMain.handle("shell:getOptions", async () => getShellOptions().map(({ label }) => label));
  ipcMain.handle("shell:start", async (_event, payload) => startShell(payload || {}));
  ipcMain.handle("shell:restart", async (_event, payload) => startShell(payload || {}));
  ipcMain.handle("shell:write", async (_event, data) => {
    if (shellProcess && shellProcess.stdin.writable) {
      shellProcess.stdin.write(data);
    }
    return true;
  });
  ipcMain.handle("dialog:openFolder", async (_event, initialPath) => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openDirectory"],
      defaultPath: initialPath || process.cwd()
    });
    return result.canceled ? null : result.filePaths[0];
  });
  ipcMain.handle("dialog:openFile", async (_event, initialPath) => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openFile"],
      defaultPath: initialPath || process.cwd()
    });
    return result.canceled ? null : result.filePaths[0];
  });
  ipcMain.handle("dialog:saveFile", async (_event, payload) => {
    const result = await dialog.showSaveDialog(mainWindow, {
      defaultPath: payload?.defaultPath || undefined,
      filters: [
        { name: "Luau Files", extensions: ["luau", "lua"] },
        { name: "All Files", extensions: ["*"] }
      ]
    });
    return result.canceled ? null : result.filePath;
  });
  ipcMain.handle("dialog:chooseLuauPath", async (_event, initialPath) => {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ["openFile"],
      defaultPath: initialPath || DEFAULT_LUAU_EXE,
      filters: [
        { name: "Executable", extensions: ["exe"] },
        { name: "All Files", extensions: ["*"] }
      ]
    });
    return result.canceled ? null : result.filePaths[0];
  });
  ipcMain.handle("fs:readDir", async (_event, targetPath) => readDirectory(targetPath));
  ipcMain.handle("fs:readFile", async (_event, targetPath) => fsp.readFile(targetPath, "utf8"));
  ipcMain.handle("fs:writeFile", async (_event, payload) => {
    await fsp.mkdir(path.dirname(payload.path), { recursive: true });
    await fsp.writeFile(payload.path, payload.content, "utf8");
    return true;
  });
  ipcMain.handle("fs:mkdir", async (_event, targetPath) => {
    await fsp.mkdir(targetPath, { recursive: true });
    return true;
  });
  ipcMain.handle("fs:rename", async (_event, payload) => {
    await fsp.rename(payload.from, payload.to);
    return true;
  });
  ipcMain.handle("fs:delete", async (_event, targetPath) => {
    await removePath(targetPath);
    return true;
  });
  ipcMain.handle("fs:exists", async (_event, targetPath) => fs.existsSync(targetPath));
  ipcMain.handle("run:luau", async (_event, payload) => runLuau(payload));
  ipcMain.handle("luau:ensure", async (_event, candidatePath) => ensureLuauRuntime(candidatePath));

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("before-quit", () => stopShell());
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
