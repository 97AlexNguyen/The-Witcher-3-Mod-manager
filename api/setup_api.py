#!/usr/bin/env python3
"""
Nexus API Setup Utility for Witcher 3 Mod Manager
Helps users set up API key for Nexus Mods integration
"""

import os
import sys
from pathlib import Path

def get_program_root():
    """Get the root directory of the program"""
    if getattr(sys, 'frozen', False):
        # If running from executable
        return Path(sys.executable).parent
    else:
        # If running from script
        return Path(__file__).parent.parent

def create_api_folder():
    """Create api folder if it does not exist"""
    api_folder = get_program_root() / "api"
    api_folder.mkdir(exist_ok=True)
    return api_folder

def setup_api_key():
    """Setup API key for Nexus Mods"""
    print("=== Nexus Mods API Setup ===")
    print()
    print("To use the Nexus API, you need an API key from Nexus Mods:")
    print("1. Log in to https://www.nexusmods.com/")
    print("2. Go to User Settings > API keys")
    print("3. Create a new Personal API key")
    print("4. Copy the API key and paste it here")
    print()
    
    # Check current API key
    current_env_key = os.environ.get("NEXUS_API_KEY")
    api_folder = create_api_folder()
    api_file = api_folder / "api_key.txt"
    
    current_file_key = None
    if api_file.exists():
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                current_file_key = f.read().strip()
        except Exception:
            pass
    
    if current_env_key:
        print(f"✓ Environment variable NEXUS_API_KEY is set")
        print(f"  API Key: {current_env_key[:8]}...{current_env_key[-4:]}")
        
        choice = input("\nDo you want to change the API key? (y/n): ").lower()
        if choice not in ['y', 'yes']:
            return
    elif current_file_key:
        print(f"✓ API key file exists: {api_file}")
        print(f"  API Key: {current_file_key[:8]}...{current_file_key[-4:]}")
        
        choice = input("\nDo you want to change the API key? (y/n): ").lower()
        if choice not in ['y', 'yes']:
            return
    
    # Enter new API key
    while True:
        print("\nEnter your API key:")
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("API key cannot be empty!")
            continue
        
        if len(api_key) < 20:
            print("API key seems too short. Are you sure this is the correct API key?")
            choice = input("Continue? (y/n): ").lower()
            if choice not in ['y', 'yes']:
                continue
        
        # Test API key
        print("\nTesting API key...")
        if test_api_key(api_key):
            print("✓ API key is valid!")
            break
        else:
            print("✗ API key is invalid or connection error.")
            choice = input("Do you want to try again? (y/n): ").lower()
            if choice not in ['y', 'yes']:
                return
    
    # Choose save method
    print("\nChoose how to save the API key:")
    print("1. Environment Variable (NEXUS_API_KEY)")
    print("2. File (api/api_key.txt)")
    print("3. Both")
    
    while True:
        choice = input("Choice (1/2/3): ").strip()
        
        if choice == "1":
            save_to_env(api_key)
            break
        elif choice == "2":
            save_to_file(api_key, api_file)
            break
        elif choice == "3":
            save_to_env(api_key)
            save_to_file(api_key, api_file)
            break
        else:
            print("Invalid choice!")

def test_api_key(api_key):
    """Test API key with Nexus Mods"""
    try:
        import requests
        
        headers = {
            'apikey': api_key,
            'User-Agent': 'TW3-Mod-Manager-Setup/1.0',
            'Application-Name': 'TW3-Mod-Manager-Setup',
            'Application-Version': '1.0',
        }
        
        # Test with user validate endpoint
        response = requests.get(
            "https://api.nexusmods.com/v1/users/validate.json",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ API key is valid for user: {user_data.get('name', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("✗ API key is invalid")
            return False
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
            
    except ImportError:
        print("⚠ Cannot test API key - missing 'requests' library")
        print("  API key will be saved without testing")
        return True
    except Exception as e:
        print(f"✗ Error testing API key: {e}")
        return False

def save_to_env(api_key):
    """Instructions to save to environment variable"""
    print("\n=== Environment Variable Setup ===")
    print("To set the environment variable, run the following command:")
    
    if os.name == 'nt':  # Windows
        print(f'setx NEXUS_API_KEY "{api_key}"')
        print("\nOr add to System Environment Variables:")
        print(f"Variable name: NEXUS_API_KEY")
        print(f"Variable value: {api_key}")
        print("\nThen restart the application to apply changes.")
    else:  # Linux/Mac
        print(f'export NEXUS_API_KEY="{api_key}"')
        print("\nTo save permanently, add the above line to ~/.bashrc or ~/.zshrc")

def save_to_file(api_key, api_file):
    """Save API key to file"""
    try:
        with open(api_file, 'w', encoding='utf-8') as f:
            f.write(api_key)
        print(f"\n✓ API key has been saved to: {api_file}")
        
        # Set file permissions (owner read/write only)
        if os.name != 'nt':  # Unix-like systems
            os.chmod(api_file, 0o600)
            print("✓ File permissions set to safe (600)")
            
    except Exception as e:
        print(f"✗ Error saving file: {e}")

def check_current_setup():
    """Check current setup"""
    print("=== Current Setup Status ===")
    
    # Check environment variable
    env_key = os.environ.get("NEXUS_API_KEY")
    if env_key:
        print(f"✓ Environment Variable: {env_key[:8]}...{env_key[-4:]}")
    else:
        print("✗ Environment Variable: Not set")
    
    # Check file
    api_folder = get_program_root() / "api"
    api_file = api_folder / "api_key.txt"
    
    if api_file.exists():
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                file_key = f.read().strip()
            if file_key:
                print(f"✓ API Key File: {file_key[:8]}...{file_key[-4:]}")
            else:
                print("✗ API Key File: Empty")
        except Exception:
            print("✗ API Key File: Error reading")
    else:
        print("✗ API Key File: Not found")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_current_setup()
        return
    
    print("Witcher 3 Mod Manager - Nexus API Setup")
    print("=" * 40)
    
    check_current_setup()
    print()
    
    setup_api_key()
    
    print("\n" + "=" * 40)
    print("Setup complete! Restart Mod Manager to use the API.")

if __name__ == "__main__":
    main()