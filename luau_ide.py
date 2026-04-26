import queue
import re
import shutil
import subprocess
import tempfile
import threading
import json
import importlib.util
import ctypes
import io
import logging
import os
import sys
import webbrowser
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog, messagebox, simpledialog, ttk

BG = "#16181d"
PANEL_BG = "#1b1f27"
ACTIVITY_BG = "#222834"
EDITOR_BG = "#10141b"
EDITOR_FG = "#d4d4d4"
OUTPUT_BG = "#0d1117"
OUTPUT_FG = "#d4d4d4"
ACCENT = "#007acc"
SECONDARY = "#ff9f1c"
BTN_BG = "#2a3140"
BTN_HOVER = "#384154"
BORDER = "#2d3441"
LINE_BG = "#161b22"
LINE_FG = "#8b949e"
SUCCESS_FG = "#4ec9b0"
ERROR_FG = "#f48771"
INFO_FG = "#569cd6"
TERMINAL_PROMPT = "#c586c0"
EXPLORER_DIR = "#4fc1ff"
EXPLORER_FILE = "#dbe4ff"
TAB_ACTIVE = "#10141b"
STATUS_BG = "#0b6aa2"
SEARCH_FG = "#dcdcaa"
MULTI_CURSOR_BG = "#264f78"
MULTI_CURSOR_FG = "#ffffff"

FILE_ICON_ACCENTS = {
    "default": "#94a3b8",
    "folder": "#f59e0b",
    "luau": "#38bdf8",
    "lua": "#60a5fa",
    "python": "#10b981",
    "markdown": "#f97316",
    "text": "#a78bfa",
    "json": "#22c55e",
    "toml": "#eab308",
    "yaml": "#f59e0b",
    "xml": "#fb7185",
    "html": "#fb7185",
    "css": "#06b6d4",
    "javascript": "#facc15",
    "typescript": "#3b82f6",
    "react": "#38bdf8",
    "config": "#c084fc",
    "shell": "#84cc16",
    "powershell": "#2563eb",
    "image": "#ec4899",
    "archive": "#f97316",
    "binary": "#ef4444",
    "git": "#f97316",
    "lock": "#64748b",
    "docker": "#0ea5e9",
}

FILE_ICON_NAME_OVERRIDES = {
    "readme": "markdown",
    "readme.md": "markdown",
    "license": "text",
    "license.txt": "text",
    "changelog.md": "markdown",
    "package.json": "javascript",
    "package-lock.json": "lock",
    "tsconfig.json": "typescript",
    "jsconfig.json": "javascript",
    ".gitignore": "git",
    ".gitattributes": "git",
    ".gitmodules": "git",
    ".editorconfig": "config",
    ".env": "config",
    ".env.example": "config",
    "dockerfile": "docker",
    "compose.yml": "docker",
    "compose.yaml": "docker",
    "docker-compose.yml": "docker",
    "docker-compose.yaml": "docker",
    "makefile": "config",
    "cmakelists.txt": "config",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "poetry.lock": "lock",
    "pipfile": "python",
    "pipfile.lock": "lock",
    "wally.toml": "toml",
    "selene.toml": "toml",
    "aftman.toml": "toml",
    "foreman.toml": "toml",
    "default.project.json": "json",
    "sourcemap.json": "json",
}

FILE_ICON_SUFFIX_OVERRIDES = {
    ".luau": "luau",
    ".lua": "lua",
    ".py": "python",
    ".pyw": "python",
    ".md": "markdown",
    ".txt": "text",
    ".log": "text",
    ".json": "json",
    ".jsonc": "json",
    ".json5": "json",
    ".toml": "toml",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".xml": "xml",
    ".svg": "image",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "css",
    ".sass": "css",
    ".less": "css",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".d.ts": "typescript",
    ".tsx": "react",
    ".jsx": "react",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".ps1": "powershell",
    ".psm1": "powershell",
    ".psd1": "powershell",
    ".cmd": "shell",
    ".bat": "shell",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".webp": "image",
    ".ico": "image",
    ".bmp": "image",
    ".zip": "archive",
    ".7z": "archive",
    ".rar": "archive",
    ".tar": "archive",
    ".gz": "archive",
    ".tgz": "archive",
    ".exe": "binary",
    ".dll": "binary",
    ".bin": "binary",
    ".lock": "lock",
}

KEYWORDS = {
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
    "while",
}

BUILTINS = {
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
    "rawequal",
    "rawget",
    "rawlen",
    "rawset",
    "require",
    "script",
    "select",
    "setmetatable",
    "string",
    "table",
    "task",
    "tonumber",
    "tostring",
    "type",
    "utf8",
    "warn",
    "workspace",
}

TOKEN_RE = re.compile(
    r"(?P<comment>--\[\[[\s\S]*?\]\]|--[^\n]*)"
    r"|(?P<string>\[(=*)\[[\s\S]*?\]\3\]|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>\b[A-Za-z_][A-Za-z0-9_]*\b)"
)

SHELL_SENTINEL = "__LUAU_IDE_SHELL__"
LUAU_EXE = r"C:\luau\luau.exe"
APP_NAME = "Lume"
APP_ID = "Lume.IDE"
APP_VERSION = "0.9.0"
APP_RELEASES_URL = "https://github.com/luau-lang/luau/releases"
LUAU_RELEASE_API = "https://api.github.com/repos/luau-lang/luau/releases/latest"
FONT_UI = ("Segoe UI", 10)
DEFAULT_CODE_FONT_SIZE = 10
DEFAULT_TERM_FONT_SIZE = 10
DEFAULT_TAB_WIDTH = 4
AUTO_PAIRS = {
    "(": ")",
    "{": "}",
    "[": "]",
    '"': '"',
    "'": "'",
}
CLOSING_CHARS = set(AUTO_PAIRS.values())


@dataclass
class EditorTab:
    frame: tk.Frame
    text: tk.Text
    lines: tk.Text
    y_scroll: tk.Scrollbar
    x_scroll: tk.Scrollbar
    path: Path | None
    untitled_name: str
    document_key: str = ""
    modified: bool = False
    highlight_job: str | None = None
    diagnostics_job: str | None = None
    loaded: bool = False
    diagnostics: str = "Ready"
    is_peer: bool = False
    multi_cursors: list[str] = field(default_factory=list)


@dataclass
class TerminalSession:
    session_id: str
    frame: tk.Frame
    text: tk.Text
    shell_name: str
    title: str
    output_queue: queue.Queue = field(default_factory=queue.Queue)
    process: subprocess.Popen | None = None
    busy: bool = False
    alive: bool = False
    command_id: int = 0
    current_marker: str | None = None
    command_history: list[str] = field(default_factory=list)
    history_index: int = 0
    prompt_index: str = "1.0"
    cwd: Path | None = None
    pending_input: str = ""


