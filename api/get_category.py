#!/usr/bin/env python
"""
category_auto_updater.py
------------------------
Auto-update module for Nexus Mods category mapping with scheduled updates.
UPDATED: Compatible with both development and executable environments.

Features:
=========
* Automatically updates category mapping once per day
* Runs as background service or scheduled task
* Maintains update logs and error handling
* Supports multiple games
* Graceful failure handling with fallback data
* Cross-platform scheduling support
* Compatible with exe builds

Usage:
======
# Run once (manual update)
python category_auto_updater.py

# Run with specific game
python category_auto_updater.py --game witcher3

# Install as scheduled service
python category_auto_updater.py --install-scheduler

# Check status
python category_auto_updater.py --status
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import logging
import os
import pathlib
import sys
import time
import threading
import schedule
from typing import Dict, Optional, OrderedDict

try:
    import yaml
except ImportError as _e:
    raise RuntimeError("PyYAML is required: pip install pyyaml") from _e

import requests

def sorted_category_mapping(mapping: Dict[int, str]) -> Dict[str, str]:
    """
    Return a *regular* dict with stringified keys, ordered by ID ascending.
    """
    return {str(k): mapping[k] for k in sorted(mapping, key=int)}

def get_resource_paths():
    """Get resource paths that work in both development and executable environments."""
    
    # Determine base directory based on execution environment
    if getattr(sys, 'frozen', False):
        # Running from executable
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            base_dir = pathlib.Path(sys._MEIPASS)
        else:
            # cx_Freeze - resources are in lib folder or next to exe
            exe_dir = pathlib.Path(sys.executable).parent
            # Try lib folder first, then exe directory
            if (exe_dir / "lib" / "mapping").exists():
                base_dir = exe_dir / "lib"
            else:
                base_dir = exe_dir
    else:
        # Running from script - go up 1 level from api/get_category.py to project root
        base_dir = pathlib.Path(__file__).resolve().parents[1]
    
    # Define paths
    mapping_dir = base_dir / "mapping"
    yaml_path = mapping_dir / "category_mapping.yaml"
    
    # For logs, always use a writable location
    if getattr(sys, 'frozen', False):
        # For exe, use a folder next to exe or user data folder
        log_dir = pathlib.Path(sys.executable).parent / "logs"
    else:
        log_dir = base_dir / "logs"
    
    log_file = log_dir / "category_updater.log"
    status_file = mapping_dir / "update_status.json"
    
    return {
        'base_dir': base_dir,
        'mapping_dir': mapping_dir,
        'yaml_path': yaml_path,
        'log_dir': log_dir,
        'log_file': log_file,
        'status_file': status_file
    }

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_GAME = "witcher3"
CACHE_EXPIRY = _dt.timedelta(hours=23)  # Update mỗi 23 giờ để đảm bảo daily update
UPDATE_HOUR = 2  # Cập nhật lúc 2 giờ sáng mỗi ngày
MAX_RETRIES = 3
RETRY_DELAY = 300  # 5 phút

# Get paths using resource-aware function
PATHS = get_resource_paths()
ROOT_DIR = PATHS['base_dir']
MAPPING_DIR = PATHS['mapping_dir']
YAML_PATH = PATHS['yaml_path']
LOG_DIR = PATHS['log_dir']
LOG_FILE = PATHS['log_file']
STATUS_FILE = PATHS['status_file']

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    try:
        LOG_DIR.mkdir(exist_ok=True, parents=True)
    except PermissionError:
        # If can't create in intended location, use temp dir
        import tempfile
        global LOG_FILE
        LOG_FILE = pathlib.Path(tempfile.gettempdir()) / "tw3mm_category_updater.log"
        print(f"Using fallback log location: {LOG_FILE}")
    
    logger = logging.getLogger("category_updater")
    logger.setLevel(logging.INFO)
    
    # File handler với rotation
    try:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Could not setup file logging: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ---------------------------------------------------------------------------
# Core updater class
# ---------------------------------------------------------------------------
class CategoryUpdater:
    """Main category updater class with resource-aware paths."""
    
    def __init__(self, game: str = DEFAULT_GAME):
        self.game = game
        self.status = self._load_status()
        
        # Log the paths being used
        logger.info(f"Using mapping directory: {MAPPING_DIR}")
        logger.info(f"Using YAML path: {YAML_PATH}")
        logger.info(f"Running from executable: {getattr(sys, 'frozen', False)}")
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or file."""
        # Try environment variable
        key = os.getenv("NEXUS_API_KEY")
        if key:
            return key.strip()
        
        # Try file in multiple locations
        possible_key_files = [
            pathlib.Path(__file__).parent / "api_key.txt",  # api/api_key.txt (development)
            ROOT_DIR / "api" / "api_key.txt",  # project_root/api/api_key.txt
            pathlib.Path(sys.executable).parent / "api_key.txt",  # next to exe
        ]
        
        for key_file in possible_key_files:
            if key_file.exists():
                try:
                    api_key = key_file.read_text(encoding="utf-8").strip()
                    if api_key:
                        logger.info(f"Found API key in: {key_file}")
                        return api_key
                except Exception as e:
                    logger.warning(f"Could not read API key file {key_file}: {e}")
        
        return None
    
    def _load_status(self) -> Dict:
        """Load update status from file."""
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not read status file: {e}")
        
        return {
            "last_update": None,
            "last_success": None,
            "update_count": 0,
            "error_count": 0,
            "last_error": None
        }
    
    def _save_status(self, success: bool = True, error_msg: str = None):
        """Save update status to file."""
        now = _dt.datetime.now().isoformat()
        
        if success:
            self.status["last_success"] = now
            self.status["update_count"] += 1
        else:
            self.status["error_count"] += 1
            self.status["last_error"] = error_msg
        
        self.status["last_update"] = now
        
        try:
            MAPPING_DIR.mkdir(exist_ok=True, parents=True)
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save status: {e}")
    
    def _fetch_categories_from_api(self) -> Optional[Dict[int, str]]:
        """Fetch categories from Nexus API."""
        api_key = self._get_api_key()
        if not api_key:
            logger.warning("No API key found. Set NEXUS_API_KEY or create api_key.txt file")
            return None
        
        url = f"https://api.nexusmods.com/v1/games/{self.game}.json"
        headers = {
            "apikey": api_key,
            "Accept": "application/json",
            "User-Agent": "TW3-Mod-Manager-CategoryUpdater/1.0"
        }
        
        try:
            logger.info(f"Fetching categories for {self.game} from Nexus API...")
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            categories = {c["category_id"]: c["name"] for c in data["categories"]}
            logger.info(f"Successfully fetched {len(categories)} categories")
            return categories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during API fetch: {e}")
            return None
    
    def _load_current_mapping(self) -> Optional[Dict[int, str]]:
        """Load current mapping from file."""
        if not YAML_PATH.exists():
            return None
        
        try:
            doc = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8")) or {}
            return {int(k): v for k, v in doc.get("Category_Mapping", {}).items()}
        except Exception as e:
            logger.error(f"Could not load current mapping: {e}")
            return None
    
    def _save_mapping(self, mapping: Dict[int, str]) -> bool:
        """Save mapping to YAML file (sorted numerically)."""
        try:
            MAPPING_DIR.mkdir(exist_ok=True, parents=True)

            data = {
                "Category_Mapping": sorted_category_mapping(mapping)
            }

            # Backup existing file
            if YAML_PATH.exists():
                backup = YAML_PATH.with_suffix(".yaml.backup")
                try:
                    YAML_PATH.rename(backup)
                    logger.info("Backup written ➜ %s", backup)
                except Exception as e:
                    logger.warning(f"Could not create backup: {e}")

            # Write new file
            YAML_PATH.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8"
            )
            logger.info("Mapping saved ➜ %s", YAML_PATH)
            return True

        except Exception as exc:
            logger.error("Could not save mapping: %s", exc)
            return False
    
    def _should_update(self) -> bool:
        """Check if update is needed."""
        if not YAML_PATH.exists():
            logger.info("No mapping file exists, update needed")
            return True
        
        try:
            mtime = _dt.datetime.fromtimestamp(YAML_PATH.stat().st_mtime)
            age = _dt.datetime.now() - mtime
            
            if age > CACHE_EXPIRY:
                logger.info(f"Mapping is {age} old, update needed")
                return True
            else:
                logger.info(f"Mapping is {age} old, still fresh")
                return False
                
        except Exception as e:
            logger.warning(f"Could not check file age: {e}, assuming update needed")
            return True
    
    def update_categories(self, force: bool = False) -> bool:
        """Update categories if needed."""
        if not force and not self._should_update():
            logger.info("Update not needed, skipping")
            return True
        
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Fetch new categories
                new_categories = self._fetch_categories_from_api()
                if not new_categories:
                    raise Exception("Could not fetch categories from API")
                
                # Compare with existing
                current_categories = self._load_current_mapping()
                if current_categories == new_categories:
                    logger.info("Categories unchanged, no update needed")
                    self._save_status(success=True)  # Still count as success
                    return True
                
                # Save new mapping
                if self._save_mapping(new_categories):
                    changes = self._log_changes(current_categories, new_categories)
                    logger.info(f"Successfully updated categories. Changes: {changes}")
                    self._save_status(success=True)
                    return True
                else:
                    raise Exception("Could not save new mapping")
                    
            except Exception as e:
                retry_count += 1
                error_msg = f"Update attempt {retry_count} failed: {e}"
                logger.error(error_msg)
                
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error("All retry attempts failed")
                    self._save_status(success=False, error_msg=str(e))
                    return False
        
        return False
    
    def _log_changes(self, old: Optional[Dict[int, str]], new: Dict[int, str]) -> Dict[str, int]:
        """Log changes between old and new categories."""
        if not old:
            return {"added": len(new), "modified": 0, "removed": 0}
        
        added = set(new.keys()) - set(old.keys())
        removed = set(old.keys()) - set(new.keys())
        modified = {k for k in old.keys() & new.keys() if old[k] != new[k]}
        
        changes = {
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed)
        }
        
        if added:
            logger.info(f"Added categories: {[f'{k}: {new[k]}' for k in added]}")
        if modified:
            logger.info(f"Modified categories: {[f'{k}: {old[k]} -> {new[k]}' for k in modified]}")
        if removed:
            logger.info(f"Removed categories: {[f'{k}: {old[k]}' for k in removed]}")
        
        return changes
    
    def get_status(self) -> Dict:
        """Get current updater status."""
        status = self.status.copy()
        status["mapping_exists"] = YAML_PATH.exists()
        status["api_key_available"] = self._get_api_key() is not None
        status["yaml_path"] = str(YAML_PATH)
        status["mapping_dir"] = str(MAPPING_DIR)
        status["is_frozen"] = getattr(sys, 'frozen', False)
        
        if YAML_PATH.exists():
            mtime = _dt.datetime.fromtimestamp(YAML_PATH.stat().st_mtime)
            status["mapping_age"] = str(_dt.datetime.now() - mtime)
            status["mapping_last_modified"] = mtime.isoformat()
        
        return status

