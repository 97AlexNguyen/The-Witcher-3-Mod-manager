# Mod manager tab — UI implementation guide

Status: **zoomable node canvas implemented against mock data** (pan/zoom + collapsible,
movable and resizable boxes + drag-to-recategorize + detail panel). **§0 describes it.**
Sections 1 and 3's rail+table design is **superseded** by §0 and kept only for context;
§2 (model layer), §4 (detail panel), §6 (threading), and §7 (empty states) still apply.
This tab manages mods already known to the app; installing is a separate flow.

Read `.agents/skills/pyqt6-ui-designer/references/design_tokens.md` before writing any
widget code. All spacing/color/typography constants referenced here come from there.

Terminology in this document follows `CLAUDE.md`: **manifest** is this app's own JSON
record (`%LOCALAPPDATA%\The Witcher 3 Mod Manager\`), **game config** is the engine's own
xml/ini files. This tab reads and writes the manifest. It triggers game config changes
only indirectly, by asking the install/toggle services to perform them.

---

## 0. Current layout — box shelf (implemented)

The tab is a `QSplitter`: a Houdini-style **node canvas** (`QGraphicsView` and
`QGraphicsScene`) on the left and a collapsible `ModDetailPanel` on the right. Each
`CategoryBox` is embedded through a `QGraphicsProxyWidget` with independent scene
coordinates and size; no layout controls box placement. Drag `⠿` to move a box and `◢`
to resize it. Moving or resizing one box never pushes its neighbours.

The canvas has a minor/major grid, wheel zoom centred under the pointer, middle-mouse or
Space+left-drag panning, plus zoom, Frame All and Arrange controls. Arrange packs the
current boxes into compact non-overlapping rows near the camera, preserving every box's
size and collapsed state, then frames the result. Its large scene supports many boxes
without expanding a conventional widget. Box geometry, collapsed state, camera centre
and zoom level all persist to `QSettings`.

- **Each box always shows** its header (category name, on/off split, mod count, attention
  flag). Collapsing a box hides its body and leaves this statistical summary visible;
  expanding it reveals search and a scrolling list of mod cards.
- **Move and resize freely** — box movement is direct geometry manipulation from its
  header handle; mod movement still uses `MIME_MOD_IDENTITY`. The separate interaction
  paths prevent moving a box from conflicting with dragging a mod between boxes.
- **Inside a box**, mods are `ModCard`s in a `FlowLayout` grid that reflows to the box's
  current width. Every card is the exact same fixed size regardless of name length, version
  presence, or status — two cards with the same job sitting next to each other must never
  differ in size. Long names wrap to two lines and ellipsise; the full name is in the tool
  tip. Nothing is clipped mid-glyph.
- **Recategorize by drag** — drag a `ModCard` out of one box and drop it on another box
  (the whole box is a drop target). Drop = `model.set_category`. Source and target refresh,
  and every box header count updates.
- **Toggle** ON/OFF per card writes through the list model; only the box header count
  refreshes, not the card grid, so the clicked card is not destroyed under the cursor.
- **Double-click a card** (or its ⋮ → *View details*) drives the `ModDetailPanel` on the
  right. Its category picker routes through the same `model.set_category`.
- **Remove** and **install** are acknowledged with a notice but not yet wired — removal
  un-merges a mod from game config and install is a separate flow.

Component map:

| Widget | File | Role |
|--------|------|------|
| `CategoryBox` | `app/ui/widgets/mod_category_box.py` | One collapsible category box; header stats + scrolling card list; box drag source and mod drop target |
| `ModBoxWorkspace` | `app/ui/widgets/mod_box_workspace.py` | Zoomable `QGraphicsView` node canvas; owns box proxies, camera, grid and pan/zoom controls |
| `ModCard` | `app/ui/widgets/mod_card.py` | One mod; fixed size; drag source; thumbnail |
| `FlowLayout` | `app/ui/widgets/flow_layout.py` | Wrapping grid for the cards |
| `ModDropTargetMixin` | `app/ui/widgets/mod_drop_target.py` | Shared drop handling |
| `ModDetailPanel` | `app/ui/widgets/mod_detail_panel.py` | Read-only mod detail; category picker |
| `ModManagerPage` | `app/ui/pages/mod_manager_page.py` | Owns model + shelf of boxes + detail panel |

`InstalledModListModel` remains the single source of truth: cards and tiles read from it
and write category/enable changes back through it, and its `dataChanged`/row signals drive
every refresh. Box membership is derived (`category_key`), never stored per box.

---

## 1. Layout — SUPERSEDED by §0 (box shelf)

> The rail + table layout below was the original design. It has been replaced by the box
> shelf described in §0. Kept for context on the sizing/persistence reasoning, which still
> informs the shelf/detail splitter.

Three horizontal panes in a `QSplitter(Qt.Orientation.Horizontal)`. Horizontal because
target displays are wide and short (1920x1080 and ultrawide); vertical stacking wastes
the axis we have most of.

```
┌────────────┬──────────────────────────────────┬─────────────────┐
│ Category   │ Toolbar: [search] [add] [filter] │ Detail panel    │
│ rail       ├──────────────────────────────────┤                 │
│            │ Mod table                        │ name / version  │
│ ● All   24 │  ⦿ │ Name      │ Ver │ Pri │ ⚠   │ category picker │
│ ● UI     6 │  ⦿ │ ...       │     │     │     │ ───────────────  │
│ ● Gfx    9 │                                  │ [Content][Set..]│
│ ● Play   7 │                                  │                 │
│ ● Unset  2 │                                  │ content view    │
│            ├──────────────────────────────────┤                 │
│ + New      │ 24 mods · 19 enabled   [▲][▼][🗑]│                 │
└────────────┴──────────────────────────────────┴─────────────────┘
     180px              stretch: 1                    320px
```

Sizing rules:

| Pane | Width | Behaviour |
|------|-------|-----------|
| Category rail | 180px default, min 140px | `setStretchFactor(0, 0)` — never grows |
| Table | fills | `setStretchFactor(1, 1)` — absorbs all resize |
| Detail | 320px default, min 260px | `setStretchFactor(2, 0)` — fixed feel, user-draggable |

- Splitter handles: 1px, `COLOR_OUTLINE_VARIANT`. Set `setChildrenCollapsible(False)` —
  a collapsed rail with no way back is a support ticket.
- Content padding: `SPACING_LG` (24px) around the splitter, `SPACING_MD` (16px) inside panes.
- Table rows: 32px (compact). This is a dense list; 40px wastes the viewport.

Persist `splitter.saveState()` to `QSettings` on close, restore on open. Same for table
column widths and the last selected category. Users re-arrange this once and expect it
to stick.

---

## 2. Model layer

**Use `QTableView` + a custom `QAbstractTableModel`. Do not use `QTableWidget`.**

This deliberately diverges from `component_library.md` §5, which offers a
`DataTable(QTableWidget)`. That component is right for static data, wrong here: this tab
needs category filtering + text search + column sorting simultaneously, which is exactly
what `QSortFilterProxyModel` gives for free and what `QTableWidget` forces you to
hand-roll by hiding rows. Everything else in the design system still applies — only the
table base class changes.

```
ModTableModel(QAbstractTableModel)      owns list[InstalledMod], read-only view of state
   └── ModFilterProxy(QSortFilterProxyModel)   category + search filtering, sorting
          └── QTableView                        presentation only
```

`ModFilterProxy` holds two filter criteria and ANDs them:
- `category_key: str | None` — `None` means "All"
- `search_text: str` — case-insensitive substring on mod name

Override `filterAcceptsRow` to check both. Do not chain two proxies; one proxy with two
criteria is simpler and avoids double-mapping index bugs.

### View-model separation

Keep two distinct types. Do not reuse one class for both, which is what the reference
implementation did (`Mod` served as both scanned-archive and installed-state, forcing
`installer.py` to compare `mod.files == installed.files and mod.name == installed.name`
to guess identity).

- `ModPackage` — scanned archive contents. Belongs to the install flow. Not on this tab.
- `InstalledMod` — manifest-backed record: name, version, priority, enabled, category,
  install date, content summary, health status, vault path.

The table model consumes `InstalledMod` only.

### Manifest shape

`InstalledMod` is the in-memory form of one entry. Indicative JSON:

```json
{
  "version": 2,
  "categories": [
    { "key": "gfx", "name": "Graphics", "color": "#1D9E75", "order": 1 }
  ],
  "mods": [
    {
      "name": "Ard Bombs",
      "enabled": true,
      "date": "2026-07-17T08:56:45Z",
      "priority": null,
      "category": "gameplay",
      "modVersion": "1.10",
      "files": ["mod_ArdBombs"],
      "dlcs": ["dlc_ArdBombs"],
      "status": "ok",
      "vault": "ard-bombs-a1b2c3.zip"
    }
  ]
}
```

Top-level `version` is a schema version for migration — the reference format grew two
incompatible readme encodings and two usersetting layouts with no way to tell them apart.

Three behaviours to carry over from the reference `Model`, independent of format:

- **Atomic write** (`model.py:55`): write `.new`, rotate the old file to `.old`, then
  rename into place. A power cut mid-write must not lose the modlist.
- **`InterProcessLock`** (`model.py:25`): two app instances must not write concurrently.
- **One-way import of legacy `installed.xml`**: existing users have one. Read it once,
  convert, never write XML again.

### Columns

| # | Column | Width | Data | Notes |
|---|--------|-------|------|-------|
| 0 | Toggle | 44px fixed | `enabled: bool` | Custom delegate, not a checkbox — see §5 |
| 1 | Name | stretch | `name: str` | Category colour dot painted as `DecorationRole` |
| 2 | Version | 72px | `version: str \| None` | Mono font. `None` renders as `?`, muted |
| 3 | Priority | 56px | `priority: int \| None` | Mono, right-aligned. `None` renders `-` |
| 4 | Health | 36px fixed | `status: ModStatus` | Icon only, tooltip carries the reason |

Set `horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)` and
`Fixed` on 0 and 4. Leave 2 and 3 `Interactive`.

Header style: `TYPO_LABEL_MD`, uppercase, tracked — per design tokens.

### Priority renders `-`, never `0`

`priority = None` and `priority = 0` are different states. `None` means the entry is
removed from `priority.ini` entirely and the game falls back to alphabetical ordering;
`0` is an explicit lowest priority. Rendering `0` for an unset mod misreports what the
app actually wrote to disk. The reference implementation gets this right (`Mod.priority`
returns `'-'` when unset) — preserve the behaviour.

Keep the three representations distinct and convert only at the boundaries:

| Layer | Unset priority |
|-------|----------------|
| Manifest (JSON) | `null` |
| `InstalledMod.priority` | `None` |
| Table cell | `-`, muted |

The reference stored `"-"` as a string in `installed.xml` and had to compare it against
the magic value `"Not Set"` on read, because XML has no null. JSON does — use it, and
never let the display string `"-"` leak into the model or the file.

---

## 3. Category system

Category is new — the reference manager has no equivalent. It is the organising principle
of this tab, so it needs its own spec.

### It does not affect load order

Load order is determined by `priority.ini` and alphabetical folder names. Category is a
**view construct only**. Users will assume grouping implies ordering, so:

- Keep the `Pri` column in the table, never in the rail.
- Never sort the table by category implicitly.
- If a "reorder priority by category" feature is ever added, it must be an explicit,
  named action with a preview — never a side effect of assigning a category.

### Storage

Category cannot be derived from mod files — nothing in an archive says "this is a
graphics mod". It is app metadata: it lives in the **manifest**, never in game config,
and it must survive uninstall/reinstall. Keyed by mod identity, not by install state.

The category list itself (key, display name, colour, order) is manifest data too, stored
alongside the mods — not in `QSettings`. `QSettings` holds view state that can be lost
without harm (splitter sizes, column widths, last selected category). Losing a user's
category definitions is data loss; losing their column widths is not.

### Resolution order

1. User assignment (explicit, wins always)
2. Nexus API `category_id`, mapped to a local category (when the API lands)
3. `Uncategorized`

The `Uncategorized` bucket is mandatory, not optional. Every mod lands somewhere, and the
bucket doubles as the user's to-do list.

### One category per mod

Single-assignment, enforced. The rail shows per-category counts, and counts are only
meaningful if they sum to the total — multi-assign breaks that, and with it the user's
ability to glance at the rail and see what still needs sorting. If richer grouping is
needed later, add **tags** as a separate system; do not loosen category.

### Rail behaviour

- Fixed built-in rows: `All` (count = total), `Uncategorized` (count = unassigned).
- User categories in between, user-orderable.
- Each row: colour dot (7px), name (elided), count (right-aligned, muted).
- Selection filters the table. Selection is persisted.
- Drop target: dragging table rows onto a rail row reassigns category. Accept the drop
  on the rail row, not the rail container, and highlight the hovered row.
- Colour is user-chosen from a fixed palette. Do not auto-assign random colours —
  palette-constrained keeps the rail readable and dark-mode-safe.

Implement the rail as a `QListView` with a custom delegate, not hand-stacked `QWidget`s.
Counts change on every toggle/install; a model-backed list updates cleanly.

---

## 4. Detail panel

Read-only in v1. Two exceptions, because they are the two things users change most and
both are cheap to make safe:

- **Category picker** — a combo box at the top. Writes metadata only, no file I/O, no
  failure mode worth designing around.
- **Priority** — a spin box with `-` as a distinct state below 0. Writes `priority.ini`.

Everything else (user settings values, key bindings, file lists) stays read-only until
there is a real reason to make it editable. Editing merged game config from a detail
panel is a footgun; the install flow already owns that responsibility.

Sections, as a segmented control (not tabs — tabs at this width look like app-level nav
and get confused with the real tab bar):

| Section | Content | Source |
|---------|---------|--------|
| Content | What was written where: `Mods/`, `DLC/`, menu xml, xml keys | `InstalledMod` manifest |
| Game settings | `user.settings` / `dx12user.settings` additions, grouped by section | manifest |
| Keys | `input.settings` bindings, grouped by context | manifest |
| Readme | Rendered readme text if the archive had one | vault |

The second section is labelled **Game settings**, not "Settings". An unqualified
"Settings" here reads as the app's own preferences, which live on a different tab
entirely — and the whole point of the terminology split is that these are the game's
files, which this panel only reports on.

Empty section = show a one-line muted message ("This mod adds no user settings"), never
a blank panel. Blank reads as broken.

Multi-selection in the table → panel shows a summary ("3 mods selected") plus the bulk
actions that apply, not the first mod's details.

---

## 5. Custom delegates

Two cells need painting, not widgets. Never put live `QWidget`s in table cells via
`setIndexWidget` — it allocates one widget per row and falls apart past a few hundred rows.

### Toggle delegate (column 0)

A switch, not a checkbox. This is load-bearing: the switch means "enabled in game"
(an immediate action that renames files on disk), while row highlight + Ctrl/Shift-click
means "selected for a bulk action". If both were checkboxes users could not tell them
apart.

- Paint via `QPainter` in `paint()`: 24x14 rounded track + 10px knob.
- Handle `editorEvent` for `MouseButtonRelease` inside the switch rect.
- On: `COLOR_PRIMARY` track. Off: `COLOR_OUTLINE_VARIANT` track. Knob always
  `COLOR_SURFACE_LOWEST`.
- Disabled mod name renders `COLOR_ON_SURFACE_VARIANT` — the whole row reads as dimmed.

### Health delegate (column 4)

Renders `ModStatus`:

| Status | Icon | Colour | Meaning |
|--------|------|--------|---------|
| `OK` | check | `COLOR_SUCCESS` | Installed cleanly |
| `INCOMPLETE` | alert-triangle | `COLOR_WARNING` | Files copied, but a merge into shared game config failed |
| `VAULT_MISSING` | archive-off | `COLOR_ON_SURFACE_VARIANT` | Cannot be reinstalled — source archive gone |
| `ERROR` | alert-circle | `COLOR_DANGER` | Install failed |

`INCOMPLETE` is the important one. Installing a mod touches six targets, and the merges
into shared files (`input.xml`, `user.settings`, `input.settings`, `dx11/dx12filelist.txt`)
each fail independently — the reference installer catches per-target exceptions and only
raises an `incompleteCount`, which it then buries in a log pane. A mod can be "installed"
and still half-broken in a way that needs manual fixing. Surface it in the list.

Tooltip must state which target failed. An icon with no explanation is worse than nothing.

---

## 6. Threading

Toggling a mod renames directories and rewrites xml/ini files. Never on the UI thread.

- Wrap mutations in a worker (`QRunnable` + `QThreadPool`, or a service object moved to a
  `QThread`). The model receives results via signals.
- **Optimistic UI**: flip the switch immediately, revert with a toast on failure. A 200ms
  freeze per toggle makes the app feel broken.
- Disable the specific row while its mutation is in flight, not the whole table.

### File watching

`CLAUDE.md` mandates `watchdog`. Its observer thread is **not** a Qt thread — emitting
directly into widgets from it is a crash waiting to happen. Marshal every event through a
`pyqtSignal` on a `QObject` that lives on the UI thread, and debounce (~300ms): a single
mod install produces dozens of filesystem events.

The reference implementation used a `QThread`-based watcher (`ModsSettingsWatcher`) for
this. `watchdog` is the better primitive but inherits the same threading obligation.

---

## 7. Empty and error states

| Condition | Treatment |
|-----------|-----------|
| No mods at all | Centred invitation in the table area + primary "Add mod" button. Rail still renders. |
| Category empty | Muted line in the table area, keep the rail selection intact. |
| Search no match | Muted line + "Clear search" ghost button. |
| Game path not set | Banner above the splitter, link to the Settings tab. Table stays disabled. |

The last one matters: with no game path, every action on this tab fails. Say so once, at
the top, instead of letting each action error separately.

---

## 8. Build order

Each step should be runnable before starting the next.

1. `InstalledMod` dataclass + `ModStatus` enum. Fake in-memory list of 5 mods.
2. `ModTableModel` + `QTableView`, plain text columns, no styling. Verify data appears.
3. `ModFilterProxy` + search input. Verify filtering.
4. Category rail (`QListView` + delegate) wired to the proxy filter. Verify counts.
5. Toggle + health delegates. Verify painting in both themes.
6. Detail panel, read-only, driven by selection.
7. `QSplitter` + `QSettings` persistence.
8. Swap the fake list for the real manifest store (JSON load/save + atomic write + lock),
   plus the one-way `installed.xml` import.
9. Threading + optimistic toggle.
10. Drag-drop onto the rail.

Steps 1–7 need no file I/O and no game install — build the whole UI against fake data
first. It is much faster to iterate on layout without a Witcher 3 installation in the loop.

Per `CLAUDE.md`, verify each step in the `w3_manager` env, and for UI steps actually
launch it (`conda run -n w3_manager python main.py`) or run an offscreen smoke test with
`QT_QPA_PLATFORM=offscreen` — compile checks do not catch layout or painting bugs.

---

## 9. Open decisions

- **Version source.** `InstalledMod.version` has no origin yet. The reference `Mod` has no
  version field at all. Options: parse from the archive filename (the `-1234-3-5-` pattern
  that `formatName` currently discards), or wait for the Nexus API. Recommendation: parse
  now, let the API overwrite later — the column is never empty, and the API upgrades data
  without changing layout.
- **Bulk category toggle.** Right-click a rail row → disable every mod in it. Convenient,
  but disabling all of "Graphics" can break a mod outside that category that depends on
  one of them. Needs a dependency story before it ships.
- **Detail panel editability** beyond category and priority.
