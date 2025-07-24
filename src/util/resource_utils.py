'''Resource utilities for handling file paths in both development and executable environments'''

import sys
import os
from pathlib import Path
from typing import Optional, List

def get_resource_path(relative_path: str) -> Optional[Path]:
    """
    Get the absolute path to a resource file that works both in development and when frozen as exe.
    
    Args:
        relative_path: Relative path from project root (e.g., "mapping/category_mapping.yaml")
    
    Returns:
        Path object if file exists, None otherwise
    """
    try:
        # Determine base directory based on execution environment
        if getattr(sys, 'frozen', False):
            # Running from executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                base_dir = Path(sys._MEIPASS)
            else:
                # cx_Freeze - resources are in lib folder
                base_dir = Path(sys.executable).parent / "lib"
        else:
            # Running from script - get project root
            # Assuming this utility is in src/util/ - go up 2 levels
            base_dir = Path(__file__).resolve().parents[2]
        
        # Try multiple possible locations
        possible_paths = [
            base_dir / relative_path,
            base_dir / "lib" / relative_path,
            Path(sys.executable).parent / relative_path,  # Next to exe
        ]
        
        # Return first existing path
        for path in possible_paths:
            if path.exists():
                return path
        
        print(f"[get_resource_path] Could not find {relative_path} in any of: {[str(p) for p in possible_paths]}")
        return None
        
    except Exception as e:
        print(f"[get_resource_path] Error finding {relative_path}: {e}")
        return None

def get_mapping_file() -> Optional[Path]:
    """Get the category mapping YAML file path"""
    return get_resource_path("mapping/category_mapping.yaml")

def load_category_mapping() -> dict:
    """Load category mapping from YAML file"""
    try:
        import yaml
        yaml_path = get_mapping_file()
        
        if not yaml_path:
            print("[load_category_mapping] Using fallback mapping")
            return get_fallback_mapping()
        
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        category_dict = data.get("Category_Mapping", {})
        print(f"[load_category_mapping] Loaded {len(category_dict)} categories from {yaml_path}")
        return category_dict
        
    except Exception as e:
        print(f"[load_category_mapping] Error loading mapping: {e}")
        return get_fallback_mapping()

def get_fallback_mapping() -> dict:
    """Fallback category mapping if file cannot be loaded"""
    return {
        "1": "The Witcher 3",
        "2": "Miscellaneous",
        "3": "Controller Button Layout", 
        "4": "Visuals and Graphics",
        "5": "Skills and Leveling",
        "6": "User Interface",
        "8": "Tweaks",
        "10": "Armour",
        "11": "Cheats and God items",
        "12": "Bug Fixes",
        "13": "Combat",
        "14": "Gwent",
        "15": "Modders Resources and Tutorials",
        "16": "ReShade Preset",
        "17": "Gameplay Changes",
        "18": "Models and Textures",
        "19": "Weapons",
        "20": "Signs",
        "21": "Save Games",
        "22": "Overhaul",
        "23": "Characters",
        "24": "Items",
        "25": "Camera",
        "27": "Debug Console",
        "28": "Alchemy and Crafting",
        "29": "Weapons and Armour",
        "30": "Inventory",
        "31": "Balancing",
        "32": "Immersion", 
        "33": "Utilities",
        "35": "Audio",
        "40": "Performance",
        "41": "Hair and Face",
        "42": "Quests and Adventures"
    }

def get_predefined_categories_list() -> List[str]:
    """Get sorted list of category names for UI components"""
    try:
        category_dict = load_category_mapping()
        sorted_names = [category_dict[k] for k in sorted(category_dict, key=lambda x: int(x))]
        return sorted_names or ['General']
    except Exception as e:
        print(f"[get_predefined_categories_list] Error: {e}")
        return ['General']