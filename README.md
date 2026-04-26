# Lume

Lume is a desktop IDE focused on fast Luau editing, project browsing, and local execution.

## Quick Start
- Open a project folder with `Ctrl+Shift+O` or `Menu > Open Folder`.
- Open files from the explorer with `Enter` or double-click.
- Run the active Luau file with `F5`.
- Use the terminal panel for `PowerShell`, `Command Prompt`, or `Git Bash` commands.

## Shells
- `PowerShell` and `Command Prompt` are built in on Windows.
- `Git Bash` is optional. Lume detects it automatically if Git for Windows is installed.

## Luau Runtime
- If `luau.exe` is bundled with the build, code runs immediately.
- If not bundled, Lume can download the Luau runtime into `%LOCALAPPDATA%\Lume\runtime` on first run.

## Editor Shortcuts
- `F5`: run active file
- `Ctrl+F`: find
- `Ctrl+H`: find and replace
- `Ctrl+D`: duplicate line
- `Ctrl+Shift+K`: delete line
- `Alt+Up` / `Alt+Down`: move line
- `Ctrl+/`: toggle line comment
- `Ctrl+Alt+Up` / `Ctrl+Alt+Down`: vertical multi-cursor

## Production Notes
- State, logs, runtime downloads, and recovery files are stored in `%LOCALAPPDATA%\Lume`.
- Update strategy is manual by default.
- For public release, code signing is strongly recommended to reduce Windows SmartScreen friction.
