# CLAUDE.md

Guidance for AI assistants (Claude Code) working in this repository.

## Project status

This repository was wiped clean for a full rewrite (see git log: "clean project for refactor"). The previous architecture is gone — do not assume any prior file layout, module structure, or pattern still applies. This is a from-scratch implementation of a Witcher 3 mod manager.

## Python environment

- Always use the Conda environment named `w3_manager` for every Python command in this repo — never system Python or another Conda environment.
- Prefer `conda run -n w3_manager <command>` so the correct environment is used even when the current shell hasn't activated it.
- Run the application:

  ```powershell
  conda run -n w3_manager python main.py
  ```

- Run verification/tests with the same environment, e.g.:

  ```powershell
  conda run -n w3_manager python -m py_compile main.py
  conda run -n w3_manager python -m pytest
  ```

- For headless Qt smoke tests, set `QT_QPA_PLATFORM=offscreen` for the command executed inside `w3_manager`.
- Do not install Python packages into system Python or any other Conda environment for this project — install into `w3_manager` only.
- The `w3_manager` env ships **PyQt6** (Qt for Python) — use `from PyQt6 import ...` imports/APIs. PySide6 was removed from this env; do not use PySide6 imports or add PySide6 back as a dependency.

## Core domain

This tool revolves around the Nexus Mods API and mod archive files (zip/rar/7z). Prefer existing pip packages over hand-rolled implementations:

- **File watching**: `watchdog` — for detecting changes in mod/game directories.
- **YAML**: `pyyaml` — for config/metadata files.
- **HTTP / Nexus API**: `requests`.
- **Archives**:
  - `.zip` — stdlib `zipfile`, no extra dependency needed.
  - `.7z` — `py7zr` (pure Python, no external binary required).
  - `.rar` — `rarfile`. This wraps an **external** `unrar`/`unar`/`bsdtar`/`7z` executable — RAR's compression is proprietary and has no pure-Python implementation. The app does **not** bundle this binary; it relies on the user already having 7-Zip or WinRAR installed (common on modding PCs). If RAR extraction fails, surface a clear error telling the user to install 7-Zip or WinRAR — do not attempt to silently fall back or reimplement RAR extraction.
- Before adding any new dependency for a "wheel that already exists" (archive formats, hashing, HTTP, YAML/JSON, file watching, etc.), check for an established pip package first rather than writing custom parsing/extraction code.

## Code language

- Always write code, identifiers, comments, docstrings, and commit messages in English — never Vietnamese or any other non-English language in code, even when the conversation with the user is in Vietnamese.

## Testing before reporting done

- Before reporting a Python change as complete, run it through the `w3_manager` environment as above (compile check and/or pytest).
- For UI (PyQt6) changes, actually launch the app or run an offscreen smoke test to confirm behavior — don't rely on compile checks alone.