class LuauIDE:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("1480x920")
        self.root.minsize(1120, 720)
        self.root.configure(bg=BG)

        self.project_root = Path.cwd()
        self.appdata_root = self._appdata_root_path()
        self.state_path = self.appdata_root / "luau_ide_state.json"
        self.runtime_root = self._runtime_root_path()
        self.logs_root = self.appdata_root / "logs"
        self.backup_root = self.appdata_root / "recovery"
        self.log_path = self.logs_root / "lume.log"
        self.logo_path = self._resource_path("logo.png")
        self.material_icons_root = self._resource_path("assets/material_icons")
        self.logo_image = None
        self.logo_small = None
        self.running = False
        self.process = None
        self.material_icon_manifest = {}
        self.material_icon_definitions = {}
        self.material_file_names = {}
        self.material_file_extensions = {}
        self.material_folder_names = {}
        self.material_folder_names_expanded = {}
        self.material_root_folder_names = {}
        self.material_root_folder_names_expanded = {}
        self.material_default_file_icon = "default"
        self.material_default_folder_icon = "folder"
        self.material_default_folder_open_icon = "folder"
        self.material_default_root_folder_icon = "folder"
        self.material_default_root_folder_open_icon = "folder"
        self.material_icon_theme_ready = False
        self.material_tree_icons = {}

        self.tabs: dict[str, EditorTab] = {}
        self.text_to_tab: dict[str, EditorTab] = {}
        self.untitled_counter = 1
        self.syncing_documents: set[str] = set()

        self.terminal_sessions: dict[str, TerminalSession] = {}
        self.active_terminal_id: str | None = None
        self.terminal_counter = 1
        self.sidebar_visible = True
        self.panels_visible = True
        self.outline_visible = True
        self.git_bash_path = self._detect_git_bash()
        self.dragdrop_backend = self._detect_dragdrop_backend()
        self.lsp_executable = self._detect_lsp_executable()
        self.shell_options = ["PowerShell", "Command Prompt"] + (["Git Bash"] if self.git_bash_path else [])
        self.shell_var = tk.StringVar(value=self.shell_options[0])
        self.luau_path_var = tk.StringVar(value=LUAU_EXE)
        self.code_font = tkfont.Font(family="Cascadia Code", size=DEFAULT_CODE_FONT_SIZE)
        self.term_font = tkfont.Font(family="Cascadia Code", size=DEFAULT_TERM_FONT_SIZE)
        self.line_font = tkfont.Font(family="Cascadia Code", size=max(DEFAULT_CODE_FONT_SIZE - 1, 8))
        self.notebook_tab_font = tkfont.Font(family="Segoe UI Semibold", size=9)
        self.recent_files: list[str] = []
        self.recent_projects: list[str] = []
        self.session_state = self._load_state()
        self.palette_window = None
        self.palette_entry = None
        self.palette_listbox = None
        self.palette_items = []
        self.palette_mode = None
        self.palette_select_callback = None
        self.completion_popup = None
        self.completion_listbox = None
        self.completion_items = []
        self.completion_tab = None
        self.notebook_close_target = None
        self.notebook_close_meta = None
        self.terminal_notebook_close_target = None
        self.terminal_context_session = None
        self.tab_drag_source = None
        self.tab_drag_notebook = None
        self.tab_drag_reordered = False
        self.tab_drag_press_root = None
        self.tab_drag_started = False
        self.explorer_drag_path = None
        self.explorer_drag_press_root = None
        self.explorer_drag_started = False
        self.context_menu_tab = None
        self.split_visible = False
        self.active_notebook = None
        self.tab_notebooks: dict[str, ttk.Notebook] = {}
        self.tree_icons = {}
        self.peer_counter = 1
        self.editor_clipboard_is_line = False
        self.editor_clipboard_value = ""
        self.find_panel_visible = False
        self.find_match_index = None
        self.autosave_job_by_tab: dict[str, str] = {}
        self.autosave_mode = "off"
        self.autosave_delay_ms = 1500
        self.tab_width_spaces = DEFAULT_TAB_WIDTH
        self.current_theme_name = "Midnight"
        self.settings_window = None
        self.editor_tab_bars: dict[str, tk.Frame] = {}
        self.terminal_tab_bar = None

        self._configure_logging()
        self._configure_style()
        self._configure_windows_chrome()
        self._load_brand_assets()
        self._load_material_icon_theme()
        self._build_tree_icons()
        self._build_titlebar()
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self._bind_shortcuts()
        self._setup_dragdrop()

        self._apply_loaded_state()
        self._apply_startup_editor_focus_layout()
        self._ensure_luau_runtime_async()

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=PANEL_BG,
            fieldbackground=PANEL_BG,
            foreground=EDITOR_FG,
            rowheight=24,
            borderwidth=0,
            font=FONT_UI,
        )
        style.map(
            "Treeview",
            background=[("selected", "#094771")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.layout("Tabless.TNotebook.Tab", [])
        style.layout("Tabless.TNotebook", [("Notebook.client", {"sticky": "nswe"})])
        style.configure(
            "TNotebook.Tab",
            background=PANEL_BG,
            foreground=LINE_FG,
            padding=(16, 8),
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", TAB_ACTIVE)],
            foreground=[("selected", "#ffffff")],
        )
        style.configure("TNotebook", tabmargins=(8, 4, 8, 0))
        style.configure(
            "Modern.Vertical.TScrollbar",
            background="#334155",
            troughcolor="#0f172a",
            arrowcolor="#cbd5e1",
            bordercolor="#0f172a",
            lightcolor="#334155",
            darkcolor="#334155",
            gripcount=0,
        )
        style.configure(
            "Modern.Horizontal.TScrollbar",
            background="#334155",
            troughcolor="#0f172a",
            arrowcolor="#cbd5e1",
            bordercolor="#0f172a",
            lightcolor="#334155",
            darkcolor="#334155",
            gripcount=0,
        )
        style.configure(
            "Modern.TCombobox",
            fieldbackground="#111827",
            background="#1f2937",
            foreground="#e5e7eb",
            arrowcolor="#e5e7eb",
            bordercolor="#374151",
            lightcolor="#1f2937",
            darkcolor="#1f2937",
            padding=4,
        )
        style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", "#111827")],
            background=[("readonly", "#111827")],
            foreground=[("readonly", "#e5e7eb")],
            selectbackground=[("readonly", "#111827")],
            selectforeground=[("readonly", "#e5e7eb")],
        )

    def _resource_path(self, name):
        candidates = []
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            candidates.append(Path(sys.executable).resolve().parent / name)
        candidates.append(Path(__file__).resolve().parent / name)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[-1]

    def _appdata_root_path(self):
        local_appdata = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        root = local_appdata / APP_NAME
        root.mkdir(parents=True, exist_ok=True)
        return root

    def _runtime_root_path(self):
        return self._appdata_root_path() / "runtime"

    def _configure_logging(self):
        try:
            self.logs_root.mkdir(parents=True, exist_ok=True)
            self.backup_root.mkdir(parents=True, exist_ok=True)
            self.logger = logging.getLogger(APP_NAME)
            self.logger.setLevel(logging.INFO)
            self.logger.handlers.clear()
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            self.logger.addHandler(handler)
            self.logger.propagate = False
            self.logger.info("Launching %s %s", APP_NAME, APP_VERSION)
        except Exception:
            self.logger = logging.getLogger(APP_NAME)

    def _log_info(self, message, *args):
        try:
            self.logger.info(message, *args)
        except Exception:
            pass

    def _log_exception(self, message, *args):
        try:
            self.logger.exception(message, *args)
        except Exception:
            pass

    def _configure_windows_chrome(self):
        if os.name != "nt":
            return
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass
        self.root.after(120, self._apply_dark_titlebar)

    def _hidden_subprocess_kwargs(self):
        if os.name != "nt":
            return {}
        kwargs = {}
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            kwargs["startupinfo"] = startupinfo
        except Exception:
            pass
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return kwargs

    def _apply_dark_titlebar(self):
        if os.name != "nt":
            return
        try:
            hwnd = self.root.winfo_id()
            value = ctypes.c_int(1)
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
        except Exception:
            pass

    def _load_brand_assets(self):
        if not self.logo_path.exists():
            return
        try:
            self.logo_image = tk.PhotoImage(file=str(self.logo_path))
            self.logo_small = self.logo_image.subsample(max(self.logo_image.width() // 40, 1), max(self.logo_image.height() // 40, 1))
            self.root.iconphoto(True, self.logo_small, self.logo_image)
        except Exception:
            self.logo_image = None
            self.logo_small = None

    def _load_material_icon_theme(self):
        manifest_path = self.material_icons_root / "material-icons.json"
        if not manifest_path.exists():
            return
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._log_exception("Failed to load Material Icon Theme manifest from %s", manifest_path)
            return

        def _lower_map(values):
            return {str(key).lower(): value for key, value in values.items()}

        self.material_icon_manifest = manifest
        self.material_icon_definitions = manifest.get("iconDefinitions", {})
        self.material_file_names = _lower_map(manifest.get("fileNames", {}))
        self.material_file_extensions = _lower_map(manifest.get("fileExtensions", {}))
        self.material_folder_names = _lower_map(manifest.get("folderNames", {}))
        self.material_folder_names_expanded = _lower_map(manifest.get("folderNamesExpanded", {}))
        self.material_root_folder_names = _lower_map(manifest.get("rootFolderNames", {}))
        self.material_root_folder_names_expanded = _lower_map(manifest.get("rootFolderNamesExpanded", {}))
        self.material_default_file_icon = manifest.get("file", "default")
        self.material_default_folder_icon = manifest.get("folder", "folder")
        self.material_default_folder_open_icon = manifest.get("folderExpanded", self.material_default_folder_icon)
        self.material_default_root_folder_icon = manifest.get("rootFolder", self.material_default_folder_icon)
        self.material_default_root_folder_open_icon = manifest.get("rootFolderExpanded", self.material_default_root_folder_icon)
        self.material_icon_theme_ready = bool(self.material_icon_definitions)

    def _material_icon_path(self, icon_key):
        if not icon_key:
            return None
        definition = self.material_icon_definitions.get(icon_key)
        if not definition:
            return None
        icon_path = definition.get("iconPath")
        if not icon_path:
            return None
        candidate = (self.material_icons_root / icon_path).resolve()
        return candidate if candidate.exists() else None

    def _candidate_luau_paths(self):
        candidates = [
            Path(self.luau_path_var.get().strip()),
            self._resource_path("luau.exe"),
            self.runtime_root / "luau.exe",
        ]
        found = shutil.which("luau.exe") or shutil.which("luau")
        if found:
            candidates.append(Path(found))
        unique = []
        for candidate in candidates:
            if not candidate:
                continue
            candidate = Path(candidate)
            if candidate not in unique:
                unique.append(candidate)
        return unique

    def _resolve_existing_luau_path(self):
        for candidate in self._candidate_luau_paths():
            if candidate.exists():
                return candidate.resolve()
        return None

    def _download_luau_runtime(self):
        self.runtime_root.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(
            LUAU_RELEASE_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"{APP_NAME}/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            release_data = json.loads(response.read().decode("utf-8"))
        assets = release_data.get("assets", [])
        asset_url = None
        for asset in assets:
            name = asset.get("name", "").lower()
            if "windows" in name and name.endswith(".zip"):
                asset_url = asset.get("browser_download_url")
                break
        if not asset_url:
            raise RuntimeError("Could not locate a Windows Luau runtime asset in the latest release.")
        with urllib.request.urlopen(asset_url, timeout=60) as response:
            archive_data = response.read()
        with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
            exe_members = [member for member in archive.namelist() if member.lower().endswith("luau.exe")]
            if not exe_members:
                raise RuntimeError("Downloaded Luau archive did not contain luau.exe.")
            member = exe_members[0]
            extracted = archive.read(member)
        target = self.runtime_root / "luau.exe"
        target.write_bytes(extracted)
        return target.resolve()

    def _ensure_luau_runtime_async(self):
        resolved = self._resolve_existing_luau_path()
        if resolved:
            self.luau_path_var.set(str(resolved))
            return

        def worker():
            try:
                runtime_path = self._download_luau_runtime()
            except (OSError, urllib.error.URLError, RuntimeError, zipfile.BadZipFile) as exc:
                self._log_exception("Luau runtime provisioning failed")
                self.root.after(0, lambda: self._set_status(f"Luau runtime unavailable: {exc}"))
                return
            self.root.after(0, lambda path=runtime_path: self._finish_luau_runtime_setup(path))

        self._set_status("Provisioning Luau runtime...")
        threading.Thread(target=worker, daemon=True).start()

    def _finish_luau_runtime_setup(self, runtime_path):
        self.luau_path_var.set(str(runtime_path))
        self._save_state()
        self._set_status(f"Luau runtime ready: {runtime_path.name}")

    def _build_titlebar(self):
        bar = tk.Frame(self.root, bg=PANEL_BG, height=38)
        self.titlebar_frame = bar
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        brand = tk.Frame(bar, bg=PANEL_BG)
        brand.pack(side=tk.LEFT, padx=12)
        if self.logo_small:
            tk.Label(brand, image=self.logo_small, bg=PANEL_BG).pack(side=tk.LEFT, padx=(0, 8), pady=4)
        tk.Label(
            brand,
            text=APP_NAME,
            bg=PANEL_BG,
            fg="#ffffff",
            font=("Segoe UI Semibold", 12),
        ).pack(side=tk.LEFT)
        tk.Label(
            brand,
            text="  luau workspace",
            bg=PANEL_BG,
            fg=SECONDARY,
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT)

        self.title_label = tk.Label(
            bar,
            text=str(self.project_root),
            bg=PANEL_BG,
            fg=LINE_FG,
            font=("Segoe UI", 9),
        )
        self.title_label.pack(side=tk.LEFT, padx=(10, 0))

    def _build_tree_icons(self):
        self.tree_icons.clear()
        self.material_tree_icons.clear()
        for icon_key, accent in FILE_ICON_ACCENTS.items():
            if icon_key == "folder":
                self.tree_icons[icon_key] = self._create_folder_icon(accent)
            else:
                self.tree_icons[icon_key] = self._create_file_icon(accent)

    def _tree_icon_image(self, icon_key, fallback_key):
        candidate = self._material_icon_path(icon_key) if self.material_icon_theme_ready else None
        if candidate:
            if icon_key in self.material_tree_icons:
                return self.material_tree_icons[icon_key]
            try:
                image = tk.PhotoImage(file=str(candidate))
                self.material_tree_icons[icon_key] = image
                return image
            except Exception:
                self._log_exception("Failed to load tree icon %s from %s", icon_key, candidate)
        if icon_key and icon_key in self.tree_icons:
            return self.tree_icons[icon_key]
        return self.tree_icons.get(fallback_key, self.tree_icons["default"])

    def _normalized_project_relative_path(self, path):
        try:
            relative = Path(path).resolve().relative_to(self.project_root.resolve())
        except ValueError:
            return None
        return relative.as_posix().lower()

    def _fallback_file_icon_key(self, path):
        name = path.name.lower()
        if name in FILE_ICON_NAME_OVERRIDES:
            return FILE_ICON_NAME_OVERRIDES[name]
        stem = path.stem.lower()
        if stem in FILE_ICON_NAME_OVERRIDES:
            return FILE_ICON_NAME_OVERRIDES[stem]
        for suffix, icon_key in sorted(FILE_ICON_SUFFIX_OVERRIDES.items(), key=lambda item: len(item[0]), reverse=True):
            if name.endswith(suffix):
                return icon_key
        return "default"

    def _candidate_file_extensions(self, path):
        name = path.name.lower()
        parts = name.split(".")
        if len(parts) <= 1:
            return []
        return [".".join(parts[index:]) for index in range(1, len(parts))]

    def _material_file_icon_key(self, path):
        if not self.material_icon_theme_ready:
            return None
        relative = self._normalized_project_relative_path(path)
        name = path.name.lower()
        for candidate in (relative, name):
            if candidate and candidate in self.material_file_names:
                return self.material_file_names[candidate]
        for candidate in self._candidate_file_extensions(path):
            if candidate in self.material_file_extensions:
                return self.material_file_extensions[candidate]
        return self.material_default_file_icon

    def _material_folder_icon_key(self, path, expanded=False, is_root=False):
        if not self.material_icon_theme_ready:
            return None
        relative = self._normalized_project_relative_path(path)
        name = path.name.lower()
        if is_root:
            exact_names = self.material_root_folder_names_expanded if expanded else self.material_root_folder_names
            default_icon = self.material_default_root_folder_open_icon if expanded else self.material_default_root_folder_icon
        else:
            exact_names = self.material_folder_names_expanded if expanded else self.material_folder_names
            default_icon = self.material_default_folder_open_icon if expanded else self.material_default_folder_icon
        for candidate in (relative, name):
            if candidate and candidate in exact_names:
                return exact_names[candidate]
        return default_icon

    def _file_icon_key(self, path):
        return self._material_file_icon_key(path) or self._fallback_file_icon_key(path)

    def _folder_icon_key(self, path, expanded=False, is_root=False):
        return self._material_folder_icon_key(path, expanded=expanded, is_root=is_root) or "folder"

    def _icon_image_for_path(self, path, expanded=False, is_root=False):
        if path.is_dir():
            icon_key = self._folder_icon_key(path, expanded=expanded, is_root=is_root)
            return self._tree_icon_image(icon_key, "folder")
        icon_key = self._file_icon_key(path)
        return self._tree_icon_image(icon_key, self._fallback_file_icon_key(path))

    def _create_file_icon(self, accent):
        image = tk.PhotoImage(width=16, height=16)
        image.put("#000000", to=(0, 0, 16, 16))
        image.transparency_set(0, 0, True)
        image.put("#e5e7eb", to=(3, 1, 13, 15))
        image.put("#0f172a", to=(4, 2, 12, 14))
        image.put("#dbeafe", to=(4, 2, 11, 13))
        image.put(accent, to=(4, 11, 12, 13))
        image.put("#ffffff", to=(11, 2, 13, 4))
        image.put("#cbd5e1", to=(10, 3, 12, 5))
        return image

    def _create_folder_icon(self, accent):
        image = tk.PhotoImage(width=16, height=16)
        image.put("#000000", to=(0, 0, 16, 16))
        image.transparency_set(0, 0, True)
        image.put("#fde68a", to=(2, 5, 14, 14))
        image.put(accent, to=(2, 4, 8, 7))
        image.put("#fbbf24", to=(2, 7, 14, 14))
        image.put("#f59e0b", to=(2, 6, 14, 7))
        return image

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=ACTIVITY_BG, height=48)
        self.toolbar_frame = toolbar
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        self.toolbar_menu = tk.Menu(self.root, tearoff=0, bg=PANEL_BG, fg=EDITOR_FG, activebackground="#0f4c81", activeforeground="#ffffff")
        self.toolbar_menu.add_command(label="New Tab", command=self._new_tab)
        self.toolbar_menu.add_command(label="Open File...", command=self._open_file)
        self.toolbar_menu.add_command(label="Open Folder...", command=self._open_folder)
        self.toolbar_menu.add_command(label="Recent Projects...", command=self._show_recent_projects)
        self.toolbar_menu.add_separator()
        self.toolbar_menu.add_command(label="Save", command=self._save_active_tab)
        self.toolbar_menu.add_command(label="Save As...", command=self._save_active_tab_as)
        self.toolbar_menu.add_command(label="Save All", command=self._save_all_tabs)
        self.toolbar_menu.add_command(label="Split Active Tab", command=self._split_active_tab)
        self.toolbar_menu.add_separator()
        self.toolbar_menu.add_command(label="Settings...", command=self._show_settings)
        self.toolbar_menu.add_command(label="Set luau.exe Path...", command=self._choose_luau_path)
        self.toolbar_menu.add_command(label="Check For Updates", command=self._check_for_updates)
        self.toolbar_menu.add_command(label="Refresh Project", command=self._refresh_project)

        self._toolbar_button(toolbar, "menu", "Menu", self._show_toolbar_menu, bg="#4338ca", hover="#4f46e5")
        self._toolbar_button(toolbar, "sidebar", "Explorer", self._toggle_sidebar, bg="#374151", hover="#475569")
        self._toolbar_button(toolbar, "sidebar", "Panels", self._toggle_panels, bg="#374151", hover="#475569")
        self._toolbar_button(toolbar, "file", "Outline", self._toggle_outline, bg="#374151", hover="#475569")
        self._toolbar_button(toolbar, "new", "New", self._new_tab, bg="#415a77", hover="#52708f")
        self._toolbar_button(toolbar, "run", "Run", self._run, bg="#0e7490", hover="#1389ab")
        self._toolbar_button(toolbar, "stop", "Stop", self._stop, bg="#7f1d1d", hover="#991b1b")
        self._toolbar_button(toolbar, "find", "Find", self._find_in_active_tab)
        self._toolbar_button(toolbar, "refresh", "Refresh", self._refresh_project)

        tk.Frame(toolbar, bg=ACTIVITY_BG).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def _toolbar_button(self, parent, icon_name, text, command, bg=None, hover=None):
        base_bg = bg or BTN_BG
        hover_bg = hover or BTN_HOVER
        btn = tk.Frame(
            parent,
            bg=base_bg,
        )
        btn.pack(side=tk.LEFT, padx=4, pady=4)
        btn.configure(cursor="hand2")
        icon = tk.Canvas(btn, width=18, height=18, bg=base_bg, highlightthickness=0, bd=0)
        icon.pack(side=tk.LEFT, padx=(10, 6), pady=8)
        self._draw_toolbar_icon(icon, icon_name, "#e2e8f0")
        label = tk.Label(
            btn,
            text=text,
            bg=base_bg,
            fg=EDITOR_FG,
            font=("Segoe UI Semibold", 10),
            padx=0,
            pady=8,
            cursor="hand2",
        )
        label.pack(side=tk.LEFT, padx=(0, 12))

        def apply_bg(color):
            btn.config(bg=color)
            icon.config(bg=color)
            label.config(bg=color)

        for widget in (btn, icon, label):
            widget.bind("<Button-1>", lambda _e: command())
            widget.bind("<Enter>", lambda _e, c=hover_bg: apply_bg(c))
            widget.bind("<Leave>", lambda _e, c=base_bg: apply_bg(c))
        return btn

    def _show_toolbar_menu(self):
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery() + 8
            self.toolbar_menu.tk_popup(x, y)
        finally:
            self.toolbar_menu.grab_release()

    def _choose_luau_path(self):
        current = self.luau_path_var.get().strip()
        initial_dir = str(Path(current).parent) if current else str(self.project_root)
        selected = filedialog.askopenfilename(
            title="Select luau.exe",
            initialdir=initial_dir,
            filetypes=[("Executables", "*.exe"), ("All files", "*.*")],
        )
        if not selected:
            return
        self.luau_path_var.set(selected)
        self._save_state()
        self._set_status(f"luau.exe set: {Path(selected).name}")

    def _save_all_tabs(self):
        saved = 0
        for tab in list(self.tabs.values()):
            if not tab.modified and tab.path:
                continue
            if not self._save_tab(tab):
                return False
            saved += 1
        self._set_status("All tabs saved" if saved else "Nothing to save")
        return True

    def _draw_toolbar_icon(self, canvas, icon_name, color):
        if icon_name == "sidebar":
            canvas.create_rectangle(2, 3, 16, 15, outline=color, width=1.5)
            canvas.create_line(7, 3, 7, 15, fill=color, width=1.5)
        elif icon_name == "new":
            canvas.create_line(9, 3, 9, 15, fill=color, width=2)
            canvas.create_line(3, 9, 15, 9, fill=color, width=2)
            canvas.create_rectangle(2.5, 2.5, 15.5, 15.5, outline=color, width=1.2)
        elif icon_name == "close":
            canvas.create_line(4, 4, 14, 14, fill=color, width=2)
            canvas.create_line(14, 4, 4, 14, fill=color, width=2)
        elif icon_name == "run":
            canvas.create_polygon(5, 3, 15, 9, 5, 15, fill=color, outline=color)
        elif icon_name == "stop":
            canvas.create_rectangle(4, 4, 14, 14, fill=color, outline=color)
        elif icon_name == "folder":
            canvas.create_polygon(2, 6, 7, 6, 9, 4, 16, 4, 16, 14, 2, 14, fill="", outline=color, width=1.5)
        elif icon_name == "file":
            canvas.create_rectangle(4, 2, 14, 16, outline=color, width=1.5)
            canvas.create_line(6, 7, 12, 7, fill=color, width=1.5)
            canvas.create_line(6, 10, 12, 10, fill=color, width=1.5)
        elif icon_name == "save":
            canvas.create_rectangle(3, 3, 15, 15, outline=color, width=1.5)
            canvas.create_rectangle(6, 4, 12, 7, fill=color, outline=color)
            canvas.create_rectangle(6, 10, 12, 14, outline=color, width=1.3)
        elif icon_name == "save_as":
            canvas.create_rectangle(2.5, 3, 12.5, 15, outline=color, width=1.5)
            canvas.create_line(13, 6, 16, 3, fill=color, width=1.5)
            canvas.create_line(13, 6, 16, 9, fill=color, width=1.5)
        elif icon_name == "find":
            canvas.create_oval(3, 3, 11, 11, outline=color, width=1.8)
            canvas.create_line(10.5, 10.5, 15, 15, fill=color, width=2)
        elif icon_name == "refresh":
            canvas.create_arc(3, 3, 15, 15, start=20, extent=280, outline=color, width=1.8, style=tk.ARC)
            canvas.create_line(12, 4, 15, 4, fill=color, width=1.8)
            canvas.create_line(12, 4, 14, 7, fill=color, width=1.8)
        elif icon_name == "menu":
            canvas.create_line(3, 5, 15, 5, fill=color, width=2)
            canvas.create_line(3, 9, 15, 9, fill=color, width=2)
            canvas.create_line(3, 13, 15, 13, fill=color, width=2)

    def _build_body(self):
        self.outer_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=5, bd=0)
        self.outer_pane.pack(fill=tk.BOTH, expand=True)

        self.sidebar_frame = tk.Frame(self.outer_pane, bg=PANEL_BG, width=320)
        self.outer_pane.add(self.sidebar_frame, minsize=220)

        self.main_pane = tk.PanedWindow(self.outer_pane, orient=tk.VERTICAL, bg=BORDER, sashwidth=5, bd=0)
        self.outer_pane.add(self.main_pane)

        self._build_sidebar(self.sidebar_frame)
        self._build_editor(self.main_pane)
        self._build_bottom_panel(self.main_pane)
        self.root.after(80, self._set_initial_layout)

    def _build_sidebar(self, parent):
        header = tk.Frame(parent, bg=PANEL_BG, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="EXPLORER",
            bg=PANEL_BG,
            fg="#9ccfd8",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT, padx=10, pady=10)

        self.folder_label = tk.Label(
            header,
            text=str(self.project_root),
            bg=PANEL_BG,
            fg=EDITOR_FG,
            font=("Segoe UI", 8),
        )
        self.folder_label.pack(side=tk.LEFT, padx=(4, 10), pady=10)

        self._mini_toolbar_button(header, "Delete", self._delete_selected_path).pack(side=tk.RIGHT, padx=4, pady=6)
        self._mini_toolbar_button(header, "Rename", self._rename_selected_path).pack(side=tk.RIGHT, padx=4, pady=6)
        self._mini_toolbar_button(header, "New File", self._new_file_in_selected_dir).pack(side=tk.RIGHT, padx=4, pady=6)
        self._mini_toolbar_button(header, "New Folder", self._new_folder_in_selected_dir).pack(side=tk.RIGHT, padx=4, pady=6)

        tree_frame = tk.Frame(parent, bg=PANEL_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(tree_frame, style="Modern.Vertical.TScrollbar")
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree = ttk.Treeview(tree_frame, show="tree", yscrollcommand=tree_scroll.set, selectmode="browse")
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.file_tree.yview)
        self.file_tree.tag_configure("dir", foreground=EXPLORER_DIR)
        self.file_tree.tag_configure("file", foreground=EXPLORER_FILE)
        self.file_tree.bind("<<TreeviewOpen>>", self._expand_selected_node)
        self.file_tree.bind("<<TreeviewClose>>", self._collapse_selected_node)
        self.file_tree.bind("<Double-1>", self._open_selected_tree_item)
        self.file_tree.bind("<Return>", self._open_selected_tree_item)
        self.file_tree.bind("<Button-3>", self._show_tree_menu)
        self.file_tree.bind("<ButtonPress-1>", self._on_tree_item_press, add="+")
        self.file_tree.bind("<B1-Motion>", self._on_tree_item_drag_motion, add="+")
        self.file_tree.bind("<ButtonRelease-1>", self._on_tree_item_drag_release, add="+")

        self.tree_menu = tk.Menu(self.root, tearoff=0, bg=PANEL_BG, fg=EDITOR_FG, activebackground="#094771", activeforeground="#ffffff")
        self.tree_menu.add_command(label="New File", command=self._new_file_in_selected_dir)
        self.tree_menu.add_command(label="New Folder", command=self._new_folder_in_selected_dir)
        self.tree_menu.add_command(label="Rename", command=self._rename_selected_path)
        self.tree_menu.add_command(label="Delete", command=self._delete_selected_path)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Copy Path", command=self._copy_selected_path)
        self.tree_menu.add_command(label="Copy Relative Path", command=self._copy_selected_relative_path)
        self.tree_menu.add_command(label="Copy Name", command=self._copy_selected_name)
        self.tree_menu.add_command(label="Open In Terminal", command=self._open_selected_in_terminal)
        self.tree_menu.add_separator()
        self.tree_menu.add_command(label="Refresh", command=self._refresh_project)

        footer = tk.Frame(parent, bg="#141922", height=34)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        self.sidebar_hint = tk.Label(
            footer,
            text="Tabs, shell, find, git commands, and project navigation are all active",
            bg="#141922",
            fg=LINE_FG,
            font=("Segoe UI", 8),
        )
        self.sidebar_hint.pack(side=tk.LEFT, padx=10, pady=9)

    def _tree_label_for_path(self, path):
        return path.name

    def _icon_key_for_path(self, path):
        if path.is_dir():
            return self._folder_icon_key(path)
        return self._file_icon_key(path)

    def _mini_toolbar_button(self, parent, text, command, padding=(8, 4), font=("Segoe UI", 8)):
        button = tk.Label(
            parent,
            text=text,
            bg=BTN_BG,
            fg=EDITOR_FG,
            font=font,
            padx=padding[0],
            pady=padding[1],
            cursor="hand2",
        )
        button.bind("<Button-1>", lambda _e: command())
        button.bind("<Enter>", lambda _e: button.config(bg=BTN_HOVER))
        button.bind("<Leave>", lambda _e: button.config(bg=BTN_BG))
        return button

    def _build_editor(self, parent):
        editor_shell = tk.Frame(parent, bg=BG)
        parent.add(editor_shell, minsize=280)

        header = tk.Frame(editor_shell, bg=PANEL_BG, height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="EDITOR", bg=PANEL_BG, fg="#9ccfd8", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        self.breadcrumb_label = tk.Label(header, text="", bg=PANEL_BG, fg="#9fb3c8", font=("Segoe UI", 8))
        self.breadcrumb_label.pack(side=tk.LEFT, padx=10)
        self._mini_toolbar_button(header, "Split", self._split_active_tab, padding=(8, 2)).pack(side=tk.RIGHT, padx=(0, 8), pady=4)
        self.diagnostics_label = tk.Label(header, text="Diagnostics ready", bg=PANEL_BG, fg=LINE_FG, font=("Segoe UI", 8))
        self.diagnostics_label.pack(side=tk.RIGHT, padx=10)

        self.find_panel = tk.Frame(editor_shell, bg="#111827", height=34)
        self.find_panel.pack(fill=tk.X)
        self.find_panel.pack_propagate(False)
        self.find_panel.pack_forget()
        tk.Label(self.find_panel, text="Find", bg="#111827", fg="#9ccfd8", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=(10, 6))
        self.find_var = tk.StringVar()
        self.replace_var = tk.StringVar()
        self.find_entry = tk.Entry(self.find_panel, textvariable=self.find_var, bg="#0b1220", fg=EDITOR_FG, insertbackground=EDITOR_FG, relief=tk.FLAT, font=("Cascadia Code", 10), width=22)
        self.find_entry.pack(side=tk.LEFT, padx=(0, 8), ipady=4)
        tk.Label(self.find_panel, text="Replace", bg="#111827", fg=LINE_FG, font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=(0, 6))
        self.replace_entry = tk.Entry(self.find_panel, textvariable=self.replace_var, bg="#0b1220", fg=EDITOR_FG, insertbackground=EDITOR_FG, relief=tk.FLAT, font=("Cascadia Code", 10), width=22)
        self.replace_entry.pack(side=tk.LEFT, padx=(0, 8), ipady=4)
        self._mini_toolbar_button(self.find_panel, "Next", self._find_next, padding=(7, 2)).pack(side=tk.LEFT, padx=4, pady=4)
        self._mini_toolbar_button(self.find_panel, "Prev", self._find_previous, padding=(7, 2)).pack(side=tk.LEFT, padx=4, pady=4)
        self._mini_toolbar_button(self.find_panel, "Replace", self._replace_current_match, padding=(7, 2)).pack(side=tk.LEFT, padx=4, pady=4)
        self._mini_toolbar_button(self.find_panel, "All", self._replace_all_matches, padding=(7, 2)).pack(side=tk.LEFT, padx=4, pady=4)
        self._mini_toolbar_button(self.find_panel, "X", self._hide_find_panel, padding=(7, 2)).pack(side=tk.RIGHT, padx=8, pady=4)
        self.find_entry.bind("<Return>", lambda _e: self._find_next())
        self.replace_entry.bind("<Return>", lambda _e: self._replace_current_match())

        self.editor_content_pane = tk.PanedWindow(editor_shell, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=4, bd=0)
        self.editor_content_pane.pack(fill=tk.BOTH, expand=True)

        self.editor_tabs_frame = tk.Frame(self.editor_content_pane, bg=EDITOR_BG)
        self.editor_content_pane.add(self.editor_tabs_frame, minsize=420)

        self.editor_split_pane = tk.PanedWindow(self.editor_tabs_frame, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=4, bd=0)
        self.editor_split_pane.pack(fill=tk.BOTH, expand=True)

        self.primary_editor_frame = tk.Frame(self.editor_split_pane, bg=EDITOR_BG)
        self.secondary_editor_frame = tk.Frame(self.editor_split_pane, bg=EDITOR_BG)
        self.editor_split_pane.add(self.primary_editor_frame, minsize=260)

        self.outline_frame = tk.Frame(self.editor_content_pane, bg=PANEL_BG, width=230)
        self.editor_content_pane.add(self.outline_frame, minsize=170)

        self.editor_notebook = self._create_editor_notebook(self.primary_editor_frame)
        self.split_notebook = self._create_editor_notebook(self.secondary_editor_frame)
        self.active_notebook = self.editor_notebook

        self.tab_context_menu = tk.Menu(self.root, tearoff=0, bg=PANEL_BG, fg=EDITOR_FG, activebackground="#0f4c81", activeforeground="#ffffff")
        self.tab_context_menu.add_command(label="Close", command=self._close_context_menu_tab)
        self.tab_context_menu.add_command(label="Close Others", command=lambda: self._close_other_tabs())
        self.tab_context_menu.add_command(label="Close All", command=self._close_all_tabs)
        self.tab_context_menu.add_separator()
        self.tab_context_menu.add_command(label="Split Right", command=self._split_context_menu_tab)
        self.tab_context_menu.add_command(label="Reveal In Explorer", command=self._reveal_context_menu_tab)

        outline_header = tk.Frame(self.outline_frame, bg=PANEL_BG, height=28)
        outline_header.pack(fill=tk.X)
        outline_header.pack_propagate(False)
        tk.Label(outline_header, text="OUTLINE", bg=PANEL_BG, fg="#9ccfd8", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=10, pady=5)
        self.outline_status = tk.Label(outline_header, text="", bg=PANEL_BG, fg=LINE_FG, font=("Segoe UI", 8))
        self.outline_status.pack(side=tk.RIGHT, padx=10, pady=5)

        outline_body = tk.Frame(self.outline_frame, bg=PANEL_BG)
        outline_body.pack(fill=tk.BOTH, expand=True)
        outline_scroll = ttk.Scrollbar(outline_body, style="Modern.Vertical.TScrollbar")
        outline_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.outline_list = tk.Listbox(
            outline_body,
            bg="#0f172a",
            fg=EDITOR_FG,
            relief=tk.FLAT,
            borderwidth=0,
            selectbackground="#1d4ed8",
            selectforeground="#ffffff",
            font=("Cascadia Code", 10),
            yscrollcommand=outline_scroll.set,
        )
        self.outline_list.pack(fill=tk.BOTH, expand=True)
        outline_scroll.config(command=self.outline_list.yview)
        self.outline_list.bind("<Double-Button-1>", self._jump_to_outline_item)
        self.outline_list.bind("<Return>", self._jump_to_outline_item)

    def _create_editor_notebook(self, parent):
        shell = tk.Frame(parent, bg=EDITOR_BG)
        shell.pack(fill=tk.BOTH, expand=True)
        tab_bar = tk.Frame(shell, bg="#0f172a", height=28)
        tab_bar.pack(fill=tk.X)
        tab_bar.pack_propagate(False)
        notebook = ttk.Notebook(shell, style="Tabless.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)
        self.editor_tab_bars[str(notebook)] = tab_bar
        self._bind_notebook_events(notebook)
        return notebook

    def _bind_notebook_events(self, notebook):
        notebook.bind("<<NotebookTabChanged>>", self._on_editor_tab_changed)
        notebook.bind("<FocusIn>", lambda _e, current=notebook: self._set_active_notebook(current), add="+")

    def _build_bottom_panel(self, parent):
        self.panels_shell = tk.Frame(parent, bg=BG)
        parent.add(self.panels_shell, minsize=180)

        panel_header = tk.Frame(self.panels_shell, bg="#111827", height=22)
        panel_header.pack(fill=tk.X)
        panel_header.pack_propagate(False)
        tk.Label(panel_header, text="PANELS", bg="#111827", fg="#9ccfd8", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=8, pady=2)
        self._mini_toolbar_button(panel_header, "x", self._toggle_panels, padding=(7, 1), font=("Segoe UI", 8, "bold")).pack(side=tk.RIGHT, padx=(4, 8), pady=1)
        self.cwd_label = tk.Label(panel_header, text=str(self.project_root), bg="#111827", fg=EDITOR_FG, font=("Segoe UI", 8))
        self.cwd_label.pack(side=tk.RIGHT, padx=8)
        tk.Label(panel_header, text="Shell", bg="#111827", fg=LINE_FG, font=("Segoe UI", 8)).pack(side=tk.RIGHT, padx=(0, 5))
        self.shell_combo = ttk.Combobox(
            panel_header,
            values=self.shell_options,
            textvariable=self.shell_var,
            state="readonly",
            width=14,
            style="Modern.TCombobox",
        )
        self.shell_combo.pack(side=tk.RIGHT, padx=(0, 8), pady=1)
        self.shell_combo.bind("<<ComboboxSelected>>", self._on_shell_changed)
        self.root.option_add("*TCombobox*Listbox.background", "#111827")
        self.root.option_add("*TCombobox*Listbox.foreground", "#e5e7eb")
        self.root.option_add("*TCombobox*Listbox.selectBackground", "#1d4ed8")
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        self.bottom_pane = tk.PanedWindow(self.panels_shell, orient=tk.HORIZONTAL, bg=BORDER, sashwidth=5, bd=0)
        self.bottom_pane.pack(fill=tk.BOTH, expand=True)

        terminal_frame = tk.Frame(self.bottom_pane, bg=OUTPUT_BG)
        output_frame = tk.Frame(self.bottom_pane, bg=OUTPUT_BG)
        self.bottom_pane.add(terminal_frame, minsize=260)
        self.bottom_pane.add(output_frame, minsize=240)

        terminal_header = tk.Frame(terminal_frame, bg="#0f172a", height=20)
        terminal_header.pack(fill=tk.X)
        terminal_header.pack_propagate(False)
        self.terminal_title = tk.Label(terminal_header, text="TERMINAL", bg="#0f172a", fg="#9ccfd8", font=("Segoe UI", 8, "bold"))
        self.terminal_title.pack(side=tk.LEFT, padx=8, pady=2)
        self._mini_toolbar_button(terminal_header, "+", self._new_terminal_session, padding=(7, 1)).pack(side=tk.RIGHT, padx=6, pady=1)
        self._mini_toolbar_button(terminal_header, "Restart", self._restart_shell, padding=(7, 1)).pack(side=tk.RIGHT, padx=6, pady=1)

        self.terminal_tab_bar = tk.Frame(terminal_frame, bg="#0b1220", height=28)
        self.terminal_tab_bar.pack(fill=tk.X)
        self.terminal_tab_bar.pack_propagate(False)

        self.terminal_notebook = ttk.Notebook(terminal_frame, style="Tabless.TNotebook")
        self.terminal_notebook.pack(fill=tk.BOTH, expand=True)
        self.terminal_notebook.bind("<<NotebookTabChanged>>", self._on_terminal_tab_changed)

        self.terminal_context_menu = tk.Menu(self.root, tearoff=0, bg=PANEL_BG, fg=EDITOR_FG, activebackground="#0f4c81", activeforeground="#ffffff")
        self.terminal_context_menu.add_command(label="New Terminal", command=self._new_terminal_session)
        self.terminal_context_menu.add_command(label="Restart", command=self._restart_shell)
        self.terminal_context_menu.add_separator()
        self.terminal_context_menu.add_command(label="Rename", command=self._rename_context_terminal)
        self.terminal_context_menu.add_command(label="Close", command=self._close_context_terminal)

        out_header = tk.Frame(output_frame, bg="#0f172a", height=20)
        out_header.pack(fill=tk.X)
        out_header.pack_propagate(False)
        tk.Label(out_header, text="RUN OUTPUT", bg="#0f172a", fg="#9ccfd8", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=8, pady=2)
        self.run_state_label = tk.Label(out_header, text="Idle", bg="#0f172a", fg=LINE_FG, font=("Segoe UI", 8))
        self.run_state_label.pack(side=tk.RIGHT, padx=8, pady=2)

        out_frame = tk.Frame(output_frame, bg=OUTPUT_BG)
        out_frame.pack(fill=tk.BOTH, expand=True)
        out_scroll = ttk.Scrollbar(out_frame, style="Modern.Vertical.TScrollbar")
        out_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output = tk.Text(
            out_frame,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            font=self.term_font,
            bd=0,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            state=tk.DISABLED,
            wrap=tk.WORD,
            yscrollcommand=out_scroll.set,
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        out_scroll.config(command=self.output.yview)
        self.output.tag_configure("success", foreground=SUCCESS_FG)
        self.output.tag_configure("error", foreground=ERROR_FG)
        self.output.tag_configure("info", foreground=INFO_FG)
        self.output.tag_configure("dim", foreground=LINE_FG)
        self._new_terminal_session(start_immediately=False)

    def _active_terminal_session(self):
        if self.active_terminal_id and self.active_terminal_id in self.terminal_sessions:
            return self.terminal_sessions[self.active_terminal_id]
        selected = self.terminal_notebook.select() if hasattr(self, "terminal_notebook") else ""
        if selected:
            for session in self.terminal_sessions.values():
                if str(session.frame) == selected:
                    self.active_terminal_id = session.session_id
                    return session
        if self.terminal_sessions:
            self.active_terminal_id = next(iter(self.terminal_sessions))
            return self.terminal_sessions[self.active_terminal_id]
        return None

    def _new_terminal_session(self, start_immediately=True, shell_name=None, title=None):
        shell_name = shell_name or self.shell_var.get()
        frame = tk.Frame(self.terminal_notebook, bg=OUTPUT_BG)
        text_frame = tk.Frame(frame, bg=OUTPUT_BG)
        text_frame.pack(fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(text_frame, style="Modern.Vertical.TScrollbar")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text = tk.Text(
            text_frame,
            bg=OUTPUT_BG,
            fg=OUTPUT_FG,
            font=self.term_font,
            bd=0,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            wrap=tk.WORD,
            yscrollcommand=scroll.set,
            selectbackground="#264f78",
            insertbackground=EDITOR_FG,
        )
        text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=text.yview)
        for tag, color in (
            ("prompt", TERMINAL_PROMPT),
            ("stdout", OUTPUT_FG),
            ("stderr", ERROR_FG),
            ("info", INFO_FG),
            ("success", SUCCESS_FG),
        ):
            text.tag_configure(tag, foreground=color)

        session_id = f"terminal-{self.terminal_counter}"
        session_title = title or f"Terminal {self.terminal_counter}"
        self.terminal_counter += 1
        session = TerminalSession(
            session_id=session_id,
            frame=frame,
            text=text,
            shell_name=shell_name,
            title=session_title,
            cwd=self.project_root,
        )
        self.terminal_sessions[session_id] = session
        self.terminal_notebook.add(frame, text=self._terminal_session_label(session))
        self.terminal_notebook.select(frame)
        self.active_terminal_id = session_id
        self._bind_terminal_session(session)
        self.shell_var.set(shell_name)
        self._update_terminal_header()
        self._render_terminal_tab_bar()
        if start_immediately:
            self._start_shell(session)
        return session

    def _clear_terminal_sessions(self):
        self._stop_shell()
        for session in list(self.terminal_sessions.values()):
            try:
                self.terminal_notebook.forget(session.frame)
            except tk.TclError:
                pass
        self.terminal_sessions.clear()
        self.active_terminal_id = None
        self._render_terminal_tab_bar()

    def _start_all_terminal_sessions(self):
        for session in self.terminal_sessions.values():
            self._start_shell(session)

    def _bind_terminal_session(self, session):
        text = session.text
        text.bind("<Return>", lambda _e, current=session: self._on_terminal_enter(current))
        text.bind("<BackSpace>", lambda _e, current=session: self._on_terminal_backspace(current))
        text.bind("<Left>", lambda _e, current=session: self._on_terminal_left(current))
        text.bind("<Home>", lambda _e, current=session: self._on_terminal_home(current))
        text.bind("<Up>", lambda _e, current=session: self._on_terminal_history_up(current))
        text.bind("<Down>", lambda _e, current=session: self._on_terminal_history_down(current))
        text.bind("<Button-1>", lambda _e, current=session: self._on_terminal_click(current))
        text.bind("<KeyPress>", lambda event, current=session: self._on_terminal_keypress(current, event))
        text.bind("<KeyRelease>", lambda _e, current=session: self._on_terminal_keyrelease(current))
        text.bind("<<Paste>>", lambda _e, current=session: self._on_terminal_paste(current))
        text.bind("<Control-v>", lambda _e, current=session: self._on_terminal_paste(current))
        text.bind("<Control-V>", lambda _e, current=session: self._on_terminal_paste(current))
        text.bind("<Shift-Insert>", lambda _e, current=session: self._on_terminal_paste(current))

    def _update_terminal_header(self):
        session = self._active_terminal_session()
        if not session:
            self.terminal_title.config(text="TERMINAL")
            self.cwd_label.config(text=self._format_shell_path(self.project_root))
            return
        self.terminal_title.config(text=f"TERMINAL  {session.shell_name}")
        self.cwd_label.config(text=self._format_shell_path(session.cwd or self.project_root))

    def _on_terminal_tab_changed(self, _event=None):
        session = self._active_terminal_session()
        if not session:
            self._render_terminal_tab_bar()
            return
        self.shell_var.set(session.shell_name)
        self._update_terminal_header()
        self._render_terminal_tab_bar()
        session.text.focus_set()

    def _terminal_session_label(self, session):
        return session.title

    def _tab_title_text(self, tab):
        name = tab.path.name if tab.path else tab.untitled_name
        prefix = "* " if tab.modified else ""
        return f"{prefix}{name}"

    def _clear_tab_bar(self, bar):
        for child in bar.winfo_children():
            child.destroy()

    def _build_tab_chip(self, bar, title, active, on_select, on_close, on_menu=None):
        bg = TAB_ACTIVE if active else "#162033"
        fg = "#ffffff" if active else "#cbd5e1"
        chip = tk.Frame(bar, bg=bg, bd=0, highlightthickness=0, cursor="hand2")
        chip.pack(side=tk.LEFT, padx=(0, 1), pady=0)
        label = tk.Label(chip, text=title, bg=bg, fg=fg, font=("Segoe UI Semibold", 9), padx=10, pady=6, cursor="hand2")
        label.pack(side=tk.LEFT)
        close = tk.Button(
            chip,
            text="×",
            command=on_close,
            bg=bg,
            fg="#9fb3c8",
            activebackground="#7f1d1d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            highlightthickness=0,
            takefocus=0,
        )
        close.pack(side=tk.LEFT)
        for widget in (chip, label):
            if on_select:
                widget.bind("<Button-1>", lambda _e: on_select())
            if on_menu:
                widget.bind("<Button-3>", lambda e: on_menu(e), add="+")
        close.bind("<Enter>", lambda _e: close.config(bg="#7f1d1d", fg="#ffffff"))
        close.bind("<Leave>", lambda _e, c=bg: close.config(bg=c, fg="#9fb3c8"))
        if on_menu:
            close.bind("<Button-3>", lambda e: on_menu(e), add="+")
        return chip

    def _render_terminal_tab_bar(self):
        if not self.terminal_tab_bar:
            return
        self._clear_tab_bar(self.terminal_tab_bar)
        selected = self.terminal_notebook.select() if hasattr(self, "terminal_notebook") else ""
        for frame_id in self.terminal_notebook.tabs():
            session = next((item for item in self.terminal_sessions.values() if str(item.frame) == frame_id), None)
            if not session:
                continue
            self._build_tab_chip(
                self.terminal_tab_bar,
                session.title,
                frame_id == selected,
                on_select=lambda current=session: self._select_terminal_session(current),
                on_close=lambda current=session: self._close_terminal_session(current),
                on_menu=lambda event, current=session: self._show_terminal_context_for_session(event, current),
            )
        filler = tk.Frame(self.terminal_tab_bar, bg="#0b1220")
        filler.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _render_editor_tab_bar(self, notebook):
        bar = self.editor_tab_bars.get(str(notebook))
        if not bar:
            return
        self._clear_tab_bar(bar)
        selected = notebook.select()
        for frame_id in notebook.tabs():
            tab = self.tabs.get(frame_id)
            if not tab:
                continue
            chip = self._build_tab_chip(
                bar,
                self._tab_title_text(tab),
                frame_id == selected,
                on_select=None,
                on_close=lambda current=tab: self._close_tab(current),
                on_menu=lambda event, current=tab, current_notebook=notebook: self._show_tab_context_for_item(event, current, current_notebook),
            )
            chip.tab_frame_id = frame_id
            chip.tab_notebook = notebook
            for widget in (chip, chip.winfo_children()[0]):
                widget.bind(
                    "<ButtonPress-1>",
                    lambda event, current=tab, current_notebook=notebook: self._on_editor_chip_press(current, current_notebook, event),
                    add="+",
                )
        filler = tk.Frame(bar, bg="#0f172a")
        filler.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _render_all_editor_tab_bars(self):
        self._render_editor_tab_bar(self.editor_notebook)
        self._render_editor_tab_bar(self.split_notebook)

    def _editor_tab_chips(self, bar):
        return [child for child in bar.winfo_children() if getattr(child, "tab_frame_id", None)]

    def _editor_tab_bar_for_notebook(self, notebook):
        return self.editor_tab_bars.get(str(notebook))

    def _editor_notebook_for_bar(self, bar):
        for notebook in (self.editor_notebook, self.split_notebook):
            if self.editor_tab_bars.get(str(notebook)) == bar:
                return notebook
        return None

    def _editor_bar_from_widget(self, widget):
        while widget is not None:
            if widget in self.editor_tab_bars.values():
                return widget
            widget = widget.master
        return None

    def _widget_descends_from(self, widget, ancestor):
        while widget is not None:
            if widget == ancestor:
                return True
            widget = widget.master
        return False

    def _editor_drop_index(self, bar, x_root, frame_id=None):
        chips = [chip for chip in self._editor_tab_chips(bar) if getattr(chip, "tab_frame_id", None) != frame_id]
        if not chips:
            return 0
        local_x = x_root - bar.winfo_rootx()
        for index, chip in enumerate(chips):
            midpoint = chip.winfo_x() + (chip.winfo_width() / 2)
            if local_x < midpoint:
                return index
        return len(chips)

    def _reorder_notebook_tab(self, notebook, frame_id, target_index):
        current_tabs = list(notebook.tabs())
        if frame_id not in current_tabs:
            return
        new_tabs = [item for item in current_tabs if item != frame_id]
        target_index = max(0, min(target_index, len(new_tabs)))
        new_tabs.insert(target_index, frame_id)
        if new_tabs == current_tabs:
            return
        for index, item in enumerate(new_tabs):
            notebook.insert(index, item)
        self.tab_drag_reordered = True
        self._render_editor_tab_bar(notebook)

    def _editor_drag_target_notebook(self, x_root, y_root, source_notebook):
        widget = self.root.winfo_containing(x_root, y_root)
        bar = self._editor_bar_from_widget(widget)
        if bar is not None:
            target = self._editor_notebook_for_bar(bar)
            if target:
                return target
        pane_x = self.editor_split_pane.winfo_rootx()
        pane_width = self.editor_split_pane.winfo_width()
        if pane_width <= 0:
            return source_notebook
        if source_notebook == self.editor_notebook and x_root >= pane_x + int(pane_width * 0.72):
            return self.split_notebook
        if source_notebook == self.split_notebook and x_root <= pane_x + int(pane_width * 0.28):
            return self.editor_notebook
        return source_notebook

    def _editor_drop_target_notebook(self, x_root, y_root):
        widget = self.root.winfo_containing(x_root, y_root)
        bar = self._editor_bar_from_widget(widget)
        if bar is not None:
            target = self._editor_notebook_for_bar(bar)
            if target:
                return target
        if widget is not None:
            if self._widget_descends_from(widget, self.primary_editor_frame):
                return self.editor_notebook
            if self.split_visible and self._widget_descends_from(widget, self.secondary_editor_frame):
                return self.split_notebook
        pane_x = self.editor_split_pane.winfo_rootx()
        pane_y = self.editor_split_pane.winfo_rooty()
        pane_width = self.editor_split_pane.winfo_width()
        pane_height = self.editor_split_pane.winfo_height()
        if pane_width <= 0 or pane_height <= 0:
            return None
        inside_editor = pane_x <= x_root <= pane_x + pane_width and pane_y <= y_root <= pane_y + pane_height
        if not inside_editor:
            return None
        if self.split_visible:
            midpoint = pane_x + (pane_width / 2)
            return self.split_notebook if x_root >= midpoint else self.editor_notebook
        if x_root >= pane_x + int(pane_width * 0.72):
            return self.split_notebook
        return self.editor_notebook

    def _open_path_in_notebook(self, path, notebook):
        path = Path(path).resolve()
        if notebook == self.split_notebook and not self.split_visible:
            self._show_split_editor()
        existing = self._tab_for_path(path)
        if existing and self.tab_notebooks.get(str(existing.frame)) == notebook:
            self._select_tab(existing)
            return existing
        self._open_path_in_tab(path, notebook=notebook, force_duplicate=bool(existing))
        return self._tab_for_path(path)

    def _on_editor_chip_press(self, tab, notebook, event):
        self._select_tab(tab)
        self.tab_drag_source = tab
        self.tab_drag_notebook = notebook
        self.tab_drag_reordered = False
        self.tab_drag_started = False
        self.tab_drag_press_root = (event.x_root, event.y_root)
        return "break"

    def _on_editor_chip_drag_motion(self, event):
        if not self.tab_drag_source or not self.tab_drag_notebook or not self.tab_drag_press_root:
            return None
        if not self.tab_drag_started:
            dx = abs(event.x_root - self.tab_drag_press_root[0])
            dy = abs(event.y_root - self.tab_drag_press_root[1])
            if max(dx, dy) < 6:
                return None
            self.tab_drag_started = True
        target_notebook = self._editor_drag_target_notebook(event.x_root, event.y_root, self.tab_drag_notebook)
        if target_notebook != self.tab_drag_notebook:
            return None
        target_bar = self._editor_tab_bar_for_notebook(target_notebook)
        if not target_bar:
            return None
        target_index = self._editor_drop_index(target_bar, event.x_root, str(self.tab_drag_source.frame))
        self._reorder_notebook_tab(target_notebook, str(self.tab_drag_source.frame), target_index)
        return "break"

    def _on_editor_chip_drag_release(self, event):
        if not self.tab_drag_source or not self.tab_drag_notebook:
            return None
        source_tab = self.tab_drag_source
        source_notebook = self.tab_drag_notebook
        drag_started = self.tab_drag_started
        self.tab_drag_source = None
        self.tab_drag_notebook = None
        self.tab_drag_press_root = None
        self.tab_drag_started = False
        if not drag_started:
            return None
        target_notebook = self._editor_drag_target_notebook(event.x_root, event.y_root, source_notebook)
        if target_notebook != source_notebook:
            self._move_tab_to_notebook(source_tab, target_notebook)
            self._set_status(
                f"Opened {source_tab.path.name if source_tab.path else source_tab.untitled_name} in "
                f"{'split' if target_notebook == self.split_notebook else 'main'} editor"
            )
            return "break"
        target_bar = self._editor_tab_bar_for_notebook(source_notebook)
        if target_bar:
            target_index = self._editor_drop_index(target_bar, event.x_root, str(source_tab.frame))
            self._reorder_notebook_tab(source_notebook, str(source_tab.frame), target_index)
            if self.tab_drag_reordered:
                self._set_status("Tabs reordered")
        return "break"

    def _select_terminal_session(self, session):
        if not session:
            return
        self.active_terminal_id = session.session_id
        self.terminal_notebook.select(session.frame)
        self._on_terminal_tab_changed()

    def _show_terminal_context_for_session(self, event, session):
        self.terminal_context_session = session
        try:
            self.terminal_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.terminal_context_menu.grab_release()
        return "break"

    def _show_tab_context_for_item(self, event, tab, notebook):
        self.context_menu_tab = tab
        self.current_notebook_event = notebook
        self._set_active_notebook(notebook)
        try:
            self.tab_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tab_context_menu.grab_release()
        return "break"

    def _terminal_session_at(self, notebook, x, y):
        try:
            index = notebook.index(f"@{x},{y}")
        except tk.TclError:
            return None, None
        tabs = notebook.tabs()
        if index >= len(tabs):
            return None, None
        frame_id = tabs[index]
        for session in self.terminal_sessions.values():
            if str(session.frame) == frame_id:
                return index, session
        return index, None

    def _notebook_label_close_hit(self, notebook, index, x, y=None):
        try:
            tab_x, tab_y, width, height = notebook.bbox(index)
        except tk.TclError:
            return False
        if y is not None and not (tab_y <= y <= tab_y + height):
            return False
        tabs = notebook.tabs()
        if index >= len(tabs):
            return False
        label_text = notebook.tab(tabs[index], "text")
        if not label_text or not label_text.endswith("x"):
            return False
        label_width = self.notebook_tab_font.measure(label_text)
        prefix_width = self.notebook_tab_font.measure(label_text[:-1])
        content_x = tab_x + max((width - label_width) // 2, 0)
        x_start = content_x + prefix_width - 2
        x_end = content_x + label_width + 2
        return x_start <= x <= x_end

    def _terminal_tab_close_hit(self, notebook, index, x):
        return self._notebook_label_close_hit(notebook, index, x)

    def _close_terminal_session(self, session=None):
        session = session or self._active_terminal_session()
        if not session:
            return
        if not session.busy:
            session.pending_input = self._terminal_current_command(session)
        self._stop_shell(session)
        try:
            self.terminal_notebook.forget(session.frame)
        except tk.TclError:
            pass
        self.terminal_sessions.pop(session.session_id, None)
        self.active_terminal_id = None
        if self.terminal_sessions:
            self._on_terminal_tab_changed()
        else:
            self._update_terminal_header()
            self._render_terminal_tab_bar()
        self._render_terminal_tab_bar()
        self._save_state()
        self._set_status(f"Closed {session.title}")

    def _rename_terminal_session(self, session=None):
        session = session or self._active_terminal_session()
        if not session:
            return
        title = simpledialog.askstring("Rename terminal", "Terminal name:", initialvalue=session.title, parent=self.root)
        if not title:
            return
        session.title = title.strip() or session.title
        try:
            self.terminal_notebook.tab(session.frame, text=self._terminal_session_label(session))
        except tk.TclError:
            return
        self._render_terminal_tab_bar()
        self._save_state()
        self._set_status(f"Renamed terminal to {session.title}")

    def _close_context_terminal(self):
        if self.terminal_context_session:
            self._close_terminal_session(self.terminal_context_session)
        self.terminal_context_session = None

    def _rename_context_terminal(self):
        if self.terminal_context_session:
            self._rename_terminal_session(self.terminal_context_session)
        self.terminal_context_session = None

    def _on_terminal_notebook_button_press(self, event):
        notebook = event.widget
        index, session = self._terminal_session_at(notebook, event.x, event.y)
        self.terminal_notebook_close_target = None
        if session:
            self.active_terminal_id = session.session_id
        if session and self._terminal_tab_close_hit(notebook, index, event.x):
            self.terminal_notebook_close_target = session
            return "break"
        return None

    def _on_terminal_notebook_button_release(self, event):
        notebook = event.widget
        index, session = self._terminal_session_at(notebook, event.x, event.y)
        target = self.terminal_notebook_close_target
        self.terminal_notebook_close_target = None
        if target and session == target and self._terminal_tab_close_hit(notebook, index, event.x):
            self._close_terminal_session(target)
            return "break"
        return None

    def _on_terminal_notebook_middle_click(self, event):
        _index, session = self._terminal_session_at(event.widget, event.x, event.y)
        if session:
            self._close_terminal_session(session)
            return "break"
        return None

    def _show_terminal_context_menu(self, event):
        _index, session = self._terminal_session_at(event.widget, event.x, event.y)
        if not session:
            return None
        self.terminal_context_session = session
        try:
            self.terminal_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.terminal_context_menu.grab_release()
        return "break"

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=STATUS_BG, height=24)
        self.statusbar_frame = bar
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        self.status_label = tk.Label(bar, text="Ready", bg=STATUS_BG, fg="#ffffff", font=("Segoe UI", 9), padx=10)
        self.status_label.pack(side=tk.LEFT)

        self.project_label = tk.Label(bar, text=self.project_root.name, bg=STATUS_BG, fg="#ffffff", font=("Segoe UI", 9), padx=10)
        self.project_label.pack(side=tk.RIGHT)

        self.cursor_label = tk.Label(bar, text="Ln 1, Col 1", bg=STATUS_BG, fg="#ffffff", font=("Segoe UI", 9), padx=10)
        self.cursor_label.pack(side=tk.RIGHT)

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda _e: self._new_tab())
        self.root.bind("<Control-N>", lambda _e: self._new_tab())
        self.root.bind("<Control-w>", lambda _e: self._close_active_tab())
        self.root.bind("<Control-W>", lambda _e: self._close_active_tab())
        self.root.bind("<Control-p>", lambda _e: self._show_quick_open())
        self.root.bind("<Control-P>", lambda _e: self._show_quick_open())
        self.root.bind("<Control-Shift-P>", lambda _e: self._show_command_palette())
        self.root.bind("<Control-Shift-p>", lambda _e: self._show_command_palette())
        self.root.bind("<Control-r>", lambda _e: self._run())
        self.root.bind("<Control-R>", lambda _e: self._run())
        self.root.bind("<F5>", lambda _e: self._run())
        self.root.bind("<Control-s>", lambda _e: self._save_active_tab())
        self.root.bind("<Control-S>", lambda _e: self._save_active_tab())
        self.root.bind("<Control-Shift-S>", lambda _e: self._save_active_tab_as())
        self.root.bind("<Control-Shift-s>", lambda _e: self._save_active_tab_as())
        self.root.bind("<Control-o>", lambda _e: self._open_file())
        self.root.bind("<Control-O>", lambda _e: self._open_file())
        self.root.bind("<Control-Shift-O>", lambda _e: self._open_folder())
        self.root.bind("<Control-Shift-o>", lambda _e: self._open_folder())
        self.root.bind("<Control-f>", lambda _e: self._find_in_active_tab())
        self.root.bind("<Control-F>", lambda _e: self._find_in_active_tab())
        self.root.bind("<Control-h>", lambda _e: self._show_find_panel(with_replace=True))
        self.root.bind("<Control-H>", lambda _e: self._show_find_panel(with_replace=True))
        self.root.bind("<Control-minus>", lambda _e: self._adjust_zoom(-1))
        self.root.bind("<Control-plus>", lambda _e: self._adjust_zoom(1))
        self.root.bind("<Control-equal>", lambda _e: self._adjust_zoom(1))
        self.root.bind("<Control-underscore>", lambda _e: self._adjust_zoom(-1))
        self.root.bind("<Control-0>", lambda _e: self._reset_zoom())
        self.root.bind("<Alt-Shift-Right>", lambda _e: self._split_active_tab())
        self.root.bind("<Control-Shift-K>", lambda _e: self._delete_editor_line(self._active_tab()) if self._active_tab() else "break")
        self.root.bind("<Control-Shift-k>", lambda _e: self._delete_editor_line(self._active_tab()) if self._active_tab() else "break")
        self.root.bind_all("<B1-Motion>", self._on_editor_chip_drag_motion, add="+")
        self.root.bind_all("<ButtonRelease-1>", self._on_editor_chip_drag_release, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _welcome_text(self):
        recent_hint = ""
        if self.recent_projects:
            recent_hint = "-- Recent project launcher is available from Menu > Recent Projects or the command palette.\n"
        return (
            f"-- {APP_NAME} {APP_VERSION}\n"
            "-- Multi-tab editor, project explorer, and integrated terminal.\n"
            "-- Open a folder, create files, and run the current tab with F5.\n"
            "-- Ctrl+F opens find, Ctrl+H opens replace, Ctrl+Shift+K deletes a line.\n"
            f"{recent_hint}"
            "\n"
            "local function greet(name)\n"
            "    return \"Hello, \" .. name .. \"!\"\n"
            "end\n"
            "\n"
            "print(greet(\"Roblox\"))\n"
        )

    def _detect_git_bash(self):
        candidates = [
            Path(r"C:\Program Files\Git\bin\bash.exe"),
            Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
            Path(r"C:\Program Files (x86)\Git\bin\bash.exe"),
            Path(r"C:\Program Files (x86)\Git\usr\bin\bash.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        found = shutil.which("bash")
        return Path(found) if found else None

    def _detect_dragdrop_backend(self):
        if importlib.util.find_spec("tkinterdnd2"):
            return "tkinterdnd2"
        if importlib.util.find_spec("windnd"):
            return "windnd"
        return None

    def _detect_lsp_executable(self):
        for name in ("luau-lsp", "luau-lsp.exe", "lua-language-server", "lua-language-server.exe"):
            found = shutil.which(name)
            if found:
                return found
        return None

    def _load_state(self):
        legacy_path = Path(__file__).with_name("luau_ide_state.json")
        path = self.state_path if self.state_path.exists() else legacy_path
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._log_exception("Failed to load state from %s", path)
            return {}

    def _apply_loaded_state(self):
        state = self.session_state or {}
        code_size = int(state.get("code_font_size", DEFAULT_CODE_FONT_SIZE))
        term_size = int(state.get("term_font_size", DEFAULT_TERM_FONT_SIZE))
        self.code_font.configure(size=max(8, min(24, code_size)))
        self.line_font.configure(size=max(self.code_font.cget("size") - 1, 8))
        self.term_font.configure(size=max(9, min(22, term_size)))
        if state.get("shell") in self.shell_options:
            self.shell_var.set(state["shell"])
        self.luau_path_var.set(state.get("luau_path", LUAU_EXE))
        self.recent_files = [item for item in state.get("recent_files", []) if Path(item).exists()]
        self.recent_projects = [item for item in state.get("recent_projects", []) if Path(item).exists()]
        self.autosave_mode = state.get("autosave_mode", "off")
        self.autosave_delay_ms = int(state.get("autosave_delay_ms", 1500))
        self.tab_width_spaces = int(state.get("tab_width_spaces", DEFAULT_TAB_WIDTH))
        self.current_theme_name = state.get("theme_name", "Midnight")

        root_path = Path(state.get("project_root", self.project_root)).resolve()
        if not root_path.exists():
            root_path = self.project_root
        self._set_project_root(root_path, restart_shell=False)

        terminal_states = state.get("terminal_sessions", [])
        self._clear_terminal_sessions()
        if terminal_states:
            for item in terminal_states:
                shell_name = item.get("shell", self.shell_options[0])
                title = item.get("title")
                session = self._new_terminal_session(start_immediately=False, shell_name=shell_name, title=title)
                session.cwd = Path(item.get("cwd", self.project_root))
                session.command_history = list(item.get("history", []))[-200:]
                session.history_index = len(session.command_history)
                session.pending_input = item.get("pending_input", "")
        else:
            self._new_terminal_session(start_immediately=False, shell_name=self.shell_var.get())
        active_terminal_index = int(state.get("active_terminal_index", 0))
        terminal_tabs = self.terminal_notebook.tabs()
        if terminal_tabs:
            active_terminal_index = max(0, min(len(terminal_tabs) - 1, active_terminal_index))
            self.terminal_notebook.select(terminal_tabs[active_terminal_index])
            self._on_terminal_tab_changed()

        restored_any = False
        open_tabs = state.get("open_tabs", [])
        for item in open_tabs:
            pane = "main"
            path_text = item
            if isinstance(item, dict):
                path_text = item.get("path", "")
                pane = item.get("pane", "main")
            path = Path(path_text)
            if path.exists() and path.is_file():
                if pane == "split":
                    self._show_split_editor()
                    self._open_path_in_tab(path, notebook=self.split_notebook, force_duplicate=True)
                else:
                    self._open_path_in_tab(path, notebook=self.editor_notebook)
                restored_any = True
        if not restored_any:
            self._new_tab(content=self._welcome_text())
        for pane_name, notebook in (("main", self.editor_notebook), ("split", self.split_notebook)):
            selected_path = state.get(f"selected_{pane_name}_tab")
            if selected_path:
                for tab in self.tabs.values():
                    if tab.path == Path(selected_path).resolve() and self.tab_notebooks.get(str(tab.frame)) == notebook:
                        notebook.select(tab.frame)
                        break
        active_pane = state.get("active_editor_pane")
        if active_pane == "split" and self.split_visible:
            self._set_active_notebook(self.split_notebook)
        else:
            self._set_active_notebook(self.editor_notebook)
        self._on_editor_tab_changed()

        if state.get("split_visible"):
            self.root.after(170, self._show_split_editor)
        self.root.after(150, lambda: self._restore_layout(state))
        self.root.after(180, self._start_all_terminal_sessions)
        self.root.after(200, self._apply_tab_width)
        self.root.after(220, lambda: self._apply_theme_preset(self.current_theme_name))

    def _apply_startup_editor_focus_layout(self):
        if self.sidebar_visible:
            self._toggle_sidebar()
        if self.outline_visible:
            self._toggle_outline()
        if self.panels_visible:
            self._toggle_panels()

    def _restore_layout(self, state):
        try:
            sidebar_x = int(state.get("sidebar_sash", 300))
            editor_y = int(state.get("editor_sash", 540))
            bottom_x = int(state.get("bottom_sash", 520))
            outline_x = int(state.get("outline_sash", 960))
            if self.sidebar_visible:
                self.outer_pane.sash_place(0, sidebar_x, 0)
            if self.panels_visible:
                self.main_pane.sash_place(0, 0, editor_y)
            self.bottom_pane.sash_place(0, bottom_x, 0)
            if self.split_visible:
                split_x = int(state.get("split_sash", max(440, self.editor_split_pane.winfo_width() // 2)))
                self.editor_split_pane.sash_place(0, split_x, 0)
            if self.outline_visible:
                self.editor_content_pane.sash_place(0, outline_x, 0)
        except (tk.TclError, ValueError):
            self._set_initial_layout()

    def _remember_recent_file(self, path):
        path_text = str(Path(path).resolve())
        self.recent_files = [item for item in self.recent_files if item != path_text]
        self.recent_files.insert(0, path_text)
        self.recent_files = self.recent_files[:30]

    def _remember_recent_project(self, path):
        path_text = str(Path(path).resolve())
        self.recent_projects = [item for item in self.recent_projects if item != path_text]
        self.recent_projects.insert(0, path_text)
        self.recent_projects = self.recent_projects[:20]

    def _serialized_open_tabs(self):
        items = []
        for pane_name, notebook in (("main", self.editor_notebook), ("split", self.split_notebook)):
            for frame_id in notebook.tabs():
                tab = self.tabs.get(frame_id)
                if tab and tab.path:
                    items.append({"path": str(tab.path), "pane": pane_name})
        return items

    def _selected_notebook_tab_path(self, notebook):
        try:
            frame_id = notebook.select()
        except tk.TclError:
            return ""
        tab = self.tabs.get(frame_id)
        return str(tab.path) if tab and tab.path else ""

    def _serialized_terminal_sessions(self):
        items = []
        for frame_id in self.terminal_notebook.tabs():
            for session in self.terminal_sessions.values():
                if str(session.frame) == frame_id:
                    items.append(
                        {
                            "title": session.title,
                            "shell": session.shell_name,
                            "cwd": str(session.cwd or self.project_root),
                            "history": session.command_history[-200:],
                            "pending_input": self._terminal_pending_input(session),
                        }
                    )
                    break
        return items

    def _active_terminal_index(self):
        try:
            selected = self.terminal_notebook.select()
            tabs = list(self.terminal_notebook.tabs())
            return tabs.index(selected) if selected in tabs else 0
        except tk.TclError:
            return 0

    def _save_state(self):
        state = {
            "project_root": str(self.project_root),
            "open_tabs": self._serialized_open_tabs(),
            "selected_main_tab": self._selected_notebook_tab_path(self.editor_notebook),
            "selected_split_tab": self._selected_notebook_tab_path(self.split_notebook),
            "active_editor_pane": "split" if self.active_notebook == self.split_notebook else "main",
            "shell": self._current_shell_name(),
            "code_font_size": int(self.code_font.cget("size")),
            "term_font_size": int(self.term_font.cget("size")),
            "luau_path": self.luau_path_var.get().strip(),
            "recent_files": self.recent_files,
            "recent_projects": self.recent_projects,
            "terminal_sessions": self._serialized_terminal_sessions(),
            "active_terminal_index": self._active_terminal_index(),
            "autosave_mode": self.autosave_mode,
            "autosave_delay_ms": self.autosave_delay_ms,
            "tab_width_spaces": self.tab_width_spaces,
            "theme_name": self.current_theme_name,
            "sidebar_visible": self.sidebar_visible,
            "panels_visible": self.panels_visible,
            "outline_visible": self.outline_visible,
            "split_visible": self.split_visible,
        }
        try:
            if self.sidebar_visible:
                state["sidebar_sash"] = self.outer_pane.sash_coord(0)[0]
            if self.panels_visible:
                state["editor_sash"] = self.main_pane.sash_coord(0)[1]
            state["bottom_sash"] = self.bottom_pane.sash_coord(0)[0]
            if self.split_visible:
                state["split_sash"] = self.editor_split_pane.sash_coord(0)[0]
            if self.outline_visible:
                state["outline_sash"] = self.editor_content_pane.sash_coord(0)[0]
        except (tk.TclError, IndexError):
            pass
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except OSError:
            self._log_exception("Failed to save state to %s", self.state_path)

    def _ps_quote(self, value):
        return "'" + str(value).replace("'", "''") + "'"

    def _format_shell_path(self, path):
        path = Path(path)
        if self._current_shell_name() == "Git Bash":
            drive = path.drive.rstrip(":").lower()
            tail = str(path).replace("\\", "/")
            if drive:
                tail = tail[len(path.drive):]
                return f"/{drive}{tail}"
        return str(path)

    def _set_project_root(self, path, restart_shell=True):
        self.project_root = Path(path).resolve()
        self._remember_recent_project(self.project_root)
        self.folder_label.config(text=str(self.project_root))
        self.title_label.config(text=str(self.project_root))
        self.project_label.config(text=self.project_root.name)
        for session in self.terminal_sessions.values():
            session.cwd = self.project_root
        self.cwd_label.config(text=self._format_shell_path(self.project_root))
        self._refresh_project()
        if restart_shell and self.terminal_sessions:
            for session in self.terminal_sessions.values():
                self._restart_shell(session)
        self._save_state()

    def _set_initial_layout(self):
        try:
            total_w = self.outer_pane.winfo_width()
            total_h = self.main_pane.winfo_height()
            if total_w > 0:
                self.outer_pane.sash_place(0, min(300, total_w // 4), 0)
            if total_h > 0:
                if self.panels_visible:
                    self.main_pane.sash_place(0, 0, max(420, int(total_h * 0.68)))
                self.bottom_pane.sash_place(0, max(420, self.bottom_pane.winfo_width() // 2), 0)
                if self.split_visible:
                    self.editor_split_pane.sash_place(0, max(340, self.editor_split_pane.winfo_width() // 2), 0)
                if self.outline_visible:
                    self.editor_content_pane.sash_place(0, max(520, int(self.editor_content_pane.winfo_width() * 0.78)), 0)
        except tk.TclError:
            pass

    def _toggle_sidebar(self):
        if self.sidebar_visible:
            try:
                self.outer_pane.forget(self.sidebar_frame)
            except tk.TclError:
                pass
            self.sidebar_visible = False
            self._set_status("Explorer hidden")
        else:
            self.outer_pane.add(self.sidebar_frame, before=self.main_pane, minsize=220)
            self.sidebar_visible = True
            self.root.after(50, self._set_initial_layout)
            self._set_status("Explorer visible")

    def _toggle_panels(self):
        if self.panels_visible:
            try:
                self.main_pane.forget(self.panels_shell)
            except tk.TclError:
                pass
            self.panels_visible = False
            self._set_status("Panels hidden")
        else:
            self.main_pane.add(self.panels_shell, minsize=180)
            self.panels_visible = True
            self.root.after(50, self._set_initial_layout)
            self._set_status("Panels visible")

    def _ensure_panels_visible(self):
        if not self.panels_visible:
            self._toggle_panels()

    def _set_active_notebook(self, notebook):
        if notebook:
            self.active_notebook = notebook

    def _show_split_editor(self):
        if self.split_visible:
            return
        self.editor_split_pane.add(self.secondary_editor_frame, minsize=260)
        self.split_visible = True
        self.root.after(50, self._set_initial_layout)
        self._render_all_editor_tab_bars()
        self._set_status("Split editor visible")

    def _hide_split_editor(self):
        if not self.split_visible:
            return
        if self.split_notebook.tabs():
            return
        try:
            self.editor_split_pane.forget(self.secondary_editor_frame)
        except tk.TclError:
            pass
        self.split_visible = False
        if self.active_notebook == self.split_notebook:
            self.active_notebook = self.editor_notebook
        self._render_all_editor_tab_bars()
        self._set_status("Split editor hidden")

    def _move_tab_to_notebook(self, tab, notebook):
        current = self.tab_notebooks.get(str(tab.frame), self.editor_notebook)
        if current == notebook:
            self._select_tab(tab)
            return
        if notebook == self.split_notebook:
            self._show_split_editor()
        if tab.path:
            for existing in self.tabs.values():
                if existing is tab:
                    continue
                if existing.path == tab.path and self.tab_notebooks.get(str(existing.frame)) == notebook:
                    self._select_tab(existing)
                    self._render_all_editor_tab_bars()
                    return
        clone = self._new_tab(
            path=tab.path,
            notebook=notebook,
            force_duplicate=True,
            document_key=tab.document_key,
            untitled_name=tab.untitled_name,
            peer_source_tab=tab,
        )
        clone.modified = tab.modified
        clone.diagnostics = tab.diagnostics
        clone.text.edit_modified(False)
        self._update_tab_title(clone)
        self.diagnostics_label.config(
            text=clone.diagnostics,
            fg=ERROR_FG if clone.diagnostics.startswith("Syntax hints:") else LINE_FG,
        )
        self._render_all_editor_tab_bars()

    def _split_active_tab(self):
        tab = self._active_tab()
        if not tab:
            return
        target = self.split_notebook if self.tab_notebooks.get(str(tab.frame)) != self.split_notebook else self.editor_notebook
        self._move_tab_to_notebook(tab, target)
        self._set_status(f"Moved {tab.path.name if tab.path else tab.untitled_name} to {'split' if target == self.split_notebook else 'main'} editor")

    def _toggle_outline(self):
        if self.outline_visible:
            try:
                self.editor_content_pane.forget(self.outline_frame)
            except tk.TclError:
                pass
            self.outline_visible = False
            self._set_status("Outline hidden")
        else:
            self.editor_content_pane.add(self.outline_frame, minsize=170)
            self.outline_visible = True
            self.root.after(50, self._set_initial_layout)
            self._set_status("Outline visible")

    def _adjust_zoom(self, delta):
        new_size = max(8, min(24, self.code_font.cget("size") + delta))
        self.code_font.configure(size=new_size)
        self.line_font.configure(size=max(new_size - 1, 8))
        self.term_font.configure(size=max(9, min(22, self.term_font.cget("size") + delta)))
        for tab in self.tabs.values():
            self._update_line_numbers(tab)
        self._set_status(f"Zoom: {new_size}pt")
        return "break"

    def _reset_zoom(self):
        self.code_font.configure(size=DEFAULT_CODE_FONT_SIZE)
        self.line_font.configure(size=max(DEFAULT_CODE_FONT_SIZE - 1, 8))
        self.term_font.configure(size=DEFAULT_TERM_FONT_SIZE)
        for tab in self.tabs.values():
            self._update_line_numbers(tab)
        self._set_status("Zoom reset")
        return "break"

    def _refresh_project(self):
        self._refresh_tree()
        self._refresh_title()
        self._set_status(f"Project ready: {self.project_root.name}")

    def _refresh_tree(self):
        open_paths = self._expanded_tree_paths()
        self.file_tree.delete(*self.file_tree.get_children())
        root_id = self.file_tree.insert(
            "",
            tk.END,
            text=self.project_root.name,
            image=self._icon_image_for_path(self.project_root, expanded=True, is_root=True),
            open=True,
            values=[str(self.project_root)],
            tags=("dir",),
        )
        self._insert_tree_children(root_id, self.project_root)
        self._restore_tree_expansion(root_id, open_paths)

    def _insert_tree_children(self, parent_id, directory):
        try:
            entries = sorted(directory.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        except (PermissionError, FileNotFoundError):
            return

        for entry in entries:
            if entry.name in {"__pycache__", ".git"}:
                continue
            if entry.is_dir():
                node_id = self.file_tree.insert(
                    parent_id,
                    tk.END,
                    text=self._tree_label_for_path(entry),
                    image=self._icon_image_for_path(entry, expanded=False),
                    values=[str(entry)],
                    tags=("dir",),
                )
                if self._directory_has_children(entry):
                    self.file_tree.insert(node_id, tk.END, text="loading", values=["dummy"])
            else:
                self.file_tree.insert(
                    parent_id,
                    tk.END,
                    text=self._tree_label_for_path(entry),
                    image=self._icon_image_for_path(entry),
                    values=[str(entry)],
                    tags=("file",),
                )

    def _expanded_tree_paths(self):
        expanded = set()
        stack = list(self.file_tree.get_children())
        while stack:
            item = stack.pop()
            values = self.file_tree.item(item, "values")
            if values and self.file_tree.item(item, "open"):
                expanded.add(values[0])
            stack.extend(self.file_tree.get_children(item))
        return expanded

    def _restore_tree_expansion(self, parent_id, open_paths):
        stack = [parent_id]
        while stack:
            item = stack.pop()
            values = self.file_tree.item(item, "values")
            if values and values[0] in open_paths:
                self.file_tree.item(item, open=True)
                self._update_tree_item_icon(item, is_open=True)
                self._expand_specific_node(item)
            stack.extend(self.file_tree.get_children(item))

    def _directory_has_children(self, directory):
        try:
            next(directory.iterdir())
            return True
        except (StopIteration, PermissionError, FileNotFoundError):
            return False

    def _expand_selected_node(self, _event=None):
        item_id = self.file_tree.focus()
        if not item_id:
            return
        self._expand_specific_node(item_id)

    def _collapse_selected_node(self, _event=None):
        item_id = self.file_tree.focus()
        if not item_id:
            return
        self._update_tree_item_icon(item_id, is_open=False)

    def _expand_specific_node(self, item_id):
        values = self.file_tree.item(item_id, "values")
        if not values:
            return
        path = Path(values[0])
        if not path.is_dir():
            return
        self._update_tree_item_icon(item_id, is_open=True)
        children = self.file_tree.get_children(item_id)
        if len(children) == 1 and self.file_tree.item(children[0], "values") == ("dummy",):
            self.file_tree.delete(children[0])
            self._insert_tree_children(item_id, path)

    def _tree_item_path(self, item_id):
        values = self.file_tree.item(item_id, "values")
        if not values or values == ("dummy",):
            return None
        return Path(values[0])

    def _update_tree_item_icon(self, item_id, is_open):
        path = self._tree_item_path(item_id)
        if not path or not path.exists() or not path.is_dir():
            return
        is_root = path.resolve() == self.project_root.resolve()
        self.file_tree.item(item_id, image=self._icon_image_for_path(path, expanded=is_open, is_root=is_root))

    def _reveal_path_in_tree(self, path):
        target = Path(path).resolve()
        if not str(target).startswith(str(self.project_root)):
            self._set_project_root(target.parent if target.is_file() else target)
        self._refresh_tree()
        current_id = self.file_tree.get_children("")
        if not current_id:
            return
        node_id = current_id[0]
        parts = [self.project_root]
        if target != self.project_root:
            relative = target.relative_to(self.project_root)
            cursor = self.project_root
            for part in relative.parts:
                cursor = cursor / part
                parts.append(cursor)
        for part in parts[1:]:
            self.file_tree.item(node_id, open=True)
            self._expand_specific_node(node_id)
            for child_id in self.file_tree.get_children(node_id):
                values = self.file_tree.item(child_id, "values")
                if values and Path(values[0]) == part:
                    node_id = child_id
                    break
        self.file_tree.selection_set(node_id)
        self.file_tree.focus(node_id)
        self.file_tree.see(node_id)
        if target.is_file():
            self._set_status(f"Revealed {target.name} in explorer")

    def _open_selected_tree_item(self, _event=None):
        item_id = None
        if _event is not None and hasattr(_event, "y"):
            item_id = self.file_tree.identify_row(_event.y)
            if item_id:
                self.file_tree.selection_set(item_id)
                self.file_tree.focus(item_id)
        if not item_id:
            item_id = self.file_tree.focus()
        if not item_id:
            return
        values = self.file_tree.item(item_id, "values")
        if not values:
            return
        path = Path(values[0])
        if path.is_file():
            self._open_path_in_tab(path)

    def _on_tree_item_press(self, event):
        self.explorer_drag_path = None
        self.explorer_drag_press_root = None
        self.explorer_drag_started = False
        item_id = self.file_tree.identify_row(event.y)
        if not item_id:
            return None
        self.file_tree.selection_set(item_id)
        self.file_tree.focus(item_id)
        values = self.file_tree.item(item_id, "values")
        if not values:
            return None
        path = Path(values[0])
        if path.is_file():
            self.explorer_drag_path = path
            self.explorer_drag_press_root = (event.x_root, event.y_root)
        return None

    def _on_tree_item_drag_motion(self, event):
        if not self.explorer_drag_path or not self.explorer_drag_press_root:
            return None
        if not self.explorer_drag_started:
            dx = abs(event.x_root - self.explorer_drag_press_root[0])
            dy = abs(event.y_root - self.explorer_drag_press_root[1])
            if max(dx, dy) < 6:
                return None
            self.explorer_drag_started = True
        return "break"

    def _on_tree_item_drag_release(self, event):
        path = self.explorer_drag_path
        drag_started = self.explorer_drag_started
        self.explorer_drag_path = None
        self.explorer_drag_press_root = None
        self.explorer_drag_started = False
        if not path or not drag_started:
            return None
        target_notebook = self._editor_drop_target_notebook(event.x_root, event.y_root)
        if not target_notebook:
            return None
        self._open_path_in_notebook(path, target_notebook)
        self._set_status(
            f"Opened {path.name} in {'split' if target_notebook == self.split_notebook else 'main'} editor"
        )
        return "break"

    def _show_tree_menu(self, event):
        item_id = self.file_tree.identify_row(event.y)
        if item_id:
            self.file_tree.selection_set(item_id)
            self.file_tree.focus(item_id)
        self.tree_menu.tk_popup(event.x_root, event.y_root)

    def _selected_tree_path(self):
        item_id = self.file_tree.focus()
        if not item_id:
            return self.project_root
        values = self.file_tree.item(item_id, "values")
        if not values:
            return self.project_root
        return Path(values[0])

    def _selected_directory(self):
        path = self._selected_tree_path()
        return path if path.is_dir() else path.parent

    def _copy_to_clipboard(self, value):
        self.root.clipboard_clear()
        self.root.clipboard_append(str(value))
        self.root.update_idletasks()

    def _copy_selected_path(self):
        path = self._selected_tree_path()
        self._copy_to_clipboard(path)
        self._set_status(f"Copied path: {path}")

    def _copy_selected_relative_path(self):
        path = self._selected_tree_path()
        try:
            relative = path.relative_to(self.project_root)
        except ValueError:
            relative = path
        self._copy_to_clipboard(relative)
        self._set_status(f"Copied relative path: {relative}")

    def _copy_selected_name(self):
        path = self._selected_tree_path()
        self._copy_to_clipboard(path.name)
        self._set_status(f"Copied name: {path.name}")

    def _open_selected_in_terminal(self):
        path = self._selected_tree_path()
        target = path if path.is_dir() else path.parent
        self._ensure_panels_visible()
        session = self._active_terminal_session()
        if not session:
            session = self._new_terminal_session()
        session.text.focus_set()
        if self._current_shell_name() == "Git Bash":
            command = f'cd "{self._format_shell_path(target)}"'
        elif self._current_shell_name() == "Command Prompt":
            command = f'cd /d "{target}"'
        else:
            command = f'Set-Location "{target}"'
        session.text.insert(tk.END, "\n")
        self._run_terminal_command(command, session)
        self._set_status(f"Opened in terminal: {target}")

    def _new_file_in_selected_dir(self):
        directory = self._selected_directory()
        name = simpledialog.askstring("New file", "File name:", parent=self.root)
        if not name:
            return
        target = (directory / name).resolve()
        if target.exists():
            messagebox.showerror("File exists", f"{target.name} already exists.")
            return
        try:
            target.write_text("", encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Create file failed", str(exc))
            return
        self._refresh_project()
        self._open_path_in_tab(target)

    def _new_folder_in_selected_dir(self):
        directory = self._selected_directory()
        name = simpledialog.askstring("New folder", "Folder name:", parent=self.root)
        if not name:
            return
        target = (directory / name).resolve()
        if target.exists():
            messagebox.showerror("Folder exists", f"{target.name} already exists.")
            return
        try:
            target.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            messagebox.showerror("Create folder failed", str(exc))
            return
        self._refresh_project()

    def _rename_selected_path(self):
        path = self._selected_tree_path()
        if path == self.project_root:
            return
        new_name = simpledialog.askstring("Rename", "New name:", initialvalue=path.name, parent=self.root)
        if not new_name or new_name == path.name:
            return
        target = path.with_name(new_name)
        if target.exists():
            messagebox.showerror("Rename failed", f"{new_name} already exists.")
            return
        try:
            path.rename(target)
        except OSError as exc:
            messagebox.showerror("Rename failed", str(exc))
            return
        for tab in self.tabs.values():
            if tab.path == path:
                tab.path = target
                tab.document_key = f"path:{target.resolve()}"
                self._update_tab_title(tab)
        self._refresh_project()

    def _delete_selected_path(self):
        path = self._selected_tree_path()
        if path == self.project_root:
            messagebox.showerror("Delete blocked", "Deleting the opened project root is disabled.")
            return

        affected_tabs = [tab for tab in self.tabs.values() if tab.path and (tab.path == path or path in tab.path.parents)]
        if any(tab.modified for tab in affected_tabs):
            confirm = messagebox.askyesno(
                "Unsaved tabs",
                "Some open files inside this path have unsaved changes. Delete anyway and close those tabs?",
                parent=self.root,
            )
            if not confirm:
                return

        confirm = messagebox.askyesno(
            "Delete",
            f"Delete {'folder' if path.is_dir() else 'file'}:\n{path}",
            parent=self.root,
        )
        if not confirm:
            return

        for tab in list(affected_tabs):
            tab.modified = False
            self._close_tab(tab)

        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except OSError as exc:
            messagebox.showerror("Delete failed", str(exc))
            return

        self._refresh_project()
        self._set_status(f"Deleted {path.name}")

    def _create_peer_text_widget(self, source_text, parent):
        peer_name = f"peer{self.peer_counter}"
        self.peer_counter += 1
        peer_path = f"{str(parent)}.{peer_name}"
        source_text.peer_create(peer_path, wrap="none")
        peer = tk.Text.__new__(tk.Text)
        peer.master = parent
        peer.tk = source_text.tk
        peer._w = peer_path
        peer.children = {}
        peer._name = peer_name
        peer._tclCommands = []
        parent.children[peer_name] = peer
        peer.configure(
            bg=EDITOR_BG,
            fg=EDITOR_FG,
            insertbackground=EDITOR_FG,
            font=self.code_font,
            bd=0,
            padx=12,
            pady=10,
            relief=tk.FLAT,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            tabs=("4c",),
            selectbackground="#264f78",
            selectforeground=EDITOR_FG,
        )
        return peer

    def _new_tab(self, content="", path=None, notebook=None, force_duplicate=False, document_key=None, untitled_name=None, peer_source_tab=None):
        if path and not force_duplicate:
            existing = self._tab_for_path(path)
            if existing:
                self._select_tab(existing)
                return existing

        notebook = notebook or self.active_notebook or self.editor_notebook

        frame = tk.Frame(notebook, bg=EDITOR_BG)
        editor_frame = tk.Frame(frame, bg=EDITOR_BG)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        line_nums = tk.Text(
            editor_frame,
            width=5,
            bg=LINE_BG,
            fg=LINE_FG,
            state=tk.DISABLED,
            font=self.line_font,
            bd=0,
            padx=8,
            pady=10,
            relief=tk.FLAT,
            selectbackground=LINE_BG,
            wrap=tk.NONE,
        )
        line_nums.pack(side=tk.LEFT, fill=tk.Y)

        tk.Frame(editor_frame, bg=BORDER, width=1).pack(side=tk.LEFT, fill=tk.Y)

        y_scroll = ttk.Scrollbar(editor_frame, style="Modern.Vertical.TScrollbar")
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, style="Modern.Horizontal.TScrollbar")
        x_scroll.pack(fill=tk.X)

        if peer_source_tab:
            text = self._create_peer_text_widget(peer_source_tab.text, editor_frame)
        else:
            text = tk.Text(
                editor_frame,
                bg=EDITOR_BG,
                fg=EDITOR_FG,
                insertbackground=EDITOR_FG,
                font=self.code_font,
                bd=0,
                padx=12,
                pady=10,
                relief=tk.FLAT,
                wrap=tk.NONE,
                undo=True,
                autoseparators=True,
                maxundo=-1,
                tabs=(f"{self.tab_width_spaces}c",),
                selectbackground="#264f78",
                selectforeground=EDITOR_FG,
            )
        text.pack(fill=tk.BOTH, expand=True)

        if untitled_name is None:
            untitled_name = f"untitled-{self.untitled_counter}.luau"
            self.untitled_counter += 1
        if document_key is None:
            document_key = f"path:{Path(path).resolve()}" if path else f"untitled:{untitled_name}"

        tab = EditorTab(
            frame=frame,
            text=text,
            lines=line_nums,
            y_scroll=y_scroll,
            x_scroll=x_scroll,
            path=Path(path).resolve() if path else None,
            untitled_name=untitled_name,
            document_key=document_key,
            is_peer=bool(peer_source_tab),
        )

        text.configure(yscrollcommand=lambda first, last, current=tab: self._sync_editor_scroll(current, first, last))
        text.configure(xscrollcommand=x_scroll.set)
        y_scroll.config(command=lambda *args, current=tab: self._on_vertical_scroll(current, *args))
        x_scroll.config(command=text.xview)

        for tag, color in (
            ("keyword", "#569cd6"),
            ("builtin", "#4fc1ff"),
            ("string", "#ce9178"),
            ("comment", "#6a9955"),
            ("number", "#b5cea8"),
            ("function_name", "#dcdcaa"),
            ("search", SEARCH_FG),
        ):
            text.tag_configure(tag, foreground=color)
        text.tag_configure("search", background="#3d2f12")
        text.tag_configure("multi_cursor", background=MULTI_CURSOR_BG, foreground=MULTI_CURSOR_FG)
        text.tag_configure("bracket_match", background="#3b82f6", foreground="#ffffff")

        text.bind("<KeyPress>", lambda event, current=tab: self._on_editor_keypress(current, event))
        text.bind("<KeyRelease>", lambda _e, current=tab: self._on_editor_keyrelease(current))
        text.bind("<ButtonRelease-1>", lambda _e, current=tab: self._on_editor_cursor_change(current))
        text.bind("<Button-1>", lambda _e, current=tab: self._clear_multi_cursors(current))
        text.bind("<FocusOut>", lambda _e, current=tab: self._on_editor_focus_out(current))
        text.bind("<MouseWheel>", lambda _e, current=tab: self.root.after_idle(lambda: self._update_line_numbers(current)))
        text.bind("<Return>", lambda event, current=tab: self._auto_indent(current, event))
        text.bind("<BackSpace>", lambda event, current=tab: self._on_editor_backspace(current, event))
        text.bind("<<Modified>>", lambda _e, current=tab: self._on_modified(current))
        text.bind("<Control-space>", lambda _e, current=tab: self._show_completion(current))
        text.bind("<Escape>", lambda _e: self._hide_completion())
        text.bind("<Tab>", lambda event, current=tab: self._on_editor_tab_key(current, event))
        text.bind("<Shift-Tab>", lambda event, current=tab: self._outdent_selection_or_line(current, event))
        text.bind("<Control-c>", lambda event, current=tab: self._on_editor_copy(current, event))
        text.bind("<Control-C>", lambda event, current=tab: self._on_editor_copy(current, event))
        text.bind("<Control-x>", lambda event, current=tab: self._on_editor_cut(current, event))
        text.bind("<Control-X>", lambda event, current=tab: self._on_editor_cut(current, event))
        text.bind("<Control-d>", lambda event, current=tab: self._duplicate_editor_line(current, event))
        text.bind("<Control-D>", lambda event, current=tab: self._duplicate_editor_line(current, event))
        text.bind("<Control-slash>", lambda event, current=tab: self._toggle_line_comment(current, event))
        text.bind("<Control-question>", lambda event, current=tab: self._toggle_line_comment(current, event))
        text.bind("<Control-v>", lambda event, current=tab: self._on_editor_paste(current, event))
        text.bind("<Control-V>", lambda event, current=tab: self._on_editor_paste(current, event))
        text.bind("<Alt-Up>", lambda event, current=tab: self._move_editor_lines(current, -1, event))
        text.bind("<Alt-Down>", lambda event, current=tab: self._move_editor_lines(current, 1, event))
        text.bind("<Control-Alt-Up>", lambda event, current=tab: self._add_multi_cursor(current, -1, event))
        text.bind("<Control-Alt-Down>", lambda event, current=tab: self._add_multi_cursor(current, 1, event))
        text.bind("<Control-Alt-Left>", lambda event, current=tab: self._move_multi_cursors(current, -1, event))
        text.bind("<Control-Alt-Right>", lambda event, current=tab: self._move_multi_cursors(current, 1, event))

        if not peer_source_tab:
            text.insert("1.0", content)
        text.edit_modified(False)
        tab.loaded = True

        self.tabs[str(frame)] = tab
        self.text_to_tab[str(text)] = tab
        self.tab_notebooks[str(frame)] = notebook
        notebook.add(frame, text=self._tab_label(tab))
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        self._select_tab(tab)
        self._render_all_editor_tab_bars()
        return tab

    def _tab_label(self, tab):
        return self._tab_title_text(tab)

    def _tab_for_path(self, path):
        resolved = Path(path).resolve()
        for tab in self.tabs.values():
            if tab.path == resolved:
                return tab
        return None

    def _linked_tabs(self, tab):
        return [current for current in self.tabs.values() if current.document_key == tab.document_key]

    def _sync_linked_tabs(self, source_tab):
        if source_tab.document_key in self.syncing_documents:
            return
        self.syncing_documents.add(source_tab.document_key)
        try:
            for tab in self._linked_tabs(source_tab):
                if tab is source_tab:
                    continue
                tab.modified = source_tab.modified
                tab.text.edit_modified(False)
                self._update_line_numbers(tab)
                self._schedule_highlight(tab)
                self._schedule_diagnostics(tab)
                self._update_tab_title(tab)
        finally:
            self.syncing_documents.discard(source_tab.document_key)

    def _active_tab(self):
        notebook = self.active_notebook
        if notebook:
            selected = notebook.select()
            if selected:
                tab = self.tabs.get(selected)
                if tab:
                    return tab
        for notebook in (self.editor_notebook, self.split_notebook):
            selected = notebook.select()
            if selected:
                tab = self.tabs.get(selected)
                if tab:
                    return tab
        return None

    def _select_tab(self, tab):
        notebook = self.tab_notebooks.get(str(tab.frame), self.editor_notebook)
        self._set_active_notebook(notebook)
        notebook.select(tab.frame)
        self._on_editor_tab_changed()
        self._render_all_editor_tab_bars()
        tab.text.focus_set()

    def _close_active_tab(self):
        tab = self._active_tab()
        if tab:
            self._close_tab(tab)

    def _close_tab(self, tab):
        if not self._prepare_tab_for_close(tab):
            return False

        if tab.highlight_job:
            self.root.after_cancel(tab.highlight_job)
        if tab.diagnostics_job:
            self.root.after_cancel(tab.diagnostics_job)
        if self.completion_tab == tab:
            self._hide_completion()
        notebook = self.tab_notebooks.pop(str(tab.frame), self.editor_notebook)
        notebook.forget(tab.frame)
        self.tabs.pop(str(tab.frame), None)
        self.text_to_tab.pop(str(tab.text), None)
        if self.split_visible and not self.split_notebook.tabs():
            self._hide_split_editor()
        if not self.tabs:
            self._new_tab()
        self._on_editor_tab_changed()
        self._render_all_editor_tab_bars()
        return True

    def _prepare_tab_for_close(self, tab):
        if not tab.modified:
            return True
        if tab.path:
            return self._save_tab(tab)
        answer = messagebox.askyesnocancel(
            "Unsaved tab",
            f"{tab.untitled_name} has not been saved yet. Save it before closing?",
            parent=self.root,
        )
        if answer is None:
            return False
        if answer:
            return self._save_tab(tab)
        return True

    def _notebook_tab_at(self, notebook, x, y):
        try:
            index = notebook.index(f"@{x},{y}")
        except tk.TclError:
            return None, None, notebook
        tabs = notebook.tabs()
        if index >= len(tabs):
            return None, None, notebook
        return index, self.tabs.get(tabs[index]), notebook

    def _tab_close_hit(self, notebook, index, x, y=None):
        return self._notebook_label_close_hit(notebook, index, x, y)

    def _tab_close_hit_with_bbox(self, bbox, x, y=None):
        if not bbox:
            return False
        tab_x, tab_y, width, height = bbox
        if y is not None and not (tab_y <= y <= tab_y + height):
            return False
        x_end = tab_x + width - 2
        x_start = x_end - max(self.notebook_tab_font.measure("x") + 6, 12)
        return x_start <= x <= x_end

    def _on_notebook_button_press(self, event):
        notebook = event.widget
        self.current_notebook_event = notebook
        self._set_active_notebook(notebook)
        index, tab, _notebook = self._notebook_tab_at(notebook, event.x, event.y)
        self.notebook_close_target = None
        self.notebook_close_meta = None
        self.tab_drag_source = None
        self.tab_drag_notebook = None
        self.tab_drag_reordered = False
        if tab and self._tab_close_hit(notebook, index, event.x, event.y):
            self._close_tab(tab)
            return "break"
        if tab:
            self.tab_drag_source = tab
            self.tab_drag_notebook = notebook
        return None

    def _on_notebook_drag_motion(self, event):
        if not self.tab_drag_source or not self.tab_drag_notebook:
            return None
        notebook = self.tab_drag_notebook
        try:
            target_index = notebook.index(f"@{event.x},{event.y}")
        except tk.TclError:
            target_index = None
        if target_index is not None and target_index >= 0:
            current_index = notebook.index(self.tab_drag_source.frame)
            if target_index != current_index:
                notebook.insert(target_index, self.tab_drag_source.frame)
                self.tab_drag_reordered = True
        return None

    def _on_notebook_button_release(self, event):
        notebook = event.widget
        self.current_notebook_event = notebook
        self._set_active_notebook(notebook)
        self.notebook_close_target = None
        self.notebook_close_meta = None
        if self.tab_drag_source:
            release_widget = notebook
            pointer_widget = self.root.winfo_containing(event.x_root, event.y_root)
            while pointer_widget is not None and pointer_widget not in {self.editor_notebook, self.split_notebook}:
                pointer_widget = pointer_widget.master
            if pointer_widget in {self.editor_notebook, self.split_notebook}:
                release_widget = pointer_widget
            if release_widget != self.tab_drag_notebook:
                self._move_tab_to_notebook(self.tab_drag_source, release_widget)
            elif release_widget == self.editor_notebook and event.x > max(release_widget.winfo_width() - 80, 0):
                self._move_tab_to_notebook(self.tab_drag_source, self.split_notebook)
            elif release_widget == self.split_notebook and event.x < 80:
                self._move_tab_to_notebook(self.tab_drag_source, self.editor_notebook)
        self.tab_drag_source = None
        self.tab_drag_notebook = None
        return None

    def _on_notebook_middle_click(self, event):
        notebook = event.widget
        self.current_notebook_event = notebook
        self._set_active_notebook(notebook)
        _index, tab, _notebook = self._notebook_tab_at(notebook, event.x, event.y)
        if tab:
            self._close_tab(tab)
            return "break"
        return None

    def _show_tab_context_menu(self, event):
        notebook = event.widget
        self.current_notebook_event = notebook
        self._set_active_notebook(notebook)
        _index, tab, _notebook = self._notebook_tab_at(notebook, event.x, event.y)
        if not tab:
            return None
        self.context_menu_tab = tab
        try:
            self.tab_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tab_context_menu.grab_release()
        return "break"

    def _close_context_menu_tab(self):
        if self.context_menu_tab:
            self._close_tab(self.context_menu_tab)
        self.context_menu_tab = None

    def _close_other_tabs(self, use_context=True):
        target = self.context_menu_tab if use_context else self._active_tab()
        target = target or self._active_tab()
        if not target:
            return
        for tab in list(self.tabs.values()):
            if tab is target:
                continue
            if not self._close_tab(tab):
                return
        self._select_tab(target)
        self.context_menu_tab = None
        self._set_status("Closed other tabs")

    def _close_all_tabs(self):
        target = self.context_menu_tab or self._active_tab()
        if not target:
            return
        for tab in list(self.tabs.values()):
            if tab is target:
                continue
            if not self._close_tab(tab):
                return
        self._close_tab(target)
        self.context_menu_tab = None
        self._set_status("Closed all tabs")

    def _split_context_menu_tab(self):
        tab = self.context_menu_tab
        if tab:
            self._move_tab_to_notebook(tab, self.split_notebook)
        self.context_menu_tab = None

    def _reveal_context_menu_tab(self):
        tab = self.context_menu_tab
        if not tab or not tab.path:
            return
        self._reveal_path_in_tree(tab.path)
        self.context_menu_tab = None

    def _sync_editor_scroll(self, tab, first, last):
        tab.y_scroll.set(first, last)
        tab.lines.yview_moveto(first)

    def _on_vertical_scroll(self, tab, *args):
        tab.text.yview(*args)
        tab.lines.yview(*args)

    def _update_line_numbers(self, tab):
        line_count = int(tab.text.index("end-1c").split(".")[0])
        numbers = "\n".join(str(i) for i in range(1, line_count + 1))
        tab.lines.config(state=tk.NORMAL)
        tab.lines.delete("1.0", tk.END)
        tab.lines.insert("1.0", numbers)
        tab.lines.config(state=tk.DISABLED)
        first, _last = tab.text.yview()
        tab.lines.yview_moveto(first)

    def _on_editor_keyrelease(self, tab):
        if tab == self._active_tab():
            self._update_cursor(tab)
        self._refresh_multi_cursor_tags(tab)
        self._refresh_bracket_match(tab)
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        if self.completion_popup and tab == self.completion_tab:
            self._update_completion_items(tab)

    def _on_editor_cursor_change(self, tab):
        if tab == self._active_tab():
            self._update_cursor(tab)
        self._refresh_multi_cursor_tags(tab)
        self._refresh_bracket_match(tab)

    def _on_modified(self, tab):
        if not tab.loaded:
            tab.text.edit_modified(False)
            return
        if tab.document_key in self.syncing_documents:
            tab.text.edit_modified(False)
            return
        modified = tab.text.edit_modified()
        if modified and not tab.modified:
            tab.modified = True
            self._update_tab_title(tab)
        if modified:
            self._sync_linked_tabs(tab)
            self._schedule_autosave(tab)
            self._write_recovery_snapshot(tab)
        tab.text.edit_modified(False)

    def _schedule_highlight(self, tab):
        if tab.highlight_job:
            self.root.after_cancel(tab.highlight_job)
        tab.highlight_job = self.root.after(120, lambda current=tab: self._highlight_tab(current))

    def _schedule_diagnostics(self, tab):
        if tab.diagnostics_job:
            self.root.after_cancel(tab.diagnostics_job)
        tab.diagnostics_job = self.root.after(220, lambda current=tab: self._update_diagnostics(current))

    def _highlight_tab(self, tab):
        tab.highlight_job = None
        for tag in ("keyword", "builtin", "string", "comment", "number", "function_name"):
            tab.text.tag_remove(tag, "1.0", tk.END)

        content = tab.text.get("1.0", "end-1c")
        for match in TOKEN_RE.finditer(content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            kind = match.lastgroup
            if kind == "comment":
                tab.text.tag_add("comment", start, end)
            elif kind == "string":
                tab.text.tag_add("string", start, end)
            elif kind == "number":
                tab.text.tag_add("number", start, end)
            elif kind == "word":
                word = match.group(kind)
                if word in KEYWORDS:
                    tab.text.tag_add("keyword", start, end)
                elif word in BUILTINS:
                    tab.text.tag_add("builtin", start, end)

        for func_match in re.finditer(r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)", content):
            start = f"1.0+{func_match.start(1)}c"
            end = f"1.0+{func_match.end(1)}c"
            tab.text.tag_add("function_name", start, end)

    def _update_diagnostics(self, tab):
        tab.diagnostics_job = None
        content = tab.text.get("1.0", "end-1c")
        cleaned = TOKEN_RE.sub(lambda match: match.group("word") if match.lastgroup == "word" else " ", content)
        tokens = re.findall(r"\b(function|then|do|repeat|end|until)\b", cleaned)
        stack = []
        issues = []
        for token in tokens:
            if token in {"function", "then", "do", "repeat"}:
                stack.append(token)
            elif token == "end":
                if stack and stack[-1] in {"function", "then", "do"}:
                    stack.pop()
                else:
                    issues.append("unexpected end")
            elif token == "until":
                if stack and stack[-1] == "repeat":
                    stack.pop()
                else:
                    issues.append("unexpected until")
        if stack:
            issues.append(f"possible unclosed block: {stack[-1]}")

        message = "Structure looks balanced" if not issues else f"Syntax hints: {', '.join(dict.fromkeys(issues))}"
        tab.diagnostics = message
        if tab == self._active_tab():
            self.diagnostics_label.config(
                text=message,
                fg=ERROR_FG if issues else LINE_FG,
            )
        self._refresh_outline(tab)

    def _refresh_outline(self, tab=None):
        tab = tab or self._active_tab()
        self.outline_list.delete(0, tk.END)
        if not tab:
            self.outline_status.config(text="")
            return
        content = tab.text.get("1.0", "end-1c").splitlines()
        items = []
        patterns = [
            re.compile(r"^\s*(?:local\s+)?function\s+([A-Za-z_][A-Za-z0-9_\.]*)"),
            re.compile(r"^\s*(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*function\b"),
        ]
        for line_no, line in enumerate(content, 1):
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    items.append((line_no, match.group(1)))
                    break
        self.outline_items = items
        for line_no, name in items:
            self.outline_list.insert(tk.END, f"{name}    :{line_no}")
        self.outline_status.config(text=f"{len(items)} symbols")

    def _jump_to_outline_item(self, _event=None):
        tab = self._active_tab()
        if not tab:
            return "break"
        selection = self.outline_list.curselection()
        if not selection:
            return "break"
        line_no, _name = self.outline_items[selection[0]]
        tab.text.mark_set(tk.INSERT, f"{line_no}.0")
        tab.text.see(f"{line_no}.0")
        tab.text.focus_set()
        self._update_cursor(tab)
        return "break"

    def _update_tab_title(self, tab):
        notebook = self.tab_notebooks.get(str(tab.frame), self.editor_notebook)
        notebook.tab(tab.frame, text=self._tab_label(tab))
        self._render_editor_tab_bar(notebook)
        if tab == self._active_tab():
            self._refresh_title()

    def _refresh_title(self):
        tab = self._active_tab()
        if not tab:
            self.root.title(APP_NAME)
            self.breadcrumb_label.config(text="")
            return
        name = tab.path.name if tab.path else tab.untitled_name
        prefix = "* " if tab.modified else ""
        breadcrumb = str(tab.path.parent) if tab.path else str(self.project_root)
        self.breadcrumb_label.config(text=breadcrumb)
        self.root.title(f"{APP_NAME} - {prefix}{name}")

    def _update_cursor(self, tab):
        line, column = tab.text.index(tk.INSERT).split(".")
        self.cursor_label.config(text=f"Ln {line}, Col {int(column) + 1}")

    def _selection_range(self, text):
        try:
            return text.index("sel.first"), text.index("sel.last")
        except tk.TclError:
            return None

    def _line_leading_spaces(self, line_text):
        return len(line_text) - len(line_text.lstrip(" "))

    def _index_key(self, index):
        line, column = index.split(".")
        return int(line), int(column)

    def _ordered_cursors(self, tab):
        current_insert = tab.text.index(tk.INSERT)
        ordered = []
        seen = set()
        for pos in tab.multi_cursors:
            current = tab.text.index(pos)
            if current != current_insert and current not in seen:
                ordered.append(current)
                seen.add(current)
        ordered.sort(key=self._index_key)
        return ordered

    def _refresh_multi_cursor_tags(self, tab):
        tab.text.tag_remove("multi_cursor", "1.0", tk.END)
        tab.multi_cursors = self._ordered_cursors(tab)
        for pos in tab.multi_cursors:
            next_pos = tab.text.index(f"{pos}+1c")
            if tab.text.compare(next_pos, ">", "end-1c"):
                if tab.text.compare(pos, ">", "1.0"):
                    tab.text.tag_add("multi_cursor", f"{pos}-1c", pos)
            else:
                tab.text.tag_add("multi_cursor", pos, next_pos)

    def _clear_multi_cursors(self, tab):
        if tab.multi_cursors:
            tab.multi_cursors.clear()
            self._refresh_multi_cursor_tags(tab)
        return None

    def _cursor_positions(self, tab):
        return [tab.text.index(tk.INSERT)] + self._ordered_cursors(tab)

    def _replace_multi_cursors(self, tab, positions, primary_index=None):
        normalized = []
        seen = set()
        for pos in positions:
            current = tab.text.index(pos)
            if current not in seen:
                normalized.append(current)
                seen.add(current)
        normalized.sort(key=self._index_key)
        if not normalized:
            normalized = [tab.text.index(tk.INSERT)]
        primary_index = tab.text.index(primary_index or normalized[0])
        tab.text.mark_set(tk.INSERT, primary_index)
        tab.multi_cursors = [pos for pos in normalized if pos != primary_index]
        self._refresh_multi_cursor_tags(tab)
        tab.text.see(primary_index)

    def _line_column_index(self, tab, line_no, column):
        if line_no < 1:
            line_no = 1
        line_text = tab.text.get(f"{line_no}.0", f"{line_no}.end")
        return f"{line_no}.{min(column, len(line_text))}"

    def _selected_line_range(self, tab):
        selection = self._selection_range(tab.text)
        if selection:
            start_line = int(selection[0].split(".")[0])
            end_index = tab.text.index(f"{selection[1]}-1c") if selection[0] != selection[1] else selection[1]
            end_line = int(end_index.split(".")[0])
            return start_line, end_line
        current_line = int(tab.text.index(tk.INSERT).split(".")[0])
        return current_line, current_line

    def _indent_selection_or_line(self, tab):
        start_line, end_line = self._selected_line_range(tab)
        for line_no in range(start_line, end_line + 1):
            tab.text.insert(f"{line_no}.0", " " * 4)
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _outdent_selection_or_line(self, tab, _event=None):
        start_line, end_line = self._selected_line_range(tab)
        for line_no in range(start_line, end_line + 1):
            line_start = f"{line_no}.0"
            leading = tab.text.get(line_start, f"{line_no}.0+4c")
            remove = min(self._line_leading_spaces(leading), 4)
            if remove:
                tab.text.delete(line_start, f"{line_no}.0+{remove}c")
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _wrap_selection(self, tab, opener, closer):
        selection = self._selection_range(tab.text)
        if not selection:
            return False
        selected = tab.text.get(selection[0], selection[1])
        tab.text.delete(selection[0], selection[1])
        tab.text.insert(selection[0], f"{opener}{selected}{closer}")
        return True

    def _insert_at_cursors(self, tab, values, cursor_shift=0):
        positions = self._cursor_positions(tab)
        if isinstance(values, str):
            values = [values] * len(positions)
        edits = list(zip(positions, values))
        for pos, value in sorted(edits, key=lambda item: self._index_key(item[0]), reverse=True):
            tab.text.insert(pos, value)
        updated = [tab.text.index(f"{pos}+{len(value) + cursor_shift}c") for pos, value in edits]
        self._replace_multi_cursors(tab, updated, primary_index=updated[0])
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _delete_before_cursors(self, tab):
        positions = self._cursor_positions(tab)
        updated = []
        for pos in sorted(positions, key=self._index_key, reverse=True):
            if tab.text.compare(pos, "<=", "1.0"):
                updated.append(pos)
                continue
            prev = tab.text.index(f"{pos}-1c")
            prev_char = tab.text.get(prev, pos)
            next_char = tab.text.get(pos, f"{pos}+1c")
            if prev_char in AUTO_PAIRS and AUTO_PAIRS[prev_char] == next_char:
                tab.text.delete(prev, f"{pos}+1c")
                updated.append(prev)
            else:
                tab.text.delete(prev, pos)
                updated.append(prev)
        updated.reverse()
        self._replace_multi_cursors(tab, updated, primary_index=updated[0] if updated else "1.0")
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _line_copy_payload(self, tab):
        line_no = int(tab.text.index(tk.INSERT).split(".")[0])
        line_text = tab.text.get(f"{line_no}.0", f"{line_no}.end")
        return line_text + "\n"

    def _reindent_paste_payload(self, tab, payload):
        payload = payload.replace("\r\n", "\n").replace("\r", "\n")
        if "\n" not in payload:
            return payload
        lines = payload.split("\n")
        base_indent = self._line_leading_spaces(tab.text.get("insert linestart", "insert"))
        tail = lines[1:]
        meaningful = [line for line in tail if line.strip()]
        common_indent = min((self._line_leading_spaces(line) for line in meaningful), default=0)
        rebuilt = [lines[0]]
        for line in tail:
            if not line:
                rebuilt.append("")
                continue
            trimmed = line[common_indent:] if len(line) >= common_indent else line.lstrip(" ")
            rebuilt.append((" " * base_indent) + trimmed)
        return "\n".join(rebuilt)

    def _editor_line_text(self, tab, line_no):
        return tab.text.get(f"{line_no}.0", f"{line_no}.end")

    def _duplicate_editor_line(self, tab, _event=None):
        start_line, end_line = self._selected_line_range(tab)
        block = "\n".join(self._editor_line_text(tab, line_no) for line_no in range(start_line, end_line + 1))
        insert_at = f"{end_line}.end"
        tab.text.insert(insert_at, "\n" + block)
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _delete_editor_line(self, tab, _event=None):
        start_line, end_line = self._selected_line_range(tab)
        start_index = f"{start_line}.0"
        end_index = f"{end_line + 1}.0" if tab.text.compare(f"{end_line}.end", "<", "end-1c") else f"{end_line}.end"
        tab.text.delete(start_index, end_index)
        if tab.text.get("1.0", "end-1c") == "":
            tab.text.insert("1.0", "")
        tab.text.mark_set(tk.INSERT, start_index)
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _move_editor_lines(self, tab, direction, _event=None):
        start_line, end_line = self._selected_line_range(tab)
        last_line = int(tab.text.index("end-1c").split(".")[0])
        if direction < 0 and start_line <= 1:
            return "break"
        if direction > 0 and end_line >= last_line:
            return "break"
        block = "\n".join(self._editor_line_text(tab, line_no) for line_no in range(start_line, end_line + 1))
        if direction < 0:
            target_line = start_line - 1
            target_text = self._editor_line_text(tab, target_line)
            tab.text.delete(f"{target_line}.0", f"{end_line + 1}.0")
            tab.text.insert(f"{target_line}.0", block + "\n" + target_text + "\n")
            new_start = target_line
        else:
            target_line = end_line + 1
            target_text = self._editor_line_text(tab, target_line)
            after_target = f"{target_line + 1}.0" if target_line < last_line else f"{target_line}.end"
            tab.text.delete(f"{start_line}.0", after_target)
            tab.text.insert(f"{start_line}.0", target_text + "\n" + block + ("\n" if target_line < last_line else ""))
            new_start = start_line + 1
        tab.text.mark_set(tk.INSERT, f"{new_start}.0")
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _toggle_line_comment(self, tab, _event=None):
        start_line, end_line = self._selected_line_range(tab)
        lines = [self._editor_line_text(tab, line_no) for line_no in range(start_line, end_line + 1)]
        non_empty = [line for line in lines if line.strip()]
        if not non_empty:
            return "break"
        uncomment = all(re.match(r"^\s*--", line) for line in non_empty)
        for offset, line_no in enumerate(range(start_line, end_line + 1)):
            line = lines[offset]
            if uncomment:
                updated = re.sub(r"^(\s*)--\s?", r"\1", line, count=1)
            else:
                indent = len(line) - len(line.lstrip(" "))
                updated = (" " * indent) + "-- " + line[indent:]
            tab.text.delete(f"{line_no}.0", f"{line_no}.end")
            tab.text.insert(f"{line_no}.0", updated)
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _matching_bracket_index(self, tab, index):
        pairs = {"(": ")", "{": "}", "[": "]", ")": "(", "}": "{", "]": "["}
        char = tab.text.get(index, f"{index}+1c")
        if char not in pairs:
            return None
        if char in "([{":
            depth = 0
            cursor = index
            while tab.text.compare(cursor, "<", "end-1c"):
                current = tab.text.get(cursor, f"{cursor}+1c")
                if current == char:
                    depth += 1
                elif current == pairs[char]:
                    depth -= 1
                    if depth == 0:
                        return cursor
                cursor = tab.text.index(f"{cursor}+1c")
        else:
            depth = 0
            cursor = index
            while tab.text.compare(cursor, ">=", "1.0"):
                current = tab.text.get(cursor, f"{cursor}+1c")
                if current == char:
                    depth += 1
                elif current == pairs[char]:
                    depth -= 1
                    if depth == 0:
                        return cursor
                if tab.text.compare(cursor, "==", "1.0"):
                    break
                cursor = tab.text.index(f"{cursor}-1c")
        return None

    def _refresh_bracket_match(self, tab):
        tab.text.tag_remove("bracket_match", "1.0", tk.END)
        positions = []
        insert_pos = tab.text.index(tk.INSERT)
        if tab.text.compare(insert_pos, ">", "1.0"):
            positions.append(tab.text.index(f"{insert_pos}-1c"))
        positions.append(insert_pos)
        for pos in positions:
            char = tab.text.get(pos, f"{pos}+1c")
            if char not in "(){}[]":
                continue
            match = self._matching_bracket_index(tab, pos)
            if match:
                tab.text.tag_add("bracket_match", pos, f"{pos}+1c")
                tab.text.tag_add("bracket_match", match, f"{match}+1c")
            return

    def _on_editor_copy(self, tab, _event=None):
        selection = self._selection_range(tab.text)
        if selection:
            payload = tab.text.get(selection[0], selection[1])
            self.editor_clipboard_is_line = False
        else:
            payload = self._line_copy_payload(tab)
            self.editor_clipboard_is_line = True
        self.editor_clipboard_value = payload
        self.root.clipboard_clear()
        self.root.clipboard_append(payload)
        self.root.update_idletasks()
        return "break"

    def _on_editor_cut(self, tab, _event=None):
        selection = self._selection_range(tab.text)
        if selection:
            payload = tab.text.get(selection[0], selection[1])
            self.editor_clipboard_is_line = False
            self.editor_clipboard_value = payload
            self.root.clipboard_clear()
            self.root.clipboard_append(payload)
            self.root.update_idletasks()
            tab.text.delete(selection[0], selection[1])
        else:
            payload = self._line_copy_payload(tab)
            self.editor_clipboard_is_line = True
            self.editor_clipboard_value = payload
            self.root.clipboard_clear()
            self.root.clipboard_append(payload)
            self.root.update_idletasks()
            self._delete_editor_line(tab)
            return "break"
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        return "break"

    def _on_editor_paste(self, tab, _event=None):
        try:
            payload = self.root.clipboard_get()
        except tk.TclError:
            return "break"
        payload = self._reindent_paste_payload(tab, payload)
        selection = self._selection_range(tab.text)
        if self.editor_clipboard_is_line and payload == self.editor_clipboard_value and not selection:
            line_no = int(tab.text.index(tk.INSERT).split(".")[0])
            insert_at = f"{line_no}.end"
            tab.text.insert(insert_at, f"\n{payload.rstrip(chr(10))}")
            self._update_line_numbers(tab)
            self._schedule_highlight(tab)
            self._schedule_diagnostics(tab)
            return "break"
        if selection:
            tab.text.delete(selection[0], selection[1])
            tab.text.insert(selection[0], payload)
            self._update_line_numbers(tab)
            self._schedule_highlight(tab)
            self._schedule_diagnostics(tab)
            return "break"
        if tab.multi_cursors:
            return self._insert_at_cursors(tab, payload)
        return None

    def _on_editor_keypress(self, tab, event):
        if event.state & 0x4:
            return None
        char = event.char
        if not char or char in {"\r", "\t", "\x08"}:
            return None
        if char in AUTO_PAIRS:
            closer = AUTO_PAIRS[char]
            if self._wrap_selection(tab, char, closer):
                self._update_line_numbers(tab)
                self._schedule_highlight(tab)
                self._schedule_diagnostics(tab)
                return "break"
            if tab.multi_cursors:
                return self._insert_at_cursors(tab, char + closer, cursor_shift=-1)
            next_char = tab.text.get("insert", "insert+1c")
            if char in {'"', "'"} and next_char == char:
                tab.text.mark_set(tk.INSERT, "insert+1c")
                return "break"
            tab.text.insert("insert", char + closer)
            tab.text.mark_set(tk.INSERT, "insert-1c")
            return "break"
        if char in CLOSING_CHARS:
            if tab.multi_cursors:
                moved = []
                for pos in self._cursor_positions(tab):
                    next_char = tab.text.get(pos, f"{pos}+1c")
                    moved.append(tab.text.index(f"{pos}+1c") if next_char == char else pos)
                self._replace_multi_cursors(tab, moved, primary_index=moved[0])
                return "break"
            if tab.text.get("insert", "insert+1c") == char:
                tab.text.mark_set(tk.INSERT, "insert+1c")
                return "break"
        if tab.multi_cursors:
            return self._insert_at_cursors(tab, char)
        return None

    def _on_editor_backspace(self, tab, _event=None):
        selection = self._selection_range(tab.text)
        if selection:
            tab.text.delete(selection[0], selection[1])
            self._update_line_numbers(tab)
            self._schedule_highlight(tab)
            self._schedule_diagnostics(tab)
            return "break"
        if tab.multi_cursors:
            return self._delete_before_cursors(tab)
        if tab.text.compare("insert", "<=", "1.0"):
            return "break"
        prev = tab.text.get("insert-1c", "insert")
        curr = tab.text.get("insert", "insert+1c")
        if prev in AUTO_PAIRS and AUTO_PAIRS[prev] == curr:
            tab.text.delete("insert-1c", "insert+1c")
            self._update_line_numbers(tab)
            self._schedule_highlight(tab)
            self._schedule_diagnostics(tab)
            return "break"
        return None

    def _add_multi_cursor(self, tab, direction, _event=None):
        positions = self._cursor_positions(tab)
        anchor = positions[0] if direction < 0 else positions[-1]
        line_no, column = map(int, anchor.split("."))
        target_line = line_no + direction
        if target_line < 1:
            return "break"
        try:
            tab.text.get(f"{target_line}.0", f"{target_line}.end")
        except tk.TclError:
            return "break"
        target = self._line_column_index(tab, target_line, column)
        self._replace_multi_cursors(tab, positions + [target], primary_index=tab.text.index(tk.INSERT))
        self._set_status(f"{1 + len(tab.multi_cursors)} cursors active")
        return "break"

    def _move_multi_cursors(self, tab, delta, _event=None):
        positions = []
        for pos in self._cursor_positions(tab):
            target = tab.text.index(f"{pos}{'+' if delta >= 0 else ''}{delta}c")
            if tab.text.compare(target, "<", "1.0"):
                target = "1.0"
            if tab.text.compare(target, ">", "end-1c"):
                target = "end-1c"
            positions.append(target)
        self._replace_multi_cursors(tab, positions, primary_index=positions[0])
        return "break"

    def _on_editor_tab_changed(self, _event=None):
        if _event and hasattr(_event, "widget"):
            self._set_active_notebook(_event.widget)
        tab = self._active_tab()
        if not tab:
            self._render_all_editor_tab_bars()
            return
        self._hide_completion()
        self._refresh_title()
        self._update_cursor(tab)
        self._update_line_numbers(tab)
        self._refresh_multi_cursor_tags(tab)
        self._refresh_bracket_match(tab)
        self._render_all_editor_tab_bars()
        self.diagnostics_label.config(
            text=tab.diagnostics,
            fg=ERROR_FG if tab.diagnostics.startswith("Syntax hints:") else LINE_FG,
        )
        self._refresh_outline(tab)

    def _auto_indent(self, tab, _event):
        positions = self._cursor_positions(tab)
        inserts = []
        new_primary = None
        move_between = False
        for pos in positions:
            line_no = int(pos.split(".")[0])
            line = tab.text.get(f"{pos} linestart", pos)
            stripped = line.strip()
            indent = self._line_leading_spaces(line)
            next_char = tab.text.get(pos, f"{pos}+1c")
            increase = (
                stripped.endswith(("then", "do", "repeat"))
                or stripped.endswith(("(", "{", "["))
                or bool(re.search(r"\bfunction\b", stripped))
            )
            inner_indent = indent + 4 if increase else indent
            if next_char in ")]}":
                inserts.append("\n" + (" " * inner_indent) + "\n" + (" " * indent))
                move_between = True
                candidate = f"{line_no + 1}.{inner_indent}"
            else:
                inserts.append("\n" + (" " * inner_indent))
                candidate = f"{line_no + 1}.{inner_indent}"
            if new_primary is None:
                new_primary = candidate
        self._insert_at_cursors(tab, inserts)
        if move_between and new_primary:
            tab.text.mark_set(tk.INSERT, new_primary)
            self._refresh_multi_cursor_tags(tab)
        elif new_primary:
            tab.text.mark_set(tk.INSERT, new_primary)
            self._refresh_multi_cursor_tags(tab)
        return "break"

    def _set_status(self, text):
        self.status_label.config(text=text)
        self._log_info("%s", text)

    def _theme_presets(self):
        return {
            "Midnight": {"status_bg": "#0b6aa2", "toolbar_bg": ACTIVITY_BG, "title_bg": PANEL_BG},
            "Slate": {"status_bg": "#334155", "toolbar_bg": "#293241", "title_bg": "#202734"},
            "Forest": {"status_bg": "#166534", "toolbar_bg": "#1f3d2f", "title_bg": "#173126"},
        }

    def _apply_theme_preset(self, theme_name=None):
        self.current_theme_name = theme_name or self.current_theme_name
        palette = self._theme_presets().get(self.current_theme_name, self._theme_presets()["Midnight"])
        try:
            self.titlebar_frame.config(bg=palette["title_bg"])
            self.toolbar_frame.config(bg=palette["toolbar_bg"])
            self.statusbar_frame.config(bg=palette["status_bg"])
            self.status_label.config(bg=palette["status_bg"])
            self.project_label.config(bg=palette["status_bg"])
            self.cursor_label.config(bg=palette["status_bg"])
        except Exception:
            self._log_exception("Failed to apply theme preset %s", self.current_theme_name)

    def _apply_tab_width(self):
        tab_setting = (f"{self.tab_width_spaces}c",)
        for tab in self.tabs.values():
            try:
                tab.text.config(tabs=tab_setting)
            except Exception:
                self._log_exception("Failed to apply tab width")

    def _schedule_autosave(self, tab):
        tab_id = str(tab.frame)
        job = self.autosave_job_by_tab.pop(tab_id, None)
        if job:
            try:
                self.root.after_cancel(job)
            except tk.TclError:
                pass
        if self.autosave_mode != "delay" or not tab.path or not tab.modified:
            return
        self.autosave_job_by_tab[tab_id] = self.root.after(self.autosave_delay_ms, lambda current=tab: self._autosave_tab(current))

    def _autosave_tab(self, tab):
        self.autosave_job_by_tab.pop(str(tab.frame), None)
        if self.autosave_mode == "off":
            return
        if tab.path and tab.modified:
            self._save_tab(tab)
        elif tab.modified:
            self._write_recovery_snapshot(tab)

    def _on_editor_focus_out(self, tab):
        if self.autosave_mode == "focus" and tab.path and tab.modified:
            self._autosave_tab(tab)
        elif tab.modified:
            self._write_recovery_snapshot(tab)
        return None

    def _write_recovery_snapshot(self, tab):
        try:
            self.backup_root.mkdir(parents=True, exist_ok=True)
            name = (tab.path.name if tab.path else tab.untitled_name).replace(os.sep, "_")
            backup_path = self.backup_root / f"{tab.document_key.replace(':', '_').replace(os.sep, '_')}_{name}.bak"
            backup_path.write_text(tab.text.get("1.0", "end-1c"), encoding="utf-8")
        except OSError:
            self._log_exception("Failed to write recovery snapshot")

    def _clear_recovery_snapshot(self, tab):
        try:
            prefix = tab.document_key.replace(":", "_").replace(os.sep, "_")
            for backup_path in self.backup_root.glob(f"{prefix}_*.bak"):
                backup_path.unlink(missing_ok=True)
        except OSError:
            self._log_exception("Failed to clear recovery snapshot")

    def _show_recent_projects(self):
        items = []
        for path_text in self.recent_projects:
            path = Path(path_text)
            if path.exists():
                items.append((f"{path.name}  [{path}]", path))
        self._show_picker("Recent Projects", items, lambda path: self._set_project_root(path), "Recent Projects")

    def _show_settings(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus_set()
            return
        window = tk.Toplevel(self.root)
        window.title("Lume Settings")
        window.transient(self.root)
        window.configure(bg=PANEL_BG)
        window.geometry("540x420")
        self.settings_window = window
        window.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, "settings_window", None), window.destroy()))

        shell_var = tk.StringVar(value=self.shell_var.get())
        code_size_var = tk.IntVar(value=int(self.code_font.cget("size")))
        term_size_var = tk.IntVar(value=int(self.term_font.cget("size")))
        tab_width_var = tk.IntVar(value=self.tab_width_spaces)
        autosave_var = tk.StringVar(value=self.autosave_mode)
        autosave_delay_var = tk.IntVar(value=max(500, self.autosave_delay_ms))
        luau_var = tk.StringVar(value=self.luau_path_var.get())
        theme_var = tk.StringVar(value=self.current_theme_name)

        fields = tk.Frame(window, bg=PANEL_BG)
        fields.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        def row(label_text, widget, row_no):
            tk.Label(fields, text=label_text, bg=PANEL_BG, fg=EDITOR_FG, anchor="w", font=("Segoe UI", 9)).grid(row=row_no, column=0, sticky="w", pady=8, padx=(0, 12))
            widget.grid(row=row_no, column=1, sticky="ew", pady=8)

        fields.columnconfigure(1, weight=1)
        row("Default shell", ttk.Combobox(fields, textvariable=shell_var, values=self.shell_options, state="readonly", style="Modern.TCombobox"), 0)
        row("Code font size", tk.Spinbox(fields, from_=8, to=24, textvariable=code_size_var, bg="#111827", fg=EDITOR_FG, relief=tk.FLAT), 1)
        row("Terminal font size", tk.Spinbox(fields, from_=8, to=24, textvariable=term_size_var, bg="#111827", fg=EDITOR_FG, relief=tk.FLAT), 2)
        row("Tab width", tk.Spinbox(fields, from_=2, to=8, textvariable=tab_width_var, bg="#111827", fg=EDITOR_FG, relief=tk.FLAT), 3)
        row("Auto-save", ttk.Combobox(fields, textvariable=autosave_var, values=["off", "focus", "delay"], state="readonly", style="Modern.TCombobox"), 4)
        row("Auto-save delay (ms)", tk.Spinbox(fields, from_=500, to=10000, increment=250, textvariable=autosave_delay_var, bg="#111827", fg=EDITOR_FG, relief=tk.FLAT), 5)
        row("Theme preset", ttk.Combobox(fields, textvariable=theme_var, values=list(self._theme_presets().keys()), state="readonly", style="Modern.TCombobox"), 6)
        luau_entry = tk.Entry(fields, textvariable=luau_var, bg="#111827", fg=EDITOR_FG, insertbackground=EDITOR_FG, relief=tk.FLAT)
        row("Luau path", luau_entry, 7)

        button_row = tk.Frame(window, bg=PANEL_BG)
        button_row.pack(fill=tk.X, padx=16, pady=(0, 16))

        def browse_luau():
            selected = filedialog.askopenfilename(initialdir=str(Path(luau_var.get()).parent) if luau_var.get() else str(self.project_root), filetypes=[("Executables", "*.exe"), ("All files", "*.*")])
            if selected:
                luau_var.set(selected)

        def apply_settings():
            self.shell_var.set(shell_var.get())
            self.code_font.configure(size=int(code_size_var.get()))
            self.term_font.configure(size=int(term_size_var.get()))
            self.line_font.configure(size=max(int(code_size_var.get()) - 1, 8))
            self.tab_width_spaces = int(tab_width_var.get())
            self.autosave_mode = autosave_var.get()
            self.autosave_delay_ms = int(autosave_delay_var.get())
            self.luau_path_var.set(luau_var.get().strip())
            self.current_theme_name = theme_var.get()
            self._apply_tab_width()
            self._apply_theme_preset(self.current_theme_name)
            self._save_state()
            self._set_status("Settings applied")

        self._mini_toolbar_button(button_row, "Browse luau.exe", browse_luau).pack(side=tk.LEFT, padx=4)
        self._mini_toolbar_button(button_row, "Apply", apply_settings).pack(side=tk.RIGHT, padx=4)
        self._mini_toolbar_button(button_row, "Close", lambda: (setattr(self, "settings_window", None), window.destroy())).pack(side=tk.RIGHT, padx=4)

    def _check_for_updates(self):
        messagebox.showinfo(
            "Updates",
            f"{APP_NAME} {APP_VERSION}\n\nUpdate strategy: manual check.\nVisit your release page or installer source to publish newer versions.",
            parent=self.root,
        )

    def _clear_output(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.config(state=tk.DISABLED)

    def _write_output(self, text, tag=""):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text, tag if tag else ())
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)

    def _show_find_panel(self, with_replace=False):
        self.find_panel.pack(fill=tk.X, before=self.editor_content_pane)
        self.find_panel_visible = True
        self.find_match_index = None
        if with_replace:
            self.replace_entry.focus_set()
            self.replace_entry.icursor(tk.END)
        else:
            self.find_entry.focus_set()
            self.find_entry.selection_range(0, tk.END)
        return "break"

    def _hide_find_panel(self):
        if self.find_panel_visible:
            self.find_panel.pack_forget()
            self.find_panel_visible = False
            self.find_match_index = None
        tab = self._active_tab()
        if tab:
            tab.text.tag_remove("search", "1.0", tk.END)
            tab.text.focus_set()

    def _highlight_find_match(self, tab, start, term):
        tab.text.tag_remove("search", "1.0", tk.END)
        end = f"{start}+{len(term)}c"
        tab.text.tag_add("search", start, end)
        tab.text.mark_set(tk.INSERT, end)
        tab.text.see(start)
        tab.text.focus_set()
        self.find_match_index = start

    def _find_term(self, reverse=False):
        tab = self._active_tab()
        if not tab:
            return None, None
        term = self.find_var.get()
        if not term:
            self._set_status("Find text is empty")
            return None, None
        start_index = self.find_match_index or tab.text.index(tk.INSERT)
        if reverse:
            start = tab.text.search(term, start_index, stopindex="1.0", backwards=True, nocase=True)
            if not start:
                start = tab.text.search(term, tk.END, stopindex="1.0", backwards=True, nocase=True)
        else:
            probe = tab.text.index(f"{start_index}+1c") if self.find_match_index else start_index
            start = tab.text.search(term, probe, stopindex=tk.END, nocase=True)
            if not start:
                start = tab.text.search(term, "1.0", stopindex=tk.END, nocase=True)
        return tab, start

    def _find_next(self):
        tab, start = self._find_term(reverse=False)
        term = self.find_var.get()
        if not tab or not start:
            self._set_status(f"No matches for {term!r}")
            return "break"
        self._highlight_find_match(tab, start, term)
        self._set_status(f"Found {term!r}")
        return "break"

    def _find_previous(self):
        tab, start = self._find_term(reverse=True)
        term = self.find_var.get()
        if not tab or not start:
            self._set_status(f"No matches for {term!r}")
            return "break"
        self._highlight_find_match(tab, start, term)
        self._set_status(f"Found {term!r}")
        return "break"

    def _replace_current_match(self):
        tab = self._active_tab()
        term = self.find_var.get()
        if not tab or not term:
            return "break"
        if self.find_match_index is None:
            self._find_next()
        if self.find_match_index is None:
            return "break"
        start = self.find_match_index
        end = f"{start}+{len(term)}c"
        if tab.text.get(start, end) == term:
            tab.text.delete(start, end)
            tab.text.insert(start, self.replace_var.get())
            self.find_match_index = None
            self._update_line_numbers(tab)
            self._schedule_highlight(tab)
            self._schedule_diagnostics(tab)
        return self._find_next()

    def _replace_all_matches(self):
        tab = self._active_tab()
        term = self.find_var.get()
        replacement = self.replace_var.get()
        if not tab or not term:
            return "break"
        content = tab.text.get("1.0", "end-1c")
        count = content.lower().count(term.lower())
        if not count:
            self._set_status(f"No matches for {term!r}")
            return "break"
        updated = re.sub(re.escape(term), replacement, content, flags=re.IGNORECASE)
        tab.text.delete("1.0", tk.END)
        tab.text.insert("1.0", updated)
        self.find_match_index = None
        self._update_line_numbers(tab)
        self._schedule_highlight(tab)
        self._schedule_diagnostics(tab)
        self._set_status(f"Replaced {count} matches")
        return "break"

    def _find_in_active_tab(self):
        return self._show_find_panel(with_replace=False)

    def _project_file_index(self):
        files = []
        for path in sorted(self.project_root.rglob("*")):
            if any(part in {"__pycache__", ".git"} for part in path.parts):
                continue
            if path.is_file():
                files.append(path)
        return files

    def _show_picker(self, title, items, on_select, prompt_text):
        if self.palette_window and self.palette_window.winfo_exists():
            self.palette_window.destroy()

        self.palette_items = items
        self.palette_select_callback = on_select
        self.palette_window = tk.Toplevel(self.root)
        self.palette_window.title(title)
        self.palette_window.transient(self.root)
        self.palette_window.configure(bg=PANEL_BG)
        self.palette_window.geometry("760x420")
        self.palette_window.minsize(520, 300)

        tk.Label(self.palette_window, text=prompt_text, bg=PANEL_BG, fg="#9ccfd8", font=("Segoe UI", 9, "bold")).pack(fill=tk.X, padx=12, pady=(12, 6))
        self.palette_entry = tk.Entry(
            self.palette_window,
            bg="#111827",
            fg=EDITOR_FG,
            insertbackground=EDITOR_FG,
            relief=tk.FLAT,
            font=("Cascadia Code", 11),
        )
        self.palette_entry.pack(fill=tk.X, padx=12, ipady=7)
        self.palette_entry.bind("<KeyRelease>", self._filter_palette_items)
        self.palette_entry.bind("<Return>", self._activate_palette_selection)
        self.palette_entry.bind("<Down>", self._palette_focus_list)
        self.palette_entry.bind("<Escape>", lambda _e: self._close_palette())

        list_frame = tk.Frame(self.palette_window, bg=PANEL_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        list_scroll = ttk.Scrollbar(list_frame, style="Modern.Vertical.TScrollbar")
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.palette_listbox = tk.Listbox(
            list_frame,
            bg="#0f172a",
            fg=EDITOR_FG,
            relief=tk.FLAT,
            borderwidth=0,
            selectbackground="#1d4ed8",
            selectforeground="#ffffff",
            font=("Cascadia Code", 10),
            yscrollcommand=list_scroll.set,
        )
        self.palette_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.palette_listbox.yview)
        self.palette_listbox.bind("<Double-Button-1>", self._activate_palette_selection)
        self.palette_listbox.bind("<Return>", self._activate_palette_selection)
        self.palette_listbox.bind("<Escape>", lambda _e: self._close_palette())

        self._refill_palette_list(items)
        self.palette_entry.focus_set()

    def _refill_palette_list(self, items):
        self.palette_listbox.delete(0, tk.END)
        for label, _payload in items:
            self.palette_listbox.insert(tk.END, label)
        if items:
            self.palette_listbox.selection_set(0)

    def _filter_palette_items(self, _event=None):
        query = self.palette_entry.get().strip().lower()
        if not query:
            filtered = self.palette_items
        else:
            filtered = [item for item in self.palette_items if query in item[0].lower()]
        self._refill_palette_list(filtered)
        self.palette_filtered_items = filtered

    def _palette_focus_list(self, _event=None):
        if self.palette_listbox.size():
            self.palette_listbox.focus_set()
            self.palette_listbox.selection_clear(0, tk.END)
            self.palette_listbox.selection_set(0)
        return "break"

    def _activate_palette_selection(self, _event=None):
        if not self.palette_window or not self.palette_window.winfo_exists():
            return "break"
        filtered = getattr(self, "palette_filtered_items", self.palette_items)
        if not filtered:
            return "break"
        selection = self.palette_listbox.curselection()
        index = selection[0] if selection else 0
        label, payload = filtered[index]
        callback = self.palette_select_callback
        self._close_palette()
        if callback:
            callback(payload)
        return "break"

    def _close_palette(self):
        if self.palette_window and self.palette_window.winfo_exists():
            self.palette_window.destroy()
        self.palette_window = None
        self.palette_entry = None
        self.palette_listbox = None
        self.palette_items = []
        self.palette_filtered_items = []

    def _show_quick_open(self):
        items = [(str(path.relative_to(self.project_root)), path) for path in self._project_file_index()]
        self._show_picker("Quick Open", items, self._open_path_in_tab, "Quick Open")

    def _show_recent_files(self):
        items = []
        for path_text in self.recent_files:
            path = Path(path_text)
            if path.exists():
                try:
                    label = f"{path.name}  [{path.relative_to(self.project_root)}]"
                except ValueError:
                    label = str(path)
                items.append((label, path))
        self._show_picker("Recent Files", items, self._open_path_in_tab, "Recent Files")

    def _show_command_palette(self):
        commands = [
            ("New Tab", self._new_tab),
            ("Close Active Tab", self._close_active_tab),
            ("Close Other Tabs", lambda: self._close_other_tabs(use_context=False)),
            ("Save All", self._save_all_tabs),
            ("Split Active Tab", self._split_active_tab),
            ("Open File", self._open_file),
            ("Open Folder", self._open_folder),
            ("Recent Projects", self._show_recent_projects),
            ("Save", self._save_active_tab),
            ("Save As", self._save_active_tab_as),
            ("Settings", self._show_settings),
            ("Check For Updates", self._check_for_updates),
            ("Quick Open", self._show_quick_open),
            ("Recent Files", self._show_recent_files),
            ("Find", self._find_in_active_tab),
            ("Find And Replace", lambda: self._show_find_panel(with_replace=True)),
            ("Duplicate Line", lambda: self._duplicate_editor_line(self._active_tab()) if self._active_tab() else None),
            ("Delete Line", lambda: self._delete_editor_line(self._active_tab()) if self._active_tab() else None),
            ("Move Line Up", lambda: self._move_editor_lines(self._active_tab(), -1) if self._active_tab() else None),
            ("Move Line Down", lambda: self._move_editor_lines(self._active_tab(), 1) if self._active_tab() else None),
            ("Toggle Line Comment", lambda: self._toggle_line_comment(self._active_tab()) if self._active_tab() else None),
            ("Toggle Explorer", self._toggle_sidebar),
            ("Toggle Panels", self._toggle_panels),
            ("Toggle Outline", self._toggle_outline),
            ("New File In Explorer", self._new_file_in_selected_dir),
            ("New Folder In Explorer", self._new_folder_in_selected_dir),
            ("Rename Selected Path", self._rename_selected_path),
            ("Delete Selected Path", self._delete_selected_path),
            ("Copy Selected Path", self._copy_selected_path),
            ("Copy Selected Relative Path", self._copy_selected_relative_path),
            ("Open Selected In Terminal", self._open_selected_in_terminal),
            ("Run Active Tab", self._run),
            ("New Terminal", self._new_terminal_session),
            ("Rename Active Terminal", self._rename_terminal_session),
            ("Close Active Terminal", self._close_terminal_session),
            ("Restart Terminal", self._restart_shell),
            ("Switch To PowerShell", lambda: self._select_shell("PowerShell")),
            ("Switch To Command Prompt", lambda: self._select_shell("Command Prompt")),
        ]
        if "Git Bash" in self.shell_options:
            commands.append(("Switch To Git Bash", lambda: self._select_shell("Git Bash")))
        commands.append(("Show Drag-and-Drop Status", self._show_dragdrop_status))
        commands.append(("Show LSP Status", self._show_lsp_status))
        items = [(label, action) for label, action in commands]
        self._show_picker("Command Palette", items, lambda action: action(), "Command Palette")

    def _select_shell(self, shell_name):
        if shell_name in self.shell_options:
            self.shell_var.set(shell_name)
            self._restart_shell()

    def _show_dragdrop_status(self):
        if self.dragdrop_backend:
            messagebox.showinfo("Drag and Drop", f"Detected backend: {self.dragdrop_backend}", parent=self.root)
        else:
            messagebox.showinfo(
                "Drag and Drop",
                "No drag-and-drop backend is installed on this machine. Install `tkinterdnd2` or `windnd` to enable desktop file drops.",
                parent=self.root,
            )

    def _show_lsp_status(self):
        if self.lsp_executable:
            messagebox.showinfo("Luau/Lua LSP", f"Detected language server:\n{self.lsp_executable}", parent=self.root)
        else:
            messagebox.showinfo(
                "Luau/Lua LSP",
                "No Luau/Lua language server executable was found. Install `luau-lsp` or `lua-language-server` to enable richer diagnostics and navigation.",
                parent=self.root,
            )

    def _setup_dragdrop(self):
        if self.dragdrop_backend != "windnd":
            return
        try:
            import windnd
        except Exception:
            return

        def handle_drop(files):
            for raw in files:
                path = Path(raw.decode("utf-8") if isinstance(raw, bytes) else str(raw))
                if path.is_dir():
                    self._set_project_root(path)
                elif path.is_file():
                    self._open_path_in_tab(path)

        try:
            windnd.hook_dropfiles(self.root, func=handle_drop)
        except Exception:
            pass

    def _word_prefix(self, tab):
        before = tab.text.get("insert linestart", "insert")
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", before)
        return match.group(1) if match else ""

    def _completion_candidates(self, tab):
        words = set(KEYWORDS) | set(BUILTINS)
        content_words = re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", tab.text.get("1.0", "end-1c"))
        words.update(content_words)
        prefix = self._word_prefix(tab)
        candidates = sorted(word for word in words if word != prefix and word.startswith(prefix))
        return prefix, candidates

    def _show_completion(self, tab):
        prefix, items = self._completion_candidates(tab)
        if not items:
            self._hide_completion()
            self._set_status("No completions")
            return "break"

        self._hide_completion()
        self.completion_tab = tab
        self.completion_items = items
        bbox = tab.text.bbox("insert")
        if bbox:
            x, y, width, height = bbox
            root_x = tab.text.winfo_rootx() + x + 8
            root_y = tab.text.winfo_rooty() + y + height + 6
        else:
            root_x = tab.text.winfo_rootx() + 40
            root_y = tab.text.winfo_rooty() + 80
        self.completion_popup = tk.Toplevel(self.root)
        self.completion_popup.overrideredirect(True)
        self.completion_popup.configure(bg=PANEL_BG)
        self.completion_popup.geometry(f"240x180+{root_x}+{root_y}")

        self.completion_listbox = tk.Listbox(
            self.completion_popup,
            bg="#0f172a",
            fg=EDITOR_FG,
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#374151",
            selectbackground="#1d4ed8",
            selectforeground="#ffffff",
            font=("Cascadia Code", 10),
        )
        self.completion_listbox.pack(fill=tk.BOTH, expand=True)
        self.completion_listbox.bind("<Double-Button-1>", lambda _e: self._apply_completion())
        self.completion_listbox.bind("<Return>", lambda _e: self._apply_completion())
        self.completion_listbox.bind("<Escape>", lambda _e: self._hide_completion())
        self._refill_completion_list(items)
        return "break"

    def _refill_completion_list(self, items):
        if not self.completion_listbox:
            return
        self.completion_listbox.delete(0, tk.END)
        for item in items[:100]:
            self.completion_listbox.insert(tk.END, item)
        if self.completion_listbox.size():
            self.completion_listbox.selection_set(0)

    def _update_completion_items(self, tab):
        prefix, items = self._completion_candidates(tab)
        if not prefix or not items:
            self._hide_completion()
            return
        self.completion_items = items
        self._refill_completion_list(items)

    def _apply_completion(self):
        if not self.completion_popup or not self.completion_tab:
            return "break"
        selection = self.completion_listbox.curselection()
        if not selection:
            return "break"
        value = self.completion_listbox.get(selection[0])
        prefix = self._word_prefix(self.completion_tab)
        if prefix:
            self.completion_tab.text.delete(f"insert-{len(prefix)}c", "insert")
        self.completion_tab.text.insert("insert", value)
        self._hide_completion()
        self.completion_tab.text.focus_set()
        return "break"

    def _hide_completion(self):
        if self.completion_popup and self.completion_popup.winfo_exists():
            self.completion_popup.destroy()
        self.completion_popup = None
        self.completion_listbox = None
        self.completion_items = []
        self.completion_tab = None

    def _on_editor_tab_key(self, tab, event):
        if self.completion_popup and tab == self.completion_tab:
            return self._apply_completion()
        selection = self._selection_range(tab.text)
        if selection:
            return self._indent_selection_or_line(tab)
        if tab.multi_cursors:
            return self._insert_at_cursors(tab, " " * 4)
        tab.text.insert("insert", " " * 4)
        return "break"

    def _open_folder(self):
        path = filedialog.askdirectory(initialdir=str(self.project_root))
        if path:
            self._set_project_root(path)

    def _open_file(self):
        path = filedialog.askopenfilename(
            initialdir=str(self.project_root),
            filetypes=[("Luau files", "*.luau"), ("Lua files", "*.lua"), ("All files", "*.*")],
        )
        if path:
            self._open_path_in_tab(Path(path))

    def _open_path_in_tab(self, path, notebook=None, force_duplicate=False):
        path = Path(path).resolve()
        existing = self._tab_for_path(path)
        if existing and force_duplicate:
            tab = self._new_tab(
                path=path,
                notebook=notebook,
                force_duplicate=True,
                document_key=existing.document_key,
                untitled_name=existing.untitled_name,
                peer_source_tab=existing,
            )
            tab.modified = existing.modified
            tab.text.edit_modified(False)
            self._update_tab_title(tab)
            self._remember_recent_file(path)
            self._set_status(f"Opened {path.name}")
            return
        existing = None if force_duplicate else existing
        if existing:
            self._select_tab(existing)
            return
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            messagebox.showerror("Open failed", str(exc))
            return
        tab = self._new_tab(content=content, path=path, notebook=notebook, force_duplicate=force_duplicate)
        tab.modified = False
        tab.text.edit_modified(False)
        self._update_tab_title(tab)
        self._remember_recent_file(path)
        self._set_status(f"Opened {path.name}")

    def _save_active_tab(self):
        tab = self._active_tab()
        if tab:
            return self._save_tab(tab)
        return False

    def _save_active_tab_as(self):
        tab = self._active_tab()
        if tab:
            return self._save_tab(tab, save_as=True)
        return False

    def _save_tab(self, tab, save_as=False):
        if save_as or not tab.path:
            path = filedialog.asksaveasfilename(
                initialdir=str(self.project_root),
                defaultextension=".luau",
                filetypes=[("Luau files", "*.luau"), ("Lua files", "*.lua"), ("All files", "*.*")],
            )
            if not path:
                return False
            tab.path = Path(path).resolve()

        try:
            tab.path.write_text(tab.text.get("1.0", "end-1c"), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Save failed", str(exc))
            return False

        new_key = f"path:{tab.path.resolve()}"
        for linked in self._linked_tabs(tab):
            linked.path = tab.path.resolve()
            linked.document_key = new_key
            linked.modified = False
            linked.text.edit_modified(False)
            self._update_tab_title(linked)
            self._clear_recovery_snapshot(linked)
        self._refresh_project()
        self._remember_recent_file(tab.path)
        self._set_status(f"Saved {tab.path.name}")
        return True

    def _run(self):
        if self.running:
            return
        tab = self._active_tab()
        if not tab:
            return

        luau_path = self._resolve_existing_luau_path() or Path(self.luau_path_var.get().strip())
        if not luau_path.exists():
            self._ensure_luau_runtime_async()
            messagebox.showerror("luau.exe not found", f"Cannot find luau.exe at:\n{luau_path}")
            return

        temp_path = None
        if tab.path:
            if not self._save_tab(tab):
                return
            run_path = tab.path
            run_cwd = tab.path.parent
        else:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".luau", delete=False, encoding="utf-8") as handle:
                handle.write(tab.text.get("1.0", "end-1c"))
                temp_path = Path(handle.name)
            run_path = temp_path
            run_cwd = self.project_root

        self._ensure_panels_visible()
        self._clear_output()
        self._write_output(f"> Running {run_path.name} from {run_cwd}\n", "info")
        self.run_state_label.config(text="Running", fg=SUCCESS_FG)
        self._set_status(f"Running {run_path.name}")
        self.running = True

        def execute():
            try:
                self.process = subprocess.Popen(
                    [str(luau_path), str(run_path)],
                    cwd=str(run_cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    **self._hidden_subprocess_kwargs(),
                )
                stdout, stderr = self.process.communicate(timeout=30)
                self.root.after(0, lambda: self._show_result(stdout, stderr))
            except subprocess.TimeoutExpired:
                if self.process:
                    self.process.kill()
                self._log_exception("Luau run timed out for %s", run_path)
                self.root.after(0, lambda: self._write_output("\nTimed out after 30 seconds.\n", "error"))
            except Exception as exc:
                self._log_exception("Run failed for %s", run_path)
                self.root.after(0, lambda: self._write_output(f"\nRun failed: {exc}\n", "error"))
            finally:
                if temp_path and temp_path.exists():
                    temp_path.unlink(missing_ok=True)
                self.root.after(0, self._finish_run)

        threading.Thread(target=execute, daemon=True).start()

    def _show_result(self, stdout, stderr):
        if stdout:
            self._write_output(stdout, "success")
        if stderr:
            self._write_output(stderr, "error")
        if not stdout and not stderr:
            self._write_output("(no output)\n", "dim")

    def _finish_run(self):
        self.running = False
        self.process = None
        self.run_state_label.config(text="Idle", fg=LINE_FG)
        self._set_status("Ready")

    def _current_shell_name(self, session=None):
        session = session or self._active_terminal_session()
        if session:
            return session.shell_name
        return self.shell_var.get()

    def _shell_prompt_prefix(self, session=None):
        if self._current_shell_name(session) == "Git Bash":
            return "bash"
        if self._current_shell_name(session) == "Command Prompt":
            return "cmd"
        return "PS"

    def _on_shell_changed(self, _event=None):
        session = self._active_terminal_session()
        if not session:
            return
        session.shell_name = self.shell_var.get()
        self._restart_shell(session)

    def _start_shell(self, session=None):
        session = session or self._active_terminal_session()
        if not session or (session.process and session.process.poll() is None):
            return

        self._reset_terminal(session)
        session.output_queue = queue.Queue()
        session.busy = False
        session.current_marker = None
        session.cwd = session.cwd or self.project_root
        try:
            if self._current_shell_name(session) == "Git Bash":
                if not self.git_bash_path:
                    raise RuntimeError("Git Bash is not installed or could not be found.")
                command = [str(self.git_bash_path), "--noprofile", "--norc", "-s"]
            elif self._current_shell_name(session) == "Command Prompt":
                command = ["cmd.exe", "/Q", "/K"]
            else:
                command = ["powershell", "-NoLogo", "-NoProfile", "-NoExit", "-Command", "-"]
            session.process = subprocess.Popen(
                command,
                cwd=str(session.cwd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                **self._hidden_subprocess_kwargs(),
            )
        except Exception as exc:
            self._log_exception("Failed to start terminal process")
            self._write_terminal_line(session, f"Failed to start terminal: {exc}\n", "stderr")
            return

        session.alive = True
        threading.Thread(target=self._read_shell_stream, args=(session, session.process.stdout, "stdout"), daemon=True).start()
        threading.Thread(target=self._read_shell_stream, args=(session, session.process.stderr, "stderr"), daemon=True).start()
        self.root.after(60, lambda current=session: self._drain_shell_queue(current))
        self._update_terminal_header()
        self._write_terminal_line(session, f"{self._current_shell_name(session)} session started at {session.cwd}\n", "info")
        self._append_terminal_prompt(session)
        if session.pending_input:
            self._replace_terminal_command(session, session.pending_input)

    def _restart_shell(self, session=None):
        session = session or self._active_terminal_session()
        if not session:
            self._new_terminal_session()
            return
        if not session.busy:
            session.pending_input = self._terminal_current_command(session)
        self._stop_shell(session)
        self._start_shell(session)

    def _stop_shell(self, session=None):
        if session is None:
            for current in list(self.terminal_sessions.values()):
                self._stop_shell(current)
            return
        if session.process and session.process.poll() is None:
            try:
                session.process.terminate()
            except OSError:
                pass
        session.process = None
        session.busy = False
        session.alive = False
        session.current_marker = None

    def _read_shell_stream(self, session, stream, stream_type):
        try:
            for line in iter(stream.readline, ""):
                session.output_queue.put((stream_type, line))
        finally:
            session.output_queue.put(("closed", stream_type))

    def _drain_shell_queue(self, session):
        keep_polling = session.process is not None
        while True:
            try:
                stream_type, payload = session.output_queue.get_nowait()
            except queue.Empty:
                break

            if stream_type == "closed":
                continue

            normalized = self._normalize_shell_output(payload, session)

            if stream_type == "stdout" and SHELL_SENTINEL in normalized:
                self._handle_shell_sentinel(session, normalized.strip())
                continue

            tag = "stderr" if stream_type == "stderr" else "stdout"
            if normalized:
                self._write_terminal_line(session, normalized, tag)

        if keep_polling:
            self.root.after(60, lambda current=session: self._drain_shell_queue(current))

    def _normalize_shell_output(self, payload, session):
        if self._current_shell_name(session) != "Command Prompt":
            return payload
        current_prompt = f"{self._format_shell_path(session.cwd or self.project_root)}>"
        normalized = payload.replace("\r", "")
        if normalized.startswith(current_prompt):
            normalized = normalized[len(current_prompt):]
        return normalized

    def _handle_shell_sentinel(self, session, line):
        parts = line.split("|", 3)
        if len(parts) != 4:
            return
        _, marker, exit_code, cwd = parts
        if marker != session.current_marker:
            return
        session.busy = False
        session.current_marker = None
        try:
            session.cwd = Path(cwd)
            self.cwd_label.config(text=self._format_shell_path(session.cwd))
        except tk.TclError:
            return
        if exit_code != "0":
            self._write_terminal_line(session, f"[exit {exit_code}]\n", "stderr")
        self._append_terminal_prompt(session)

    def _write_terminal_line(self, session, text, tag="stdout"):
        session.text.insert(tk.END, text, tag)
        session.text.see(tk.END)

    def _reset_terminal(self, session):
        session.text.delete("1.0", tk.END)
        session.prompt_index = "1.0"

    def _append_terminal_prompt(self, session):
        prompt_path = self._format_shell_path(session.cwd or self.project_root)
        prompt = f"{self._shell_prompt_prefix(session)} {prompt_path}> "
        if session.text.index("end-1c") != "1.0":
            last_char = session.text.get("end-2c", "end-1c")
            if last_char != "\n":
                session.text.insert(tk.END, "\n")
        session.text.insert(tk.END, prompt, "prompt")
        session.prompt_index = session.text.index("end-1c")
        session.text.mark_set(tk.INSERT, "end-1c")
        session.text.see(tk.END)
        session.text.focus_set()

    def _terminal_pending_input(self, session):
        if session.busy:
            return session.pending_input
        try:
            return self._terminal_current_command(session)
        except tk.TclError:
            return session.pending_input

    def _terminal_current_command(self, session):
        return session.text.get(session.prompt_index, "end-1c")

    def _replace_terminal_command(self, session, command):
        session.text.delete(session.prompt_index, "end-1c")
        session.text.insert("end-1c", command)
        session.text.mark_set(tk.INSERT, "end-1c")
        session.text.see(tk.END)
        session.pending_input = command

    def _focus_terminal_end(self, session):
        session.text.mark_set(tk.INSERT, "end-1c")
        session.text.see(tk.END)
        session.text.focus_set()

    def _on_terminal_click(self, session, _event=None):
        self.root.after_idle(lambda current=session: self._focus_terminal_end(current))

    def _on_terminal_keypress(self, session, event):
        if session.busy:
            return "break"
        if event.keysym in {"Return", "BackSpace", "Left", "Right", "Up", "Down", "Home", "End", "Tab"}:
            return None
        if event.state & 0x4:
            return None
        if session.text.compare(tk.INSERT, "<", session.prompt_index):
            self._focus_terminal_end(session)
        return None

    def _on_terminal_keyrelease(self, session, _event=None):
        if session.busy:
            return None
        try:
            session.pending_input = self._terminal_current_command(session)
        except tk.TclError:
            pass
        return None

    def _on_terminal_backspace(self, session, _event=None):
        if session.busy or session.text.compare(tk.INSERT, "<=", session.prompt_index):
            return "break"
        return None

    def _on_terminal_paste(self, session, _event=None):
        if session.busy:
            return "break"
        try:
            pasted = self.root.clipboard_get()
        except tk.TclError:
            return "break"
        pasted = pasted.replace("\r\n", "\n").replace("\r", "\n")
        if session.text.compare(tk.INSERT, "<", session.prompt_index):
            self._focus_terminal_end(session)
        session.text.insert(tk.INSERT, pasted)
        session.text.see(tk.END)
        session.pending_input = self._terminal_current_command(session)
        return "break"

    def _on_terminal_left(self, session, _event=None):
        if session.busy or session.text.compare(tk.INSERT, "<=", session.prompt_index):
            return "break"
        return None

    def _on_terminal_home(self, session, _event=None):
        session.text.mark_set(tk.INSERT, session.prompt_index)
        return "break"

    def _on_terminal_history_up(self, session, _event=None):
        if session.busy or not session.command_history:
            return "break"
        session.history_index = max(0, session.history_index - 1)
        self._replace_terminal_command(session, session.command_history[session.history_index])
        return "break"

    def _on_terminal_history_down(self, session, _event=None):
        if session.busy or not session.command_history:
            return "break"
        session.history_index = min(len(session.command_history), session.history_index + 1)
        replacement = "" if session.history_index == len(session.command_history) else session.command_history[session.history_index]
        self._replace_terminal_command(session, replacement)
        return "break"

    def _on_terminal_enter(self, session, _event=None):
        if session.busy:
            return "break"
        command = self._terminal_current_command(session).strip()
        session.pending_input = ""
        session.text.insert(tk.END, "\n")
        session.text.see(tk.END)
        self._run_terminal_command(command, session)
        return "break"

    def _run_terminal_command(self, command, session=None):
        session = session or self._active_terminal_session()
        if not session:
            return "break"
        if not command:
            self._append_terminal_prompt(session)
            return "break"
        if not session.process or session.process.poll() is not None:
            self._start_shell(session)
        if not session.process or session.process.poll() is not None:
            return "break"

        session.command_history.append(command)
        session.history_index = len(session.command_history)
        session.busy = True
        session.command_id += 1
        marker = f"cmd{session.command_id}"
        session.current_marker = marker

        if self._current_shell_name(session) == "Git Bash":
            wrapped_command = (
                f"{command}\n"
                "__luau_exit=$?\n"
                f"printf '%s|%s|%s|%s\\n' '{SHELL_SENTINEL}' '{marker}' \"$__luau_exit\" \"$PWD\"\n"
            )
        elif self._current_shell_name(session) == "Command Prompt":
            wrapped_command = (
                f"{command}\r\n"
                f"echo {SHELL_SENTINEL}^|{marker}^|%errorlevel%^|%cd%\r\n"
            )
        else:
            wrapped_command = (
                "$ErrorActionPreference = 'Continue'\n"
                f"try {{ {command} }} catch {{ Write-Error $_ }}\n"
                "$__luauExit = if ($LASTEXITCODE -ne $null) { $LASTEXITCODE } elseif ($?) { 0 } else { 1 }\n"
                f"[Console]::Out.WriteLine('{SHELL_SENTINEL}|{marker}|'+$__luauExit+'|'+(Get-Location).Path)\n"
            )

        try:
            session.process.stdin.write(wrapped_command)
            session.process.stdin.flush()
        except Exception as exc:
            session.busy = False
            self._write_terminal_line(session, f"Terminal error: {exc}\n", "stderr")
            self._append_terminal_prompt(session)
        return "break"

    def _stop(self):
        stopped = False
        if self.process and self.running:
            self.process.terminate()
            stopped = True
        session = self._active_terminal_session()
        if session and session.busy:
            self._write_terminal_line(session, "^C\n", "stderr")
            self._restart_shell(session)
            stopped = True
        if stopped:
            self._write_output("\nStopped.\n", "dim")
        self._finish_run()
        self._set_status("Stopped")

    def _on_close(self):
        for tab in list(self.tabs.values()):
            if not self._prepare_tab_for_close(tab):
                return
        self._save_state()
        if self.process:
            self.process.terminate()
        self._stop_shell()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = LuauIDE(root)
    root.mainloop()