# ---------------------------------------------------------------------------
# Scheduler functions (unchanged)
# ---------------------------------------------------------------------------
def run_daily_update(game: str = DEFAULT_GAME):
    """Run daily category update."""
    logger.info("Starting scheduled category update")
    updater = CategoryUpdater(game)
    success = updater.update_categories()
    
    if success:
        logger.info("Scheduled update completed successfully")
    else:
        logger.error("Scheduled update failed")
    
    return success

def start_scheduler(game: str = DEFAULT_GAME):
    """Start the background scheduler."""
    logger.info(f"Starting category updater scheduler (daily at {UPDATE_HOUR}:00)")
    
    # Schedule daily update
    schedule.every().day.at(f"{UPDATE_HOUR:02d}:00").do(run_daily_update, game)
    
    # Run once immediately if mapping doesn't exist
    if not YAML_PATH.exists():
        logger.info("No mapping exists, running initial update")
        run_daily_update(game)
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

def install_system_scheduler(game: str = DEFAULT_GAME):
    """Install system scheduler (platform-specific)."""
    script_path = pathlib.Path(__file__).resolve()
    
    if sys.platform == "win32":
        # Windows Task Scheduler
        task_name = "Witcher3ModManager_CategoryUpdater"
        cmd = f'schtasks /create /tn "{task_name}" /tr "python \\"{script_path}\\" --game {game}" /sc daily /st 02:00 /f'
        
        try:
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Successfully installed Windows scheduled task: {task_name}")
                logger.info("Task will run daily at 2:00 AM")
                return True
            else:
                logger.error(f"Failed to install scheduled task: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error installing Windows scheduler: {e}")
            return False
    
    elif sys.platform in ["linux", "darwin"]:
        # Crontab
        cron_entry = f"0 2 * * * python {script_path} --game {game} >/dev/null 2>&1"
        logger.info("To install on Linux/Mac, add this crontab entry:")
        logger.info(f"  {cron_entry}")
        logger.info("Run: crontab -e")
        return True
    
    else:
        logger.warning(f"Automatic scheduler installation not supported on {sys.platform}")
        logger.info("Please manually schedule the script to run daily")
        return False

