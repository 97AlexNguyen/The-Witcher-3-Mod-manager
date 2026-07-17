from __future__ import annotations

from datetime import date

from app.domain import Category, InstalledMod, ModStatus


def make_mock_categories() -> list[Category]:
    return [
        Category("all", "All mods", "neutral", built_in=True),
        Category("graphics", "Graphics", "blue"),
        Category("gameplay", "Gameplay", "violet"),
        Category("interface", "Interface", "teal"),
        Category("uncategorized", "Uncategorized", "amber", built_in=True),
    ]


def make_mock_mods() -> list[InstalledMod]:
    return [
        InstalledMod(
            identity="hd-reworked",
            name="The Witcher 3 HD Reworked Project",
            description="High-resolution textures and meshes that preserve the original visual direction.",
            version="12.0",
            priority=10,
            enabled=True,
            category_key="graphics",
            installed_on=date(2026, 7, 12),
            content={"Mods/": ("modHDReworkedProject",), "DLC/": ("dlcHDReworkedProject",)},
            readme="High-fidelity textures and meshes while preserving the original art direction.",
            status=ModStatus.OK,
            vault_path="vault/hd-reworked-12.0.7z",
        ),
        InstalledMod(
            identity="friendly-hud",
            name="Friendly HUD",
            description="A configurable HUD overhaul with immersive markers, minimap, and exploration tools.",
            version="13.6",
            priority=20,
            enabled=True,
            category_key="interface",
            installed_on=date(2026, 7, 10),
            content={"Mods/": ("modFriendlyHUD",), "Menu XML": ("friendlyhud.xml",)},
            settings={"Friendly HUD": ("hudScale=1.0", "showQuestMarkers=true")},
            keys={"Exploration": ("F2: Toggle HUD", "F3: Toggle minimap")},
            readme="Configure HUD modules in the in-game Mods menu.",
            status=ModStatus.INCOMPLETE,
            status_detail="Installed, but the merge into input.settings failed",
            vault_path="vault/friendly-hud-13.6.zip",
        ),
        InstalledMod(
            identity="ghost-mode",
            name="Ghost Mode",
            description="A comprehensive gameplay rebalance focused on combat, progression, and consistency.",
            version="4.6",
            priority=5,
            enabled=False,
            category_key="gameplay",
            installed_on=date(2026, 7, 8),
            content={"Mods/": ("modGhostMode",), "DLC/": ("dlcGhostMode",)},
            settings={"Gameplay": ("difficultyScaling=true",)},
            readme="A gameplay overhaul focused on balance and consistency.",
            status=ModStatus.OK,
            vault_path="vault/ghost-mode-4.6.zip",
        ),
        InstalledMod(
            identity="brothers-in-arms",
            name="Brothers in Arms - TW3 Bug Fix Collection",
            description="A community collection fixing quests, dialogue, gameplay, scripts, and visual issues.",
            version="1.30",
            priority=None,
            enabled=True,
            category_key="gameplay",
            installed_on=date(2026, 7, 5),
            content={"Mods/": ("modBrothersInArms",), "XML keys": ("biaconfig.xml",)},
            status=ModStatus.VAULT_MISSING,
            status_detail="Source archive is missing from the local vault",
        ),
        InstalledMod(
            identity="auto-apply-oils",
            name="Auto Apply Oils",
            description="Automatically applies the best available blade oil when combat begins.",
            version=None,
            priority=0,
            enabled=True,
            category_key="uncategorized",
            installed_on=date(2026, 7, 2),
            content={"Mods/": ("modAutoApplyOils",)},
            keys={"Combat": ("O: Toggle automatic oil selection",)},
            status=ModStatus.ERROR,
            status_detail="Installation manifest is incomplete",
            vault_path="vault/auto-apply-oils.zip",
        ),
    ]
