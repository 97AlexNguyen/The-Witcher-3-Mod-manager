# Roadmap

Short coordination checklist for the rewrite. One phase at a time; each phase should be
runnable before the next starts. Terminology follows `CLAUDE.md` (**manifest** vs
**game config**).

## Done

### Foundations

- [x] **Mod manager UI** — node canvas, category boxes, mod cards, drag-to-recategorize,
      detail panel. Starts empty; the sample data lives in `tests/fixtures.py` for the tests.
- [x] **Category catalog** — Nexus taxonomy loader (`app/data/category_catalog.py`). Boxes are no
      longer spawned from it; kept for the future Nexus category mapping.
- [x] **Mod-derived categories** — a category box exists exactly when a mod is filed under it.
      Installing creates the chosen category; moving the last mod out removes it. **Uncategorized**
      is the one permanent box. Category name/colour persist in the manifest's `categories` list.
- [x] **Settings** — `config.json` (game path, vault path) in `%LOCALAPPDATA%`, atomic write;
      Nexus API key in OS keyring; path validation + modal dialog (`app/config/`, `app/ui/dialogs/`).
- [x] **Nexus API key check** — real `users/validate.json` call, off-thread in the dialog
      (`app/config/nexus_api.py`).

### Install mod flow (disk + manifest)

Turns a downloaded archive into an installed, manifest-tracked mod — everything except the
game-config merge, which is deferred (see Next).

- [x] **Manifest store** — `InstalledMod` ↔ JSON at `%LOCALAPPDATA%\…\manifest.json`,
      atomic write + `fasteners` inter-process lock (`app/manifest/store.py`). `ModManagerPage`
      loads mods and categories from it (fresh install = empty, only Uncategorized), and persists
      every install/toggle/recategorize (debounced) + on exit. A second live instance stays
      read-only. **Deviation:** no `installed.xml` import (this tool's JSON is brand new by decision).
- [x] **Archive extraction** — zip (stdlib), 7z (`py7zr`), rar (`rarfile` → external 7-Zip/WinRAR;
      clear error if missing). Inspects contents into a `ModPackage` (scanned, not yet installed)
      (`app/install/extract.py`, `app/install/scanner.py`). Handles wrapped `Mods/`/`DLC/`, an
      extra nesting folder, and loose `mod*`/`dlc*` folders; guesses name/version from the filename.
- [x] **Install to disk** — copies `Mods/` + `DLC/` bundles into the game and vaults the source
      archive to `vault_path` (`app/install/installer.py`). Reinstall overwrites in place.
- [x] **Record in manifest** — `install_package` returns an `InstalledMod` (content groups, vault
      path, status); `ModManagerPage` adds it to the model, which persists to `manifest.json`.
      Settings/keys await the merge step (see Next).
- [x] **Install UI** — header "＋ INSTALL MOD" button (file picker) + archive drop target both call
      `ModManagerPage.install_archives`, which prompts for a category (existing or new — created on
      the spot) → install + result notice. Read-only instance is blocked; a missing/invalid game
      folder is refused with a notice.

## Next

Open items on the install flow, in rough priority order.

- [ ] **Threading** — extraction/install off the UI thread; optimistic where safe. Installs
      currently run **synchronously** on the UI thread, so a large archive freezes the window.
      Pick this up first — it is the last piece of the disk-install flow.
- [ ] **Merge into game config** — `input.xml`, `user.settings`, `input.settings`,
      `dx11/dx12filelist.txt`, menu xml. Each merge fails independently → per-target status,
      surface `INCOMPLETE` in the mod list (never silently). **Deferred by decision** — not started;
      installed mods currently record `OK` for the disk copy alone. Once wired, this also fills the
      manifest's `settings`/`keys` groups.

## After install

- [ ] **Toggle / uninstall** — enable/disable renames on disk; uninstall un-merges from game
      config and restores, and removes the (now-empty) category box. Off-thread, optimistic toggle
      (see `docs/ui/mod-manager-tab.md` §6). Note `_request_remove` is still a stub notice.
- [ ] **File watching** — `watchdog` on game/mod dirs, debounced, marshalled to the UI thread.
- [ ] **Nexus API integration** — use the validated key: fetch mod metadata, category mapping
      (resolution order in `mod-manager-tab.md` §3), version/update checks.
- [ ] **Version source** — parsed from archive filename now (`app/install/scanner.py`); let the API
      overwrite later (open decision, `mod-manager-tab.md` §9).

## Notes

- Install depends on the manifest store — build persistence first even though the goal is install.
- Never change game-config formats/encodings; merges are into engine-owned files.
- Tests: `conda run -n w3_manager python -m unittest discover -s tests` (env has no pytest).