# ---------------------------------------------------------------------------
# CLI interface (unchanged)
# ---------------------------------------------------------------------------
def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Auto-update Nexus Mods category mapping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python category_auto_updater.py                    # Run once
  python category_auto_updater.py --force            # Force update
  python category_auto_updater.py --scheduler        # Start background scheduler
  python category_auto_updater.py --install          # Install system scheduler
  python category_auto_updater.py --status           # Check status
        """
    )
    
    parser.add_argument("--game", default=DEFAULT_GAME, 
                       help="Game domain name (default: witcher3)")
    parser.add_argument("--force", action="store_true",
                       help="Force update even if cache is fresh")
    parser.add_argument("--scheduler", action="store_true",
                       help="Start background scheduler")
    parser.add_argument("--install", action="store_true",
                       help="Install system scheduler")
    parser.add_argument("--status", action="store_true",
                       help="Show updater status")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger("category_updater").setLevel(logging.DEBUG)
    
    updater = CategoryUpdater(args.game)
    
    try:
        if args.status:
            status = updater.get_status()
            print("Category Updater Status:")
            print("=" * 25)
            for key, value in status.items():
                print(f"{key}: {value}")
            return
        
        if args.install:
            success = install_system_scheduler(args.game)
            sys.exit(0 if success else 1)
        
        if args.scheduler:
            start_scheduler(args.game)
        else:
            # Run once
            success = updater.update_categories(force=args.force)
            if success:
                logger.info("Update completed successfully")
                sys.exit(0)
            else:
                logger.error("Update failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()