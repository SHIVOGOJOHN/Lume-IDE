(function () {
  const DEFAULT_LUAU_EXE = "C:\\luau\\luau.exe";
  const KEYWORDS = [
    "and",
    "break",
    "continue",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while"
  ];
  const BUILTINS = [
    "assert",
    "Color3",
    "CFrame",
    "Enum",
    "Instance",
    "Vector2",
    "Vector3",
    "error",
    "game",
    "getmetatable",
    "ipairs",
    "math",
    "next",
    "pairs",
    "pcall",
    "print",
    "require",
    "script",
    "string",
    "table",
    "task",
    "tonumber",
    "tostring",
    "type",
    "utf8",
    "warn",
    "workspace"
  ];

  const pathUtils = {
    normalize(input) {
      return (input || "").replace(/\//g, "\\");
    },
    basename(input) {
      const normalized = pathUtils.normalize(input).replace(/\\+$/, "");
      const parts = normalized.split("\\");
      return parts[parts.length - 1] || normalized;
    },
    dirname(input) {
      const normalized = pathUtils.normalize(input).replace(/\\+$/, "");
      const parts = normalized.split("\\");
      parts.pop();
      return parts.join("\\") || normalized;
    },
    join(...parts) {
      return pathUtils.normalize(parts.join("\\").replace(/\\+/g, "\\"));
    },
    extname(input) {
      const name = pathUtils.basename(input);
      const index = name.lastIndexOf(".");
      return index >= 0 ? name.slice(index).toLowerCase() : "";
    },
    relative(root, target) {
      const normalizedRoot = pathUtils.normalize(root).toLowerCase();
      const normalizedTarget = pathUtils.normalize(target);
      if (normalizedTarget.toLowerCase().startsWith(normalizedRoot)) {
        return normalizedTarget.slice(root.length).replace(/^\\/, "") || pathUtils.basename(target);
      }
      return normalizedTarget;
    },
    bash(input) {
      const normalized = pathUtils.normalize(input);
      const drive = normalized.slice(0, 1).toLowerCase();
      return `/${drive}${normalized.slice(2).replace(/\\/g, "/")}`;
    }
  };

  const icons = {
    menu: '<svg viewBox="0 0 16 16"><path d="M2 4h12v1.8H2zm0 3.9h12v1.8H2zm0 3.9h12v1.8H2z"/></svg>',
    explorer: '<svg viewBox="0 0 16 16"><path d="M2 3h12v10H2zM6 3v10" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    panels: '<svg viewBox="0 0 16 16"><path d="M2 3h12v10H2zM2 11h12" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    outline: '<svg viewBox="0 0 16 16"><path d="M3 4h10v1.5H3zm2 3.2h8v1.5H5zm2 3.2h6v1.5H7z"/></svg>',
    newTab: '<svg viewBox="0 0 16 16"><path d="M7 2h2v5h5v2H9v5H7V9H2V7h5z"/></svg>',
    run: '<svg viewBox="0 0 16 16"><path d="M4 2.8 13 8l-9 5.2z"/></svg>',
    stop: '<svg viewBox="0 0 16 16"><path d="M4 4h8v8H4z"/></svg>',
    find: '<svg viewBox="0 0 16 16"><path d="M7 2.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Zm4.1 7.7 2.6 2.6-1 1-2.6-2.6z"/></svg>',
    refresh: '<svg viewBox="0 0 16 16"><path d="M13 4.5V1.8l-1.7 1.7A5.6 5.6 0 1 0 13.6 8h-1.7a3.9 3.9 0 1 1-1.4-3l-2 2.1H13Z"/></svg>',
    split: '<svg viewBox="0 0 16 16"><path d="M2 3h12v10H2zM8 3v10" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>',
    file: '<svg viewBox="0 0 16 16"><path d="M4 1.8h5l3 3V14H4z" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M9 1.8v3h3"/></svg>',
    folder: '<svg viewBox="0 0 16 16"><path d="M1.8 4.2h4l1.2-1.5h7.2V13H1.8z" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    save: '<svg viewBox="0 0 16 16"><path d="M3 2h10v12H3z" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M5 2h5v3H5zm1 7h4v3H6z"/></svg>',
    terminal: '<svg viewBox="0 0 16 16"><path d="M2 3h12v10H2z" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="m4 6 2 2-2 2M7.8 10H12"/></svg>',
    plus: '<svg viewBox="0 0 16 16"><path d="M7 3h2v4h4v2H9v4H7V9H3V7h4z"/></svg>',
    trash: '<svg viewBox="0 0 16 16"><path d="M3 4h10M6 4V2.5h4V4m-5 1v8m3-8v8m3-8v8M4.5 4.5h7l-.6 9h-5.8z" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    edit: '<svg viewBox="0 0 16 16"><path d="m11.9 2.4 1.7 1.7-7.7 7.7-2.6.9.9-2.6zM10.8 3.5l1.7 1.7" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>',
    chevronRight: '<svg viewBox="0 0 16 16"><path d="m6 3 5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    chevronDown: '<svg viewBox="0 0 16 16"><path d="m3 6 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
  };

  const dom = {};
  const docs = new Map();
  const docsByPath = new Map();
  const editorInstances = {};
  const modelListeners = new Map();
  const state = {
    projectRoot: null,
    luauPath: DEFAULT_LUAU_EXE,
    shellType: "PowerShell",
    shellOptions: [],
    zoom: 14,
    sidebarVisible: true,
    panelsVisible: true,
    outlineVisible: true,
    splitVisible: false,
    recentFiles: [],
    expandedDirs: new Set(),
    selectedExplorerPath: null,
    dirCache: new Map(),
    layout: {
      sidebarWidth: 300,
      panelsHeight: 260,
      splitWidth: "42%",
      outlineWidth: 230,
      terminalWidth: "1fr"
    },
    groups: {
      main: { tabs: [], activeId: null },
      split: { tabs: [], activeId: null }
    },
    activeGroup: "main",
    untitledCounter: 1,
    palette: { items: [], index: 0, onSelect: null },
    contextMenu: null,
    monaco: null,
    terminal: null,
    fitAddon: null
  };

  const toolbarButtons = [
    { id: "menu", label: "Menu", icon: "menu", action: () => openMainMenu(), variant: "" },
    { id: "explorer", label: "Explorer", icon: "explorer", action: () => toggleSidebar(), variant: "" },
    { id: "panels", label: "Panels", icon: "panels", action: () => togglePanels(), variant: "" },
    { id: "outline", label: "Outline", icon: "outline", action: () => toggleOutline(), variant: "" },
    { id: "new", label: "New", icon: "newTab", action: () => createUntitledDoc(), variant: "" },
    { id: "run", label: "Run", icon: "run", action: () => runActiveDoc(), variant: "run" },
    { id: "stop", label: "Restart", icon: "stop", action: () => restartShell(), variant: "stop" },
    { id: "find", label: "Find", icon: "find", action: () => showFindPrompt(), variant: "" },
    { id: "refresh", label: "Refresh", icon: "refresh", action: () => refreshExplorer(), variant: "" }
  ];

  function byId(id) {
    return document.getElementById(id);
  }

  function setStatus(text) {
    dom.statusText.textContent = text;
  }

  function scheduleStateSave() {
    clearTimeout(scheduleStateSave.timer);
    scheduleStateSave.timer = setTimeout(() => {
      const payload = {
        projectRoot: state.projectRoot,
        luauPath: state.luauPath,
        shellType: state.shellType,
        zoom: state.zoom,
        sidebarVisible: state.sidebarVisible,
        panelsVisible: state.panelsVisible,
        outlineVisible: state.outlineVisible,
        splitVisible: state.splitVisible,
        recentFiles: state.recentFiles.slice(0, 40),
        expandedDirs: Array.from(state.expandedDirs),
        selectedExplorerPath: state.selectedExplorerPath,
        layout: state.layout,
        openTabs: [
          ...state.groups.main.tabs
            .map((id) => docs.get(id))
            .filter(Boolean)
            .filter((doc) => doc.path)
            .map((doc) => ({ path: doc.path, group: "main" })),
          ...state.groups.split.tabs
            .map((id) => docs.get(id))
            .filter(Boolean)
            .filter((doc) => doc.path)
            .map((doc) => ({ path: doc.path, group: "split" }))
        ],
        activeTabs: {
          main: docById(state.groups.main.activeId)?.path || null,
          split: docById(state.groups.split.activeId)?.path || null
        }
      };
      window.desktopAPI.saveState(payload);
    }, 200);
  }

  function docById(id) {
    return docs.get(id) || null;
  }

  function activeGroupState() {
    return state.groups[state.activeGroup];
  }

  function activeDoc() {
    return docById(activeGroupState().activeId);
  }

  function isDocOpenAnywhere(docId) {
    return state.groups.main.tabs.includes(docId) || state.groups.split.tabs.includes(docId);
  }

  function detectLanguage(filePath) {
    const ext = pathUtils.extname(filePath || "");
    return ext === ".luau" || ext === ".lua" ? "luau" : ext === ".json" ? "json" : "plaintext";
  }

  function updateCssVariables() {
    document.documentElement.style.setProperty("--sidebar-width", `${state.layout.sidebarWidth}px`);
    document.documentElement.style.setProperty("--panels-height", `${state.layout.panelsHeight}px`);
    document.documentElement.style.setProperty("--split-width", state.layout.splitWidth);
    document.documentElement.style.setProperty("--outline-width", `${state.layout.outlineWidth}px`);
    document.documentElement.style.setProperty("--terminal-width", state.layout.terminalWidth);
    document.documentElement.style.setProperty("--editor-font-size", `${state.zoom}px`);
  }

  function updateLayoutClasses() {
    dom.workspace.classList.toggle("sidebar-hidden", !state.sidebarVisible);
    dom.mainColumn.classList.toggle("panels-hidden", !state.panelsVisible);
    dom.panelsShell.classList.toggle("hidden", !state.panelsVisible);
    dom.panelsSplitter.classList.toggle("hidden", !state.panelsVisible);
    dom.editorLayout.classList.toggle("split-hidden", !state.splitVisible);
    dom.editorLayout.classList.toggle("outline-hidden", !state.outlineVisible);
    dom.outlinePanel.classList.toggle("hidden", !state.outlineVisible);
    dom.editorSplitter.classList.toggle("hidden", !state.splitVisible);
    dom.splitGroup.classList.toggle("hidden", !state.splitVisible);
  }

  function fileIconForPath(filePath, isDirectory = false) {
    if (isDirectory) {
      return `<span class="file-icon" style="color:#ffb454">${icons.folder}</span>`;
    }
    const ext = pathUtils.extname(filePath);
    const colors = {
      ".luau": "#54a6ff",
      ".lua": "#6ec1ff",
      ".md": "#ff9f68",
      ".txt": "#c3b3ff",
      ".toml": "#ffd166",
      ".json": "#7ee787",
      ".exe": "#ff6b82",
      ".html": "#ff8a65",
      ".css": "#4dd0e1",
      ".js": "#ffd54f",
      ".ts": "#64b5f6",
      ".py": "#55d39b"
    };
    return `<span class="file-icon" style="color:${colors[ext] || "#b6c5dd"}">${icons.file}</span>`;
  }

  function promptText(message, value = "") {
    return window.prompt(message, value);
  }

  function confirmAction(message) {
    return window.confirm(message);
  }

  async function loadDirectory(dirPath) {
    const entries = await window.desktopAPI.readDir(dirPath);
    state.dirCache.set(dirPath, entries);
    return entries;
  }

  async function ensureDirectoryLoaded(dirPath) {
    if (!state.dirCache.has(dirPath)) {
      await loadDirectory(dirPath);
    }
    return state.dirCache.get(dirPath) || [];
  }

  function renderToolbar() {
    dom.toolbar.innerHTML = "";
    const left = document.createElement("div");
    left.className = "toolbar-group";
    toolbarButtons.forEach((button) => {
      const element = document.createElement("button");
      element.className = "toolbar-button";
      element.dataset.variant = button.variant;
      element.innerHTML = `${icons[button.icon]}<span class="label">${button.label}</span>`;
      element.addEventListener("click", button.action);
      left.appendChild(element);
    });
    const spacer = document.createElement("div");
    spacer.className = "toolbar-spacer";
    const right = document.createElement("div");
    right.className = "toolbar-group";
    right.innerHTML = `<button class="ghost-button" id="quick-open-button">${icons.find}<span>Quick Open</span></button>`;
    dom.toolbar.append(left, spacer, right);
    byId("quick-open-button").addEventListener("click", showQuickOpen);
  }

  function registerLuauLanguage(monaco) {
    monaco.languages.register({ id: "luau" });
    monaco.languages.setMonarchTokensProvider("luau", {
      tokenizer: {
        root: [
          [/--\[\[[\s\S]*?\]\]/, "comment"],
          [/--.*$/, "comment"],
          [/"([^"\\]|\\.)*$/, "string.invalid"],
          [/"([^"\\]|\\.)*"/, "string"],
          [/'([^'\\]|\\.)*$/, "string.invalid"],
          [/'([^'\\]|\\.)*'/, "string"],
          [/\b\d+(\.\d+)?\b/, "number"],
          [new RegExp(`\\b(?:${KEYWORDS.join("|")})\\b`), "keyword"],
          [new RegExp(`\\b(?:${BUILTINS.join("|")})\\b`), "type.identifier"],
          [/[a-zA-Z_][\w]*/, "identifier"]
        ]
      }
    });
    monaco.languages.setLanguageConfiguration("luau", {
      comments: { lineComment: "--", blockComment: ["--[[", "]]"] },
      autoClosingPairs: [
        { open: "{", close: "}" },
        { open: "[", close: "]" },
        { open: "(", close: ")" },
        { open: '"', close: '"' },
        { open: "'", close: "'" }
      ]
    });
  }

  function createDoc({ path = null, content = "" }) {
    const id = `doc-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
    const name = path ? pathUtils.basename(path) : `untitled-${state.untitledCounter++}.luau`;
    const uri = path
      ? state.monaco.Uri.parse(`file:///${path.replace(/\\/g, "/")}`)
      : state.monaco.Uri.parse(`inmemory:///${name}`);
    const model = state.monaco.editor.createModel(content, detectLanguage(path), uri);
    const doc = { id, path, name, model, dirty: false, lastSavedValue: content };
    docs.set(id, doc);
    if (path) {
      docsByPath.set(path.toLowerCase(), id);
    }
    const disposable = model.onDidChangeContent(() => {
      const current = model.getValue();
      doc.dirty = current !== doc.lastSavedValue;
      renderTabs();
      refreshTitle();
      refreshOutline();
      scheduleStateSave();
    });
    modelListeners.set(id, disposable);
    return doc;
  }

  function touchRecentFile(filePath) {
    if (!filePath) {
      return;
    }
    const normalized = pathUtils.normalize(filePath);
    state.recentFiles = [normalized, ...state.recentFiles.filter((item) => item !== normalized)].slice(0, 40);
  }

  async function openPath(filePath, groupName = state.activeGroup, force = false) {
    const normalized = pathUtils.normalize(filePath);
    if (!force) {
      const existingId = docsByPath.get(normalized.toLowerCase());
      if (existingId) {
        openDocInGroup(docById(existingId), groupName);
        return docById(existingId);
      }
    }
    let content = "";
    try {
      content = await window.desktopAPI.readFile(normalized);
    } catch (error) {
      setStatus(`Open failed: ${error.message}`);
      return null;
    }
    const doc = createDoc({ path: normalized, content });
    doc.dirty = false;
    doc.lastSavedValue = content;
    openDocInGroup(doc, groupName);
    touchRecentFile(normalized);
    setStatus(`Opened ${doc.name}`);
    return doc;
  }

  function openDocInGroup(doc, groupName = state.activeGroup) {
    if (!doc) {
      return;
    }
    const group = state.groups[groupName];
    if (!group.tabs.includes(doc.id)) {
      group.tabs.push(doc.id);
    }
    group.activeId = doc.id;
    state.activeGroup = groupName;
    if (groupName === "split") {
      state.splitVisible = true;
    }
    applyModelToEditor(groupName);
    renderTabs();
    refreshTitle();
    refreshOutline();
    updateLayoutClasses();
    scheduleStateSave();
  }

  function applyModelToEditor(groupName) {
    const group = state.groups[groupName];
    const editor = editorInstances[groupName];
    if (!editor) {
      return;
    }
    const doc = docById(group.activeId);
    editor.setModel(doc ? doc.model : null);
    if (doc) {
      editor.focus();
      updateCursorLabel(editor);
    }
  }

  function renderTabs() {
    renderGroupTabs("main", dom.tabbarMain);
    renderGroupTabs("split", dom.tabbarSplit);
  }

  function renderGroupTabs(groupName, container) {
    const group = state.groups[groupName];
    container.innerHTML = "";
    group.tabs.forEach((docId) => {
      const doc = docById(docId);
      if (!doc) {
        return;
      }
      const tab = document.createElement("div");
      tab.className = `tab ${group.activeId === doc.id ? "active" : ""} ${doc.dirty ? "dirty" : ""}`;
      tab.innerHTML = `
        ${fileIconForPath(doc.path || doc.name)}
        <span class="tab-name">${doc.name}</span>
        <button class="tab-close">x</button>
      `;
      tab.addEventListener("click", () => {
        state.activeGroup = groupName;
        openDocInGroup(doc, groupName);
      });
      tab.addEventListener("contextmenu", (event) => {
        event.preventDefault();
        state.activeGroup = groupName;
        showTabContextMenu(event.clientX, event.clientY, doc, groupName);
      });
      tab.querySelector(".tab-close").addEventListener("click", async (event) => {
        event.stopPropagation();
        await closeDocInGroup(groupName, doc.id);
      });
      container.appendChild(tab);
    });
  }

  async function saveDoc(doc, saveAs = false) {
    if (!doc) {
      return false;
    }
    let targetPath = doc.path;
    if (saveAs || !targetPath) {
      targetPath = await window.desktopAPI.saveFileDialog({ defaultPath: doc.path || pathUtils.join(state.projectRoot || "", doc.name) });
      if (!targetPath) {
        return false;
      }
    }
    await window.desktopAPI.writeFile({ path: targetPath, content: doc.model.getValue() });
    if (doc.path && doc.path.toLowerCase() !== targetPath.toLowerCase()) {
      docsByPath.delete(doc.path.toLowerCase());
    }
    doc.path = targetPath;
    doc.name = pathUtils.basename(targetPath);
    doc.lastSavedValue = doc.model.getValue();
    doc.dirty = false;
    docsByPath.set(targetPath.toLowerCase(), doc.id);
    touchRecentFile(targetPath);
    state.monaco.editor.setModelLanguage(doc.model, detectLanguage(targetPath));
    renderTabs();
    refreshTitle();
    refreshExplorer();
    scheduleStateSave();
    setStatus(`Saved ${doc.name}`);
    return true;
  }

  async function saveAllDocs() {
    for (const doc of docs.values()) {
      if (doc.dirty || !doc.path) {
        const ok = await saveDoc(doc);
        if (!ok) {
          return false;
        }
      }
    }
    setStatus("All files saved");
    return true;
  }

  async function closeDocInGroup(groupName, docId) {
    const group = state.groups[groupName];
    const doc = docById(docId);
    if (!doc) {
      return true;
    }
    const openElsewhere = groupName === "main" ? state.groups.split.tabs.includes(docId) : state.groups.main.tabs.includes(docId);
    if (!openElsewhere) {
      if (doc.dirty && doc.path) {
        const saved = await saveDoc(doc);
        if (!saved) {
          return false;
        }
      } else if (doc.dirty && !doc.path) {
        const answer = confirmAction(`${doc.name} has unsaved changes. Save before closing?`);
        if (answer) {
          const saved = await saveDoc(doc);
          if (!saved) {
            return false;
          }
        }
      }
    }
    group.tabs = group.tabs.filter((id) => id !== docId);
    if (group.activeId === docId) {
      group.activeId = group.tabs[group.tabs.length - 1] || null;
    }
    if (!isDocOpenAnywhere(docId)) {
      docs.delete(docId);
      if (doc.path) {
        docsByPath.delete(doc.path.toLowerCase());
      }
      modelListeners.get(docId)?.dispose();
      modelListeners.delete(docId);
      doc.model.dispose();
    }
    if (groupName === "split" && group.tabs.length === 0) {
      state.splitVisible = false;
    }
    if (!state.groups.main.tabs.length && !state.groups.split.tabs.length) {
      createUntitledDoc();
    }
    applyModelToEditor(groupName);
    if (groupName === "split" && !state.splitVisible) {
      applyModelToEditor("main");
    }
    updateLayoutClasses();
    renderTabs();
    refreshTitle();
    refreshOutline();
    scheduleStateSave();
    return true;
  }

  async function closeOtherTabs(targetDoc = activeDoc()) {
    if (!targetDoc) {
      return;
    }
    const ids = Array.from(docs.keys());
    for (const docId of ids) {
      if (docId === targetDoc.id) {
        continue;
      }
      if (state.groups.main.tabs.includes(docId)) {
        await closeDocInGroup("main", docId);
      }
      if (state.groups.split.tabs.includes(docId)) {
        await closeDocInGroup("split", docId);
      }
    }
    openDocInGroup(targetDoc, state.groups.main.tabs.includes(targetDoc.id) ? "main" : "split");
    setStatus("Closed other tabs");
  }

  async function closeAllTabs() {
    for (const docId of [...state.groups.main.tabs]) {
      await closeDocInGroup("main", docId);
    }
    for (const docId of [...state.groups.split.tabs]) {
      await closeDocInGroup("split", docId);
    }
    setStatus("Closed all tabs");
  }

  function createUntitledDoc() {
    const doc = createDoc({ content: "-- Luau Electron IDE\n\nprint(\"Hello, Roblox\")\n" });
    openDocInGroup(doc, "main");
    return doc;
  }

  function refreshTitle() {
    dom.titleProject.textContent = state.projectRoot || "No folder open";
    dom.folderLabel.textContent = state.projectRoot || "No folder open";
    const doc = activeDoc();
    dom.breadcrumb.textContent = doc?.path ? pathUtils.dirname(doc.path) : state.projectRoot || "No folder open";
    document.title = doc ? `${doc.dirty ? "* " : ""}${doc.name} - Luau Electron IDE` : "Luau Electron IDE";
  }

  function updateCursorLabel(editor) {
    const position = editor?.getPosition();
    if (!position) {
      dom.cursorText.textContent = "Ln 1, Col 1";
      return;
    }
    dom.cursorText.textContent = `Ln ${position.lineNumber}, Col ${position.column}`;
  }

  function refreshOutline() {
    const doc = activeDoc();
    dom.outlineList.innerHTML = "";
    if (!doc) {
      dom.outlineCount.textContent = "0 symbols";
      dom.diagnostics.textContent = "Diagnostics ready";
      return;
    }
    const text = doc.model.getValue();
    const items = [];
    const patterns = [
      /^\s*local\s+function\s+([A-Za-z_][\w]*)/m,
      /^\s*function\s+([A-Za-z_][\w.:]*)/m,
      /^\s*local\s+([A-Za-z_][\w]*)\s*=\s*function/m
    ];
    text.split(/\r?\n/).forEach((line, index) => {
      for (const pattern of patterns) {
        const match = line.match(pattern);
        if (match) {
          items.push({ name: match[1], line: index + 1 });
          break;
        }
      }
    });
    items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "outline-item";
      row.innerHTML = `<div>${item.name}</div><div class="line">:${item.line}</div>`;
      row.addEventListener("click", () => {
        editorInstances[state.activeGroup].revealLineInCenter(item.line);
        editorInstances[state.activeGroup].setPosition({ lineNumber: item.line, column: 1 });
        editorInstances[state.activeGroup].focus();
      });
      dom.outlineList.appendChild(row);
    });
    dom.outlineCount.textContent = `${items.length} symbols`;
    const diagnostics = computeDiagnostics(text);
    dom.diagnostics.textContent = diagnostics;
    dom.diagnostics.style.color = diagnostics.startsWith("Syntax hints:") ? "#ffb454" : "";
  }

  function computeDiagnostics(text) {
    const lines = text.split(/\r?\n/);
    let balance = 0;
    for (const line of lines) {
      const trimmed = line.trim();
      if (/^(function|if|for|while|repeat)\b/.test(trimmed) || /\bthen$/.test(trimmed) || /\bdo$/.test(trimmed)) {
        balance += 1;
      }
      if (/^end\b/.test(trimmed) || /^until\b/.test(trimmed)) {
        balance -= 1;
      }
    }
    if (balance > 0) {
      return "Syntax hints: possible missing `end`";
    }
    if ((text.match(/"/g) || []).length % 2 === 1) {
      return "Syntax hints: possible unclosed string";
    }
    return "Diagnostics ready";
  }

  async function refreshExplorer() {
    if (!state.projectRoot) {
      dom.explorerTree.innerHTML = "";
      return;
    }
    await ensureDirectoryLoaded(state.projectRoot);
    dom.explorerTree.innerHTML = "";
    const root = buildTreeNode({ path: state.projectRoot, name: pathUtils.basename(state.projectRoot), kind: "directory" }, 0);
    dom.explorerTree.appendChild(root);
    scheduleStateSave();
  }

  function buildTreeNode(entry, depth) {
    const wrapper = document.createElement("div");
    const row = document.createElement("div");
    row.className = `tree-row ${state.selectedExplorerPath === entry.path ? "selected" : ""}`;
    row.style.paddingLeft = `${8 + depth * 12}px`;
    const expanded = state.expandedDirs.has(entry.path);
    row.innerHTML = `
      <span class="tree-chevron">${entry.kind === "directory" ? (expanded ? icons.chevronDown : icons.chevronRight) : ""}</span>
      ${fileIconForPath(entry.path, entry.kind === "directory")}
      <span class="file-name">${entry.name}</span>
    `;
    row.addEventListener("click", async () => {
      state.selectedExplorerPath = entry.path;
      if (entry.kind === "directory") {
        if (state.expandedDirs.has(entry.path)) {
          state.expandedDirs.delete(entry.path);
        } else {
          state.expandedDirs.add(entry.path);
          await ensureDirectoryLoaded(entry.path);
        }
        await refreshExplorer();
      } else {
        await openPath(entry.path);
        await revealInExplorer(entry.path);
      }
    });
    row.addEventListener("contextmenu", async (event) => {
      event.preventDefault();
      state.selectedExplorerPath = entry.path;
      await showExplorerContextMenu(event.clientX, event.clientY, entry);
    });
    wrapper.appendChild(row);
    if (entry.kind === "directory" && state.expandedDirs.has(entry.path)) {
      const childrenWrap = document.createElement("div");
      childrenWrap.className = "tree-children";
      const children = state.dirCache.get(entry.path) || [];
      children.forEach((child) => childrenWrap.appendChild(buildTreeNode(child, depth + 1)));
      wrapper.appendChild(childrenWrap);
    }
    return wrapper;
  }

  async function revealInExplorer(filePath) {
    if (!state.projectRoot) {
      return;
    }
    const parts = pathUtils.relative(state.projectRoot, filePath).split("\\");
    let current = state.projectRoot;
    state.expandedDirs.add(state.projectRoot);
    for (let index = 0; index < parts.length - 1; index += 1) {
      current = pathUtils.join(current, parts[index]);
      state.expandedDirs.add(current);
      await ensureDirectoryLoaded(current);
    }
    state.selectedExplorerPath = filePath;
    await refreshExplorer();
  }

  async function openFolder() {
    const selected = await window.desktopAPI.openFolderDialog(state.projectRoot);
    if (!selected) {
      return;
    }
    state.projectRoot = pathUtils.normalize(selected);
    state.dirCache.clear();
    state.expandedDirs = new Set([state.projectRoot]);
    state.selectedExplorerPath = state.projectRoot;
    dom.panelCwd.textContent = state.projectRoot;
    refreshTitle();
    await refreshExplorer();
    await restartShell();
    scheduleStateSave();
    setStatus(`Project ready: ${pathUtils.basename(state.projectRoot)}`);
  }

  async function openFileDialog() {
    const selected = await window.desktopAPI.openFileDialog(state.projectRoot || undefined);
    if (!selected) {
      return;
    }
    if (!state.projectRoot) {
      state.projectRoot = pathUtils.dirname(selected);
      state.expandedDirs = new Set([state.projectRoot]);
      dom.panelCwd.textContent = state.projectRoot;
    }
    await openPath(selected);
    await revealInExplorer(selected);
    scheduleStateSave();
  }

  async function renameSelectedPath() {
    if (!state.selectedExplorerPath) {
      return;
    }
    const current = pathUtils.basename(state.selectedExplorerPath);
    const nextName = promptText("Rename to:", current);
    if (!nextName || nextName === current) {
      return;
    }
    const target = pathUtils.join(pathUtils.dirname(state.selectedExplorerPath), nextName);
    await window.desktopAPI.renamePath({ from: state.selectedExplorerPath, to: target });
    if (docsByPath.has(state.selectedExplorerPath.toLowerCase())) {
      const doc = docById(docsByPath.get(state.selectedExplorerPath.toLowerCase()));
      docsByPath.delete(state.selectedExplorerPath.toLowerCase());
      doc.path = target;
      doc.name = nextName;
      docsByPath.set(target.toLowerCase(), doc.id);
    }
    state.selectedExplorerPath = target;
    state.dirCache.clear();
    await refreshExplorer();
    renderTabs();
    refreshTitle();
  }

  async function deleteSelectedPath() {
    if (!state.selectedExplorerPath) {
      return;
    }
    if (!confirmAction(`Delete ${pathUtils.basename(state.selectedExplorerPath)}?`)) {
      return;
    }
    await window.desktopAPI.deletePath(state.selectedExplorerPath);
    state.dirCache.clear();
    await refreshExplorer();
  }

  async function createFileInExplorer() {
    const base = state.selectedExplorerPath || state.projectRoot;
    const directory = (state.dirCache.has(base) || base === state.projectRoot) && !pathUtils.extname(base) ? base : pathUtils.dirname(base);
    const name = promptText("File name:", "new_file.luau");
    if (!name) {
      return;
    }
    const fullPath = pathUtils.join(directory, name);
    await window.desktopAPI.writeFile({ path: fullPath, content: "" });
    state.dirCache.clear();
    await refreshExplorer();
    await openPath(fullPath);
    await revealInExplorer(fullPath);
  }

  async function createFolderInExplorer() {
    const base = state.selectedExplorerPath || state.projectRoot;
    const directory = (state.dirCache.has(base) || base === state.projectRoot) && !pathUtils.extname(base) ? base : pathUtils.dirname(base);
    const name = promptText("Folder name:", "new_folder");
    if (!name) {
      return;
    }
    const fullPath = pathUtils.join(directory, name);
    await window.desktopAPI.mkdir(fullPath);
    state.dirCache.clear();
    await refreshExplorer();
    state.selectedExplorerPath = fullPath;
  }

  async function openSelectedInTerminal() {
    if (!state.selectedExplorerPath) {
      return;
    }
    ensurePanelsVisible();
    const target = pathUtils.extname(state.selectedExplorerPath) ? pathUtils.dirname(state.selectedExplorerPath) : state.selectedExplorerPath;
    const command =
      state.shellType === "Git Bash"
        ? `cd "${pathUtils.bash(target)}"\r`
        : state.shellType === "Command Prompt"
          ? `cd /d "${target}"\r`
          : `Set-Location "${target}"\r`;
    await window.desktopAPI.writeShell(command);
    setStatus(`Opened in terminal: ${target}`);
  }

  function showContextMenu(items, x, y) {
    dom.contextMenu.innerHTML = "";
    items.forEach((item) => {
      if (item.separator) {
        const separator = document.createElement("div");
        separator.className = "context-separator";
        dom.contextMenu.appendChild(separator);
        return;
      }
      const row = document.createElement("div");
      row.className = "context-item";
      row.textContent = item.label;
      row.addEventListener("click", async () => {
        hideContextMenu();
        await item.action();
      });
      dom.contextMenu.appendChild(row);
    });
    dom.contextMenu.style.left = `${x}px`;
    dom.contextMenu.style.top = `${y}px`;
    dom.contextMenu.classList.remove("hidden");
  }

  function hideContextMenu() {
    dom.contextMenu.classList.add("hidden");
  }

  function showTabContextMenu(x, y, doc, groupName) {
    showContextMenu(
      [
        { label: "Close", action: () => closeDocInGroup(groupName, doc.id) },
        { label: "Close Others", action: () => closeOtherTabs(doc) },
        { label: "Close All", action: () => closeAllTabs() },
        { separator: true },
        { label: "Split Right", action: () => splitDocument(doc) },
        { label: "Reveal In Explorer", action: () => revealInExplorer(doc.path) }
      ],
      x,
      y
    );
  }

  async function showExplorerContextMenu(x, y, entry) {
    showContextMenu(
      [
        { label: "New File", action: () => createFileInExplorer() },
        { label: "New Folder", action: () => createFolderInExplorer() },
        { label: "Rename", action: () => renameSelectedPath() },
        { label: "Delete", action: () => deleteSelectedPath() },
        { separator: true },
        { label: "Copy Path", action: () => window.desktopAPI.copyText(entry.path) },
        { label: "Copy Relative Path", action: () => window.desktopAPI.copyText(pathUtils.relative(state.projectRoot, entry.path)) },
        { label: "Open In Terminal", action: () => openSelectedInTerminal() }
      ],
      x,
      y
    );
  }

  function showPalette(items, placeholder, onSelect) {
    state.palette.items = items;
    state.palette.index = 0;
    state.palette.onSelect = onSelect;
    dom.paletteInput.value = "";
    dom.paletteInput.placeholder = placeholder;
    renderPaletteItems(items);
    dom.paletteOverlay.classList.remove("hidden");
    dom.paletteInput.focus();
  }

  function hidePalette() {
    dom.paletteOverlay.classList.add("hidden");
  }

  function renderPaletteItems(items) {
    dom.paletteList.innerHTML = "";
    items.forEach((item, index) => {
      const row = document.createElement("div");
      row.className = `palette-item ${index === state.palette.index ? "active" : ""}`;
      row.innerHTML = `<span>${item.label}</span><span class="panel-subtitle">${item.meta || ""}</span>`;
      row.addEventListener("click", () => {
        state.palette.onSelect(item);
        hidePalette();
      });
      dom.paletteList.appendChild(row);
    });
  }

  function filterPalette() {
    const query = dom.paletteInput.value.trim().toLowerCase();
    const filtered = state.palette.items.filter((item) => item.label.toLowerCase().includes(query));
    state.palette.filtered = filtered;
    state.palette.index = 0;
    renderPaletteItems(filtered);
  }

  function showCommandPalette() {
    const commands = [
      { label: "Open Folder", action: openFolder },
      { label: "Open File", action: openFileDialog },
      { label: "New Tab", action: () => createUntitledDoc() },
      { label: "Save", action: () => saveDoc(activeDoc()) },
      { label: "Save As", action: () => saveDoc(activeDoc(), true) },
      { label: "Save All", action: saveAllDocs },
      { label: "Quick Open", action: showQuickOpen },
      { label: "Run Active Tab", action: runActiveDoc },
      { label: "Split Active Tab", action: () => splitDocument(activeDoc()) },
      { label: "Close Other Tabs", action: () => closeOtherTabs(activeDoc()) },
      { label: "Toggle Explorer", action: toggleSidebar },
      { label: "Toggle Panels", action: togglePanels },
      { label: "Toggle Outline", action: toggleOutline },
      { label: "Set luau.exe Path", action: chooseLuauPath },
      { label: "Restart Terminal", action: restartShell }
    ];
    showPalette(commands, "Command Palette", (item) => item.action());
  }

  async function collectProjectFiles(dirPath, acc = []) {
    const entries = await ensureDirectoryLoaded(dirPath);
    for (const entry of entries) {
      if (entry.kind === "directory") {
        await collectProjectFiles(entry.path, acc);
      } else {
        acc.push(entry.path);
      }
    }
    return acc;
  }

  async function showQuickOpen() {
    if (!state.projectRoot) {
      return;
    }
    const files = await collectProjectFiles(state.projectRoot);
    showPalette(
      files.map((filePath) => ({ label: pathUtils.relative(state.projectRoot, filePath), meta: pathUtils.basename(filePath), path: filePath })),
      "Quick Open",
      (item) => openPath(item.path)
    );
  }

  function toggleSidebar() {
    state.sidebarVisible = !state.sidebarVisible;
    updateLayoutClasses();
    scheduleStateSave();
  }

  function ensurePanelsVisible() {
    if (!state.panelsVisible) {
      state.panelsVisible = true;
      updateLayoutClasses();
      fitTerminal();
      scheduleStateSave();
    }
  }

  function togglePanels() {
    state.panelsVisible = !state.panelsVisible;
    updateLayoutClasses();
    fitTerminal();
    scheduleStateSave();
  }

  function toggleOutline() {
    state.outlineVisible = !state.outlineVisible;
    updateLayoutClasses();
    scheduleStateSave();
  }

  function splitDocument(doc) {
    if (!doc) {
      return;
    }
    state.splitVisible = true;
    openDocInGroup(doc, "split");
    updateLayoutClasses();
    fitTerminal();
    scheduleStateSave();
  }

  function showFindPrompt() {
    const doc = activeDoc();
    if (!doc) {
      return;
    }
    const term = promptText("Find text:");
    if (!term) {
      return;
    }
    const editor = editorInstances[state.activeGroup];
    const matches = doc.model.findMatches(term, true, false, false, null, true);
    if (!matches.length) {
      setStatus(`No matches for "${term}"`);
      return;
    }
    editor.setSelection(matches[0].range);
    editor.revealRangeInCenter(matches[0].range);
    editor.focus();
    setStatus(`Found ${matches.length} matches for "${term}"`);
  }

  async function chooseLuauPath() {
    const selected = await window.desktopAPI.chooseLuauPathDialog(state.luauPath);
    if (!selected) {
      return;
    }
    state.luauPath = pathUtils.normalize(selected);
    setStatus(`luau.exe set: ${pathUtils.basename(selected)}`);
    scheduleStateSave();
  }

  function writeRunOutput(text, clear = false) {
    if (clear) {
      dom.runOutput.textContent = "";
    }
    dom.runOutput.textContent += text;
    dom.runOutput.scrollTop = dom.runOutput.scrollHeight;
  }

  async function runActiveDoc() {
    const doc = activeDoc();
    if (!doc) {
      return;
    }
    ensurePanelsVisible();
    if (doc.path) {
      const saved = await saveDoc(doc);
      if (!saved) {
        return;
      }
    }
    dom.runStatus.textContent = "Running";
    writeRunOutput(`> Running ${doc.name} from ${doc.path ? pathUtils.dirname(doc.path) : (state.projectRoot || "temp")}\n`, true);
    const result = await window.desktopAPI.runLuau({
      luauPath: state.luauPath,
      filePath: doc.path,
      content: doc.model.getValue(),
      projectRoot: state.projectRoot
    });
    if (result.stdout) {
      writeRunOutput(result.stdout.endsWith("\n") ? result.stdout : `${result.stdout}\n`);
    }
    if (result.stderr) {
      writeRunOutput(result.stderr.endsWith("\n") ? result.stderr : `${result.stderr}\n`);
    }
    if (!result.stdout && !result.stderr) {
      writeRunOutput("(no output)\n");
    }
    dom.runStatus.textContent = result.code === 0 ? "Done" : "Finished";
    setStatus(`Run completed: ${doc.name}`);
  }

  async function restartShell() {
    const payload = await window.desktopAPI.restartShell({
      type: state.shellType,
      cwd: state.projectRoot || "C:\\"
    });
    state.shellOptions = payload.options;
    dom.shellSelect.innerHTML = payload.options.map((label) => `<option value="${label}">${label}</option>`).join("");
    dom.shellSelect.value = payload.shellType;
    dom.panelCwd.textContent = payload.cwd;
    fitTerminal();
  }

  function fitTerminal() {
    setTimeout(() => state.fitAddon?.fit(), 30);
  }

  function initTerminal() {
    state.terminal = new window.Terminal({
      fontFamily: "Cascadia Code",
      fontSize: 13,
      convertEol: true,
      cursorBlink: true,
      theme: {
        background: "#0b1019",
        foreground: "#dce7f8",
        cursor: "#7dc6ff",
        black: "#1f2430",
        red: "#ff7b92",
        green: "#8be9b3",
        yellow: "#ffd166",
        blue: "#6cb6ff",
        magenta: "#c792ea",
        cyan: "#7fdbff",
        white: "#dce7f8"
      }
    });
    state.fitAddon = new window.FitAddon.FitAddon();
    state.terminal.loadAddon(state.fitAddon);
    state.terminal.open(dom.terminal);
    state.terminal.onData((data) => {
      window.desktopAPI.writeShell(data);
    });
    window.desktopAPI.onShellData((payload) => {
      state.terminal.write(payload.data);
    });
    window.desktopAPI.onShellStarted((payload) => {
      state.shellType = payload.shellType;
      state.shellOptions = payload.options;
      dom.shellSelect.innerHTML = payload.options.map((label) => `<option value="${label}">${label}</option>`).join("");
      dom.shellSelect.value = payload.shellType;
      dom.panelCwd.textContent = payload.cwd;
      fitTerminal();
    });
    window.desktopAPI.onShellExit(() => {
      state.terminal.write("\r\n[terminal exited]\r\n");
    });
    window.desktopAPI.onShellError((payload) => {
      state.terminal.write(`\r\n[terminal error] ${payload.message}\r\n`);
    });
  }

  function openMainMenu() {
    showContextMenu(
      [
        { label: "Open Folder...", action: openFolder },
        { label: "Open File...", action: openFileDialog },
        { label: "New Tab", action: () => createUntitledDoc() },
        { separator: true },
        { label: "Save", action: () => saveDoc(activeDoc()) },
        { label: "Save As...", action: () => saveDoc(activeDoc(), true) },
        { label: "Save All", action: saveAllDocs },
        { separator: true },
        { label: "Split Active Tab", action: () => splitDocument(activeDoc()) },
        { label: "Set luau.exe Path...", action: chooseLuauPath }
      ],
      18,
      90
    );
  }

  function attachResizer(element, apply) {
    let active = false;
    element.addEventListener("mousedown", (event) => {
      active = true;
      event.preventDefault();
    });
    window.addEventListener("mousemove", (event) => {
      if (!active) {
        return;
      }
      apply(event);
      fitTerminal();
    });
    window.addEventListener("mouseup", () => {
      if (!active) {
        return;
      }
      active = false;
      scheduleStateSave();
    });
  }

  function wireResizers() {
    attachResizer(dom.sidebarSplitter, (event) => {
      state.layout.sidebarWidth = Math.max(180, Math.min(480, event.clientX));
      updateCssVariables();
    });
    attachResizer(dom.panelsSplitter, (event) => {
      state.layout.panelsHeight = Math.max(160, Math.min(window.innerHeight - 160, window.innerHeight - event.clientY - 26));
      updateCssVariables();
    });
    attachResizer(dom.editorSplitter, (event) => {
      const rect = dom.editorLayout.getBoundingClientRect();
      const rightWidth = Math.max(260, rect.right - event.clientX - state.layout.outlineWidth);
      state.layout.splitWidth = `${Math.min(rect.width - 260, rightWidth)}px`;
      updateCssVariables();
      Object.values(editorInstances).forEach((editor) => editor.layout());
    });
    attachResizer(dom.terminalOutputSplitter, (event) => {
      const rect = dom.panelsLayout.getBoundingClientRect();
      const width = Math.max(260, Math.min(rect.width - 260, event.clientX - rect.left));
      state.layout.terminalWidth = `${width}px`;
      updateCssVariables();
      fitTerminal();
    });
  }

  function registerShortcuts() {
    window.addEventListener("keydown", async (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        if (event.shiftKey) {
          await saveDoc(activeDoc(), true);
        } else {
          await saveDoc(activeDoc());
        }
      } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "o") {
        event.preventDefault();
        if (event.shiftKey) {
          await openFolder();
        } else {
          await openFileDialog();
        }
      } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "p" && event.shiftKey) {
        event.preventDefault();
        showCommandPalette();
      } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "p") {
        event.preventDefault();
        await showQuickOpen();
      } else if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "w") {
        event.preventDefault();
        const doc = activeDoc();
        if (doc) {
          await closeDocInGroup(state.activeGroup, doc.id);
        }
      } else if ((event.ctrlKey || event.metaKey) && (event.key === "+" || event.key === "=")) {
        event.preventDefault();
        state.zoom = Math.min(24, state.zoom + 1);
        applyZoom();
      } else if ((event.ctrlKey || event.metaKey) && event.key === "-") {
        event.preventDefault();
        state.zoom = Math.max(10, state.zoom - 1);
        applyZoom();
      } else if ((event.ctrlKey || event.metaKey) && event.key === "0") {
        event.preventDefault();
        state.zoom = 14;
        applyZoom();
      } else if (event.key === "F5" || ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "r")) {
        event.preventDefault();
        await runActiveDoc();
      }
    });
  }

  function applyZoom() {
    updateCssVariables();
    Object.values(editorInstances).forEach((editor) => editor.updateOptions({ fontSize: state.zoom }));
    setStatus(`Zoom: ${state.zoom}px`);
    scheduleStateSave();
  }

  async function bootstrapState() {
    const saved = await window.desktopAPI.loadState();
    state.projectRoot = saved.projectRoot || null;
    state.luauPath = saved.luauPath || DEFAULT_LUAU_EXE;
    state.shellType = saved.shellType || "PowerShell";
    state.zoom = saved.zoom || 14;
    state.sidebarVisible = saved.sidebarVisible !== false;
    state.panelsVisible = saved.panelsVisible !== false;
    state.outlineVisible = saved.outlineVisible !== false;
    state.splitVisible = saved.splitVisible === true;
    state.recentFiles = Array.isArray(saved.recentFiles) ? saved.recentFiles : [];
    state.expandedDirs = new Set(saved.expandedDirs || []);
    state.selectedExplorerPath = saved.selectedExplorerPath || null;
    state.layout = { ...state.layout, ...(saved.layout || {}) };
    updateCssVariables();
    updateLayoutClasses();
    dom.shellSelect.value = state.shellType;
    dom.panelCwd.textContent = state.projectRoot || "C:\\";
    refreshTitle();

    if (state.projectRoot) {
      state.expandedDirs.add(state.projectRoot);
      await refreshExplorer();
    }

    const openTabs = Array.isArray(saved.openTabs) ? saved.openTabs : [];
    for (const item of openTabs) {
      if (item?.path) {
        await openPath(item.path, item.group || "main");
      }
    }
    if (!docs.size) {
      createUntitledDoc();
    }
  }

  function initEditors(monaco) {
    state.monaco = monaco;
    registerLuauLanguage(monaco);
    editorInstances.main = monaco.editor.create(dom.editorMain, {
      language: "luau",
      automaticLayout: true,
      fontSize: state.zoom,
      minimap: { enabled: false },
      theme: "vs-dark",
      wordWrap: "off",
      smoothScrolling: true
    });
    editorInstances.split = monaco.editor.create(dom.editorSplit, {
      language: "luau",
      automaticLayout: true,
      fontSize: state.zoom,
      minimap: { enabled: false },
      theme: "vs-dark",
      wordWrap: "off",
      smoothScrolling: true
    });

    Object.entries(editorInstances).forEach(([groupName, editor]) => {
      editor.onDidFocusEditorText(() => {
        state.activeGroup = groupName;
        updateCursorLabel(editor);
        refreshOutline();
      });
      editor.onDidChangeCursorPosition(() => {
        if (state.activeGroup === groupName) {
          updateCursorLabel(editor);
        }
      });
    });
  }

  function loadMonaco() {
    return new Promise((resolve) => {
      const vsPath = new URL("../node_modules/monaco-editor/min/vs", window.location.href).href;
      const workerBase = `${vsPath}/`;
      window.MonacoEnvironment = {
        getWorkerUrl() {
          return `data:text/javascript;charset=utf-8,${encodeURIComponent(
            `self.MonacoEnvironment = { baseUrl: "${workerBase}" }; importScripts("${workerBase}base/worker/workerMain.js");`
          )}`;
        }
      };
      window.require.config({ paths: { vs: vsPath } });
      window.require(["vs/editor/editor.main"], () => resolve(window.monaco));
    });
  }

  function bindDom() {
    dom.toolbar = byId("toolbar");
    dom.titleProject = byId("title-project");
    dom.folderLabel = byId("folder-label");
    dom.breadcrumb = byId("breadcrumb");
    dom.diagnostics = byId("diagnostics");
    dom.workspace = byId("workspace");
    dom.mainColumn = byId("main-column");
    dom.explorerTree = byId("explorer-tree");
    dom.outlinePanel = byId("outline-panel");
    dom.outlineList = byId("outline-list");
    dom.outlineCount = byId("outline-count");
    dom.editorLayout = byId("editor-layout");
    dom.editorMain = byId("editor-main");
    dom.editorSplit = byId("editor-split");
    dom.tabbarMain = byId("tabbar-main");
    dom.tabbarSplit = byId("tabbar-split");
    dom.splitGroup = document.querySelector('.editor-group[data-group="split"]');
    dom.editorSplitter = byId("editor-splitter");
    dom.panelsShell = byId("panels-shell");
    dom.panelsSplitter = byId("panels-splitter");
    dom.panelsLayout = byId("panels-layout");
    dom.terminal = byId("terminal");
    dom.runOutput = byId("run-output");
    dom.runStatus = byId("run-status");
    dom.statusText = byId("status-text");
    dom.cursorText = byId("cursor-text");
    dom.panelCwd = byId("panel-cwd");
    dom.shellSelect = byId("shell-select");
    dom.paletteOverlay = byId("palette-overlay");
    dom.paletteInput = byId("palette-input");
    dom.paletteList = byId("palette-list");
    dom.contextMenu = byId("context-menu");
    dom.sidebarSplitter = byId("sidebar-splitter");
    dom.terminalOutputSplitter = byId("terminal-output-splitter");
  }

  function bindUi() {
    renderToolbar();
    byId("set-luau-path-button").addEventListener("click", chooseLuauPath);
    byId("split-active-button").addEventListener("click", () => splitDocument(activeDoc()));
    byId("hide-panels-button").addEventListener("click", togglePanels);
    byId("restart-shell-button").addEventListener("click", restartShell);
    byId("shell-select").addEventListener("change", async (event) => {
      state.shellType = event.target.value;
      await restartShell();
      scheduleStateSave();
    });
    document.querySelector('[data-action="new-file"]').innerHTML = icons.plus;
    document.querySelector('[data-action="new-folder"]').innerHTML = icons.folder;
    document.querySelector('[data-action="rename-path"]').innerHTML = icons.edit;
    document.querySelector('[data-action="delete-path"]').innerHTML = icons.trash;
    document.querySelector('[data-action="new-file"]').addEventListener("click", createFileInExplorer);
    document.querySelector('[data-action="new-folder"]').addEventListener("click", createFolderInExplorer);
    document.querySelector('[data-action="rename-path"]').addEventListener("click", renameSelectedPath);
    document.querySelector('[data-action="delete-path"]').addEventListener("click", deleteSelectedPath);
    dom.paletteInput.addEventListener("input", filterPalette);
    dom.paletteInput.addEventListener("keydown", (event) => {
      const items = state.palette.filtered || state.palette.items;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        state.palette.index = Math.min(items.length - 1, state.palette.index + 1);
        renderPaletteItems(items);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        state.palette.index = Math.max(0, state.palette.index - 1);
        renderPaletteItems(items);
      } else if (event.key === "Enter") {
        event.preventDefault();
        const item = items[state.palette.index];
        if (item) {
          state.palette.onSelect(item);
          hidePalette();
        }
      } else if (event.key === "Escape") {
        hidePalette();
      }
    });
    dom.paletteOverlay.addEventListener("click", (event) => {
      if (event.target === dom.paletteOverlay) {
        hidePalette();
      }
    });
    window.addEventListener("click", (event) => {
      if (!dom.contextMenu.contains(event.target)) {
        hideContextMenu();
      }
    });
    window.addEventListener("resize", fitTerminal);
    wireResizers();
    registerShortcuts();
  }

  async function init() {
    bindDom();
    bindUi();
    const monaco = await loadMonaco();
    initEditors(monaco);
    initTerminal();
    await bootstrapState();
    await window.desktopAPI.startShell({ type: state.shellType, cwd: state.projectRoot || "C:\\" });
    applyModelToEditor("main");
    applyModelToEditor("split");
    fitTerminal();
    setStatus("Ready");
  }

  window.addEventListener("DOMContentLoaded", () => {
    init().catch((error) => {
      console.error(error);
      alert(`Failed to start Electron IDE: ${error.message}`);
    });
  });
})();
