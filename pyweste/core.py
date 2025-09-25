import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import tomllib

from .gui import start_gui_installer
from .files import validate_source_files


def create_uninstaller_script(app_name: str, install_path: str) -> str:
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


def init_installer():
    bin_directory = os.path.dirname(sys.executable)
    bundle_root = os.path.dirname(bin_directory)
    
    toml_path = os.path.join(bin_directory, "pyproject.toml")
    config = load_toml_config(toml_path)
    app_name = config['project']['name']
    entry = config['tool']['pywest']['entry']
    icon_path = os.path.join(bin_directory, "icon.ico")
    
    default_install_path = str(Path('C:/Program Files') / app_name)
    source_files = [(bundle_root + "/", "")]  # Copy entire bundle directory contents
    
    main_executable = "bin/python.exe"
    
    print(f"INFO: Starting GUI installer for: {app_name}")
    print(f"INFO: Default install path: {default_install_path}")
    print(f"INFO: Will copy entire bundle directory: {bundle_root}")
    print(f"INFO: Main executable (for registry): {main_executable}")
    print(f"INFO: Shortcuts will point to: run.bat")
    
    # Start GUI installer
    try:
        start_gui_installer(
            app_name=app_name,
            icon_path=icon_path,
            source_files=source_files,
            main_executable=main_executable
        )
    except Exception as e:
        print(f"ERROR: Installer failed: {e}")
