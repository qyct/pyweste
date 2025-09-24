"""
PyWeste main installer module.
Handles pyproject.toml configuration loading and installer orchestration.
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any

try:
    import tomllib
except ImportError:
    # For Python < 3.11, use tomli
    try:
        import tomli as tomllib
    except ImportError:
        print("ERROR: tomllib/tomli not available. Please install tomli for Python < 3.11")
        sys.exit(1)

from .gui import start_gui_installer
from .files import validate_source_files


def create_uninstaller_script(app_name: str, install_path: str) -> str:
    """
    Create an uninstallation script that requests admin privileges.
    
    Args:
        app_name: Name of the application
        install_path: Installation directory path
        
    Returns:
        str: Path to the created uninstaller script
    """
    install_path = Path(install_path)
    uninstall_script_path = install_path / "uninstall.bat"
    
    uninstall_content = f'''@echo off
:: Request administrator privileges if not already running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \\"%~f0\\"' -Verb RunAs"
    exit /b
)

echo Uninstalling {app_name}...
echo.

:: Remove desktop shortcut for current user
echo Removing desktop shortcut...
del "%USERPROFILE%\\Desktop\\{app_name}.lnk" 2>nul
if exist "%PUBLIC%\\Desktop\\{app_name}.lnk" del "%PUBLIC%\\Desktop\\{app_name}.lnk" 2>nul

:: Remove start menu shortcuts for current user
echo Removing start menu shortcuts...
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{app_name}.lnk" 2>nul

:: Remove start menu shortcuts from publisher folder
if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\*" (
    for /d %%i in ("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\*") do (
        if exist "%%i\\{app_name}.lnk" del "%%i\\{app_name}.lnk" 2>nul
    )
)

:: Remove from registry (Add/Remove Programs) - try both HKCU and HKLM
echo Removing registry entries...
reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul

echo Removing installation files...

:: Change to parent directory before removing installation folder
cd /d "{install_path.parent}"

:: Remove installation directory and all contents
rmdir /s /q "{install_path.name}" 2>nul

:: Verify removal
if exist "{install_path}" (
    echo Warning: Some files could not be removed. Please remove manually: {install_path}
    pause
) else (
    echo.
    echo {app_name} has been uninstalled successfully.
    timeout /t 3 >nul
)

exit
'''
    
    try:
        with open(uninstall_script_path, 'w', encoding='utf-8') as f:
            f.write(uninstall_content)
        print(f"INFO: Uninstaller created: {uninstall_script_path}")
        return str(uninstall_script_path)
    except Exception as e:
        print(f"ERROR: Failed to create uninstaller: {e}")
        return None


def load_toml_config(toml_path: str) -> Dict[str, Any]:
    """
    Load configuration from pyproject.toml file.
    
    Args:
        toml_path: Path to the pyproject.toml configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(toml_path, 'rb') as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"ERROR: pyproject.toml file not found: {toml_path}")
        return {}
    except Exception as e:
        print(f"ERROR: Failed to load pyproject.toml configuration: {e}")
        return {}


def parse_source_files(config: Dict[str, Any], base_path: str = None) -> List[Tuple[str, str]]:
    """
    Parse source files from pyproject.toml configuration.
    
    Args:
        config: pyproject.toml configuration dictionary
        base_path: Base path for resolving relative source paths
        
    Returns:
        List of (source, destination) tuples
    """
    source_files = []
    
    # Check for installer-specific files section
    if 'tool' in config and 'pyweste' in config['tool'] and 'files' in config['tool']['pyweste']:
        files_config = config['tool']['pyweste']['files']
        
        # Handle source_files array format
        if 'source_files' in files_config:
            for entry in files_config['source_files']:
                if isinstance(entry, list) and len(entry) == 2:
                    source, dest = entry
                    source_files.append((source, dest))
                else:
                    print(f"WARNING: Invalid file entry format: {entry}")
        
        # Handle copy dictionary format (alternative)
        if 'copy' in files_config:
            for source, dest in files_config['copy'].items():
                source_files.append((source, dest))
    
    # If no specific files configuration found, try to find common files in base_path
    if not source_files and base_path:
        base_dir = Path(base_path)
        common_patterns = [
            "*.exe", "*.dll", "*.pyd", "*.so",
            "README*", "LICENSE*", "CHANGELOG*",
            "config.ini", "settings.json"
        ]
        
        for pattern in common_patterns:
            for file_path in base_dir.glob(pattern):
                if file_path.is_file():
                    source_files.append((str(file_path), file_path.name))
        
        # Also look for directories that might contain assets
        for dir_name in ["data", "assets", "resources", "static"]:
            dir_path = base_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                source_files.append((str(dir_path) + "/", f"{dir_name}/"))
    
    # Validate and resolve paths if base_path provided
    if base_path and source_files:
        source_files = validate_source_files(source_files, base_path)
    
    return source_files


