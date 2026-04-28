# Release Checklist

## Before Public Release
- Build `Lume.exe` with `build_lume_nuitka.cmd`.
- Test on a clean Windows machine with no developer tooling installed.
- Confirm `PowerShell`, `Command Prompt`, and optional `Git Bash` behavior.
- Verify `%LOCALAPPDATA%\Lume` is created and logs/state/runtime work correctly.
- Confirm bundled `luau.exe` is present or first-run runtime download works.

## Public Release Requirements
- Sign the executable and installer with a valid code-signing certificate.
- Create your Inno Setup installer.
- Confirm file properties, icon, product name, and version all say `Lume`.
- Replace `LICENSE.txt` with your final license terms.
- Review and complete `THIRD_PARTY_NOTICES.md` with exact versions and licenses.

## Update Strategy
- Current strategy: manual update check.
- Publish a new installer or executable for each release.
- Update the version in `luau_ide.py` and `build_lume_nuitka.cmd` before shipping.


