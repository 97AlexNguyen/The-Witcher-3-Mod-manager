![Logo](https://github.com/97AlexNguyen/The-Witcher-3-Mod-manager/blob/Custom/witcher%20mod%20manager.png)

Hi guys .I have enhanced some of these tools for personal use and now wish to share them with everyone. I hope they are useful to you.
Git : https://github.com/97AlexNguyen/The-Witcher-3-Mod-manager/releases/tag/release-0.9.4-beta1
**New Features:**
- A redesigned menu section.
- The ability to sort and group mods by category for better organization.
- Automatic category extraction from Nexus Mods, which assigns each mod to its appropriate group. Support both : API and web scrap.
- An added mod summary display that allows users to quickly see what each mod does.
**ToDo:**
- Support for installing additional files, such as .ini, .dll, and more.
- An improved menu installation system that creates automatic checkpoints for game menus before any mod overwrites them. This ensures that uninstalling a mod will restore the menu to its original state.

https://github.com/97AlexNguyen/w3string_gui/releases/tag/0.0.0.1
- An integrated companion tool for working with .w3strings files, featuring:
  - Encoding and decoding of .w3strings.
  - Splitting CSVs by ID and merging them back together.
  - A design specifically aimed at enabling mod translation via AI. Users can extract lines based on ID, send them to an AI like ChatGPT for translation, and then merge them back, making mod localization much more efficient.




# The Witcher 3 Mod Manager

Mod Manager for The Witcher 3.

Supports the Steam and GOG releases on Windows and the Steam Proton release on Linux.

## Description

The Witcher 3 Mod Manager is an application that simplifies installing and managing The Witcher 3 mods, originally developed by [stefan3372](https://github.com/stefan3372) and now being continued here.

See the [Nexus Mods page](https://www.nexusmods.com/witcher3/mods/2678) for releases, screenshots and more information.

## Usage

### Release Versions (Windows)

Download and unpack the latest release from Nexus Mods or from the GitHub releases. If you are upgrading from version 0.6 or later, directly overwrite the previous installation. Existing configuration files will be searched in the same directory as the executable first, in `Documents\The Witcher 3 Mod Manager` second.

On the first run, if no configuration can be found, configuration files will be created under `Documents\The Witcher 3 Mod Manager`. They can be freely relocated between the two searched locations as preferred.

### Python (Windows and Linux)

The project uses [PDM](https://pdm-project.org/en/latest/) for dependency management. Requires Python 3.10 or newer (3.10+), up to Python 3.12.

1. Install PDM with [recommended installation method](https://pdm-project.org/en/latest/#recommended-installation-method)
2. Clone the repository
3. Install dependencies: `pdm install --prod`
4. Run the application: `pdm run start`

On Linux:
- Configuration files are created in `~/.config/TheWitcher3ModManager`
- `wine` must be available to run Script Merger
- Consider using `pdm run` prefix for all commands

### Build Release (Windows)

1. Install dependencies with development tools: `pdm install`
2. Build executable: `pdm run build-win`
3. Find files in `build/exe.[platform identifier].[python version]`