def installer() -> bool:
    """
    Main installer function that automatically detects configuration from Python executable directory.
    
    Returns:
        bool: True if installation completed successfully, False otherwise
    """
    # Use Python executable directory as bin directory
    bin_directory = os.path.dirname(sys.executable)
    
    # Go one step out of bin directory to get the main folder (bundle root)
    bundle_root = os.path.dirname(bin_directory)
    
    # Look for pyproject.toml in the bin directory
    toml_path = os.path.join(bin_directory, "pyproject.toml")
    
    print(f"INFO: Bin directory (Python executable location): {bin_directory}")
    print(f"INFO: Bundle root directory: {bundle_root}")
    print(f"INFO: Looking for configuration at: {toml_path}")
    
    # Verify that run.bat exists in bundle root
    run_bat_path = os.path.join(bundle_root, "run.bat")
    if not os.path.exists(run_bat_path):
        print(f"ERROR: run.bat not found at: {run_bat_path}")
        return False
    
    print(f"INFO: Found run.bat at: {run_bat_path}")
    
    # Load pyproject.toml configuration
    config = load_toml_config(toml_path)
    if not config:
        print("ERROR: Could not load pyproject.toml configuration")
        return False
    
    # Extract project information
    project_config = config.get('project', {})
    
    # Get installer-specific configuration if available
    pyweste_config = {}
    if 'tool' in config and 'pyweste' in config['tool']:
        pyweste_config = config['tool']['pyweste']
    
    # Extract app details from project section
    app_name = project_config.get('name', 'MyApp')
    
    # Get publisher from project authors or pyweste config
    publisher = pyweste_config.get('publisher', 'Unknown')
    if publisher == 'Unknown' and 'authors' in project_config:
        authors = project_config['authors']
        if authors and isinstance(authors[0], dict):
            publisher = authors[0].get('name', 'Unknown')
        elif authors and isinstance(authors[0], str):
            publisher = authors[0]
    
    # Get other configuration
    main_executable = pyweste_config.get('main_executable')
    
    # Look for icon.ico in the bin directory
    icon_path = os.path.join(bin_directory, "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = pyweste_config.get('icon')
        if icon_path and not os.path.isabs(icon_path):
            icon_path = os.path.join(bin_directory, icon_path)
    
    # If no icon found, set to None
    if icon_path and not os.path.exists(icon_path):
        print(f"WARNING: Icon file not found: {icon_path}")
        icon_path = None
    else:
        print(f"INFO: Using icon: {icon_path}")
    
    # Build default install path
    default_base = pyweste_config.get('default_install_path', 'C:/Program Files')
    default_install_path = str(Path(default_base) / app_name)
    
    # Create source files list - copy the entire bundle directory maintaining structure
    # This will copy everything from bundle_root, including run.bat, bin/, and any other folders
    source_files = [(bundle_root + "/", "")]  # Copy entire bundle directory contents
    
    # NOTE: We don't exclude setup.bat here since the requirement specifically states 
    # "don't copy the setup.bat file alone" - this means we should copy it as part 
    # of the bundle but not create shortcuts to it
    
    # The shortcuts will always point to run.bat (handled in gui.py)
    # The main_executable is only used for registry icon purposes
    if main_executable:
        # If main_executable is specified, ensure it includes proper path from bundle root
        if not os.path.sep in main_executable and not '/' in main_executable:
            # If it's just a filename, assume it's in the bin folder
            main_executable = f"bin/{main_executable}"
    
    print(f"INFO: Starting GUI installer for: {app_name}")
    print(f"INFO: Publisher: {publisher}")
    print(f"INFO: Default install path: {default_install_path}")
    print(f"INFO: Will copy entire bundle directory: {bundle_root}")
    print(f"INFO: Main executable (for registry): {main_executable}")
    print(f"INFO: Shortcuts will point to: run.bat")
    
    # Start GUI installer
    try:
        return start_gui_installer(
            app_name=app_name,
            default_install_path=default_install_path,
            icon_path=icon_path,
            source_files=source_files,
            publisher=publisher,
            main_executable=main_executable
        )
    except Exception as e:
        print(f"ERROR: Installer failed: {e}")
        return False


def main():
    """Command line entry point."""
    # For backwards compatibility, still accept toml path as argument
    # but prioritize auto-detection from Python executable directory
    
    success = installer()
    
    if success:
        print("INFO: Installation completed successfully!")
        sys.exit(0)
    else:
        print("ERROR: Installation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()