'''Witcher 3 Mod Manager main module'''
import sys
from argparse import ArgumentParser
from os import environ
import threading

def init_category_updater():
    """Initialize category updater in background with proper error handling"""
    try:
        # Try to import CategoryUpdater with fallback handling
        try:
            from api.get_category import CategoryUpdater
        except ImportError:
            # Fallback for different import paths in exe
            try:
                import sys
                import os
                
                # Add possible paths where the module might be
                if getattr(sys, 'frozen', False):
                    # Running from executable
                    exe_dir = os.path.dirname(sys.executable)
                    possible_paths = [
                        os.path.join(exe_dir, 'lib'),
                        os.path.join(exe_dir, 'lib', 'api'),
                        exe_dir
                    ]
                    
                    for path in possible_paths:
                        if path not in sys.path:
                            sys.path.insert(0, path)
                
                from api.get_category import CategoryUpdater
            except ImportError as e:
                print(f"[CategoryUpdater] Could not import CategoryUpdater: {e}")
                print("[CategoryUpdater] Category auto-update will be disabled")
                return
        
        # Initialize updater
        updater = CategoryUpdater("witcher3")
        
        def background_update():
            try:
                print("[CategoryUpdater] Checking for category updates...")
                success = updater.update_categories()
                if success:
                    print("[CategoryUpdater] Categories updated successfully")
                else:
                    print("[CategoryUpdater] Category update failed")
            except Exception as e:
                print(f"[CategoryUpdater] Error during update: {e}")
        
        # Run in separate thread to not block GUI startup
        update_thread = threading.Thread(target=background_update, daemon=True)
        update_thread.start()
        print("[CategoryUpdater] Background update started")
        
    except Exception as e:
        print(f"[CategoryUpdater] Failed to initialize: {e}")
        print("[CategoryUpdater] Continuing without auto-update")

def setup_environment():
    """Setup environment variables and paths"""
    # Correct screen scaling
    if "QT_DEVICE_PIXEL_RATIO" in environ:
        del environ["QT_DEVICE_PIXEL_RATIO"]
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def parse_arguments():
    """Parse command line arguments"""
    documentsPath: str = ''
    gamePath: str = ''
    configPath: str = ''
    
    try:
        from src.util.util import getVersionString
        
        parser = ArgumentParser(description=getVersionString())
        parser.add_argument(
            "-d", "--debug", dest="debug", action="store_true", default=False,
            help="show debug information on errors")
        parser.add_argument(
            "-v", "--version", dest="version", action="store_true", default=False,
            help="show version information and exit")
        
        # Category updater arguments
        parser.add_argument(
            "--update-categories", action="store_true",
            help="Update categories and exit")
        parser.add_argument(
            "--force-update-categories", action="store_true", 
            help="Force update categories and exit")
        
        dirs = parser.add_argument_group(title='start overrides')
        dirs.add_argument(
            "-u", "--userdocuments", dest="userdocuments", type=str, default="",
            help="override the documents path")
        dirs.add_argument(
            "-g", "--game", dest="game", type=str, default="",
            help="override the game path")
        dirs.add_argument(
            "-c", "--config", dest="config", type=str, default="",
            help="override the config path")
        
        args = parser.parse_args()
        
        if args.version:
            print(getVersionString())
            sys.exit(0)
        
        # Handle category update commands
        if args.update_categories or args.force_update_categories:
            handle_category_update_command(args.force_update_categories)
            sys.exit(0)
        
        return args.debug, args.userdocuments, args.game, args.config
        
    except Exception as e:
        print(f"Error parsing arguments: {e}")
        return False, '', '', ''

def handle_category_update_command(force=False):
    """Handle category update command line arguments"""
    try:
        from api.get_category import CategoryUpdater
        print("Running category update...")
        
        updater = CategoryUpdater("witcher3")
        success = updater.update_categories(force=force)
        
        if success:
            print("✓ Category update completed successfully")
        else:
            print("✗ Category update failed")
            sys.exit(1)
            
    except ImportError:
        print("✗ CategoryUpdater not available")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Category update error: {e}")
        sys.exit(1)

def initialize_application():
    """Initialize the main application"""
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        from src.configuration.config import Configuration
        from src.core.model import Model
        from src.globals import data
        from src.gui.alerts import MessageAlertOtherInstance, MessageInitializationFailed
        from src.gui.main_widget import CustomMainWidget
        from src.gui.main_window import CustomMainWindow
        from src.gui.themes import get_dark_palette, get_light_palette, get_system_palette
        from src.util.util import formatUserError, translateToChosenLanguage, fixUserSettingsDuplicateBrackets, reconfigureGamePath,getIcon

        # Parse arguments
        debug, documentsPath, gamePath, configPath = parse_arguments()
        
        # Setup data
        data.app = QApplication(sys.argv)
        data.debug = debug
        data.config = Configuration(documentsPath, gamePath, configPath)
        
        # Setup theme
        data.app.setStyle("Fusion")
        data.dark_palette = get_dark_palette()
        data.light_palette = get_light_palette()

        if data.config.theme == 'Dark':
            data.app.setPalette(data.dark_palette)
        elif data.config.theme == 'Light':
            data.app.setPalette(data.light_palette)
        else:  # Follow System
            data.app.setPalette(get_system_palette())

        # Setup language
        translateToChosenLanguage()

        # Verify game path
        if not Configuration.getCorrectGamePath(data.config.gameexe):
            if not reconfigureGamePath():
                sys.exit(1)

        # Initialize model
        try:
            modModel = Model()
        except IOError as err:
            print(err, file=sys.stderr)
            if MessageAlertOtherInstance() == QMessageBox.Yes:
                modModel = Model(ignorelock=True)
            else:
                sys.exit(1)
        except Exception as e:
            MessageInitializationFailed(formatUserError(e))
            sys.exit(1)

        # Fix user settings
        fixUserSettingsDuplicateBrackets()

        # Create UI
        mainWindow = CustomMainWindow()
        mainWidget = CustomMainWidget(mainWindow, modModel)
        mainWidget.checkTheme()
        mainWindow.dropCallback = mainWidget.installModFiles
        data.app.setWindowIcon(getIcon("w3a.ico"))

        # Show window
        mainWindow.show()

        # Run application
        ret = data.app.exec()
        
        # Cleanup
        data.config.saveWindowSettings(mainWidget, mainWindow)
        data.config.write_priority().join()
        data.config.write_config().join()
        modModel.write()

        return ret
        
    except Exception as e:
        import traceback
        from src.util.util import formatUserError
        
        print(formatUserError(e), file=sys.stderr)
        
        try:
            if sys.platform == "win32":
                import win32api  # pylint: disable=import-error # type: ignore
                win32api.MessageBox(
                    0, f'{str(e)}\n\n{traceback.format_exc()}', "Unexpected Error", 0x10)
        except Exception as x:
            print("Failed to show error message: " + formatUserError(x), file=sys.stderr)
        
        return 1

if __name__ == "__main__":
    try:
        # Setup environment
        setup_environment()
        
        # Initialize category updater in background (non-blocking)
        init_category_updater()
        
        # Run main application
        exit_code = initialize_application()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)