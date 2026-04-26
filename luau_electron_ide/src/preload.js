const { contextBridge, ipcRenderer, clipboard } = require("electron");

contextBridge.exposeInMainWorld("desktopAPI", {
  loadState: () => ipcRenderer.invoke("state:load"),
  saveState: (state) => ipcRenderer.invoke("state:save", state),
  getShellOptions: () => ipcRenderer.invoke("shell:getOptions"),
  startShell: (payload) => ipcRenderer.invoke("shell:start", payload),
  restartShell: (payload) => ipcRenderer.invoke("shell:restart", payload),
  writeShell: (data) => ipcRenderer.invoke("shell:write", data),
  onShellData: (handler) => ipcRenderer.on("shell:data", (_event, payload) => handler(payload)),
  onShellExit: (handler) => ipcRenderer.on("shell:exit", (_event, payload) => handler(payload)),
  onShellStarted: (handler) => ipcRenderer.on("shell:started", (_event, payload) => handler(payload)),
  onShellError: (handler) => ipcRenderer.on("shell:error", (_event, payload) => handler(payload)),
  openFolderDialog: (initialPath) => ipcRenderer.invoke("dialog:openFolder", initialPath),
  openFileDialog: (initialPath) => ipcRenderer.invoke("dialog:openFile", initialPath),
  saveFileDialog: (payload) => ipcRenderer.invoke("dialog:saveFile", payload),
  chooseLuauPathDialog: (initialPath) => ipcRenderer.invoke("dialog:chooseLuauPath", initialPath),
  readDir: (targetPath) => ipcRenderer.invoke("fs:readDir", targetPath),
  readFile: (targetPath) => ipcRenderer.invoke("fs:readFile", targetPath),
  writeFile: (payload) => ipcRenderer.invoke("fs:writeFile", payload),
  mkdir: (targetPath) => ipcRenderer.invoke("fs:mkdir", targetPath),
  renamePath: (payload) => ipcRenderer.invoke("fs:rename", payload),
  deletePath: (targetPath) => ipcRenderer.invoke("fs:delete", targetPath),
  pathExists: (targetPath) => ipcRenderer.invoke("fs:exists", targetPath),
  ensureLuauRuntime: (candidatePath) => ipcRenderer.invoke("luau:ensure", candidatePath),
  runLuau: (payload) => ipcRenderer.invoke("run:luau", payload),
  copyText: (text) => clipboard.writeText(text)
});
