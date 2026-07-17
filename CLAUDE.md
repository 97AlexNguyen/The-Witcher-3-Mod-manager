# CLAUDE.md

Guidance for AI assistants (Claude Code) working in this repository.

## Project status

This repository was wiped clean for a full rewrite (see git log: "clean project for refactor"). The previous architecture is gone — do not assume any prior file layout, module structure, or pattern still applies. This is a from-scratch implementation of a Witcher 3 mod manager.

## Terminology — read this first

Two unrelated sets of files are both casually called "settings". Confusing them corrupts
the user's game install. Always use these terms; never write "settings" unqualified.

| Term | What it is | Where it lives | Who reads it | Format |
|------|-----------|----------------|--------------|--------|
| **Manifest** | This app's own record of which mods are installed, their category, priority, and what each one wrote where | `%LOCALAPPDATA%\The Witcher 3 Mod Manager\` | **Only this app** | **JSON** — we choose it |
| **Game config** | The game's own configuration that mods merge into | `<game>\bin\config\r4game\user_config_matrix\pc\` and `<Documents>\The Witcher 3\` | **REDengine, at startup** | XML / INI / UTF-16 text — **the game dictates it** |

Rules that follow from this:

- **Never** propose changing the format of game config. `input.xml`, `hidden.xml`, the menu
  xml files, `user.settings`, `dx12user.settings`, `input.settings`, and
  `dx11filelist.txt` / `dx12filelist.txt` are read by the game engine. It does not parse
  JSON. Their formats and encodings (including UTF-16) are hard external constraints.
- Installing a mod **merges into** game config — it is not a folder copy. Those merges can
  each fail independently, leaving a mod installed but half-broken.
- The manifest is ours alone. It is machine-written and machine-read; no user edits it by
  hand.
- In code and docs, prefer `manifest` and `game_config` as identifiers. Do not name
  anything just `settings`.

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
- **Manifest**: stdlib `json`. Machine-written and machine-read, so JSON's lack of type
  coercion is the point: YAML would silently turn mod version `1.10` into the float `1.1`
  and a category named `NO` into `False`. JSON is also UTF-8 by spec, so the manifest
  never needs encoding detection. Do not add `pyyaml` for this — reach for YAML only if a
  file is ever introduced that users edit by hand, and none exists today.
- **Game config**: format is fixed by the engine, not by us — see Terminology. Use stdlib
  `xml.etree.ElementTree` for xml and `configparser` for the INI-like `.settings` files.
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
