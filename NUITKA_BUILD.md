# Lume Nuitka Build

Use `build_lume_nuitka.cmd` from `C:\Users\adm\.vscode\Products\Ides`.

What the build script includes automatically:
- `logo.png` as runtime data so the window/taskbar branding used by Tk stays available after compilation.
- `logo.ico` as the Windows executable icon.
- `luau.exe` if it exists next to `luau_ide.py` at build time.

Runtime behavior:
- If `luau.exe` is bundled next to the app, Lume will use it first.
- If it is not bundled, Lume will look in the persistent per-user runtime folder.
- If no runtime exists yet, Lume will download the latest Windows Luau release automatically into `%LOCALAPPDATA%\Lume\runtime\luau.exe`.

Recommended build flow:
1. Keep `logo.png`, `logo.ico`, `luau_ide.py`, and optionally `luau.exe` in the same folder.
2. Run `build_lume_nuitka.cmd`.
3. Distribute the generated `Lume.dist` folder.

Notes:
- `logo.ico` was generated from `logo.png` and is required for the compiled `.exe` icon.
- The script currently builds `--standalone`, which is the safer target for Tk apps with external assets.
- If you later want a `--onefile` build, keep the same data-file flags and test startup carefully because extraction changes runtime paths.
