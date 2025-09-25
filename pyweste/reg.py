import os
import winreg
from pathlib import Path
from .utils import create_shortcut, calculate_directory_size


def create_uninstaller_script(app_name: str, install_path: str) -> str:
    """Create an uninstallation script."""
    install_path = Path(install_path)
    uninstall_script_path = install_path / "uninstall.bat"
    
    uninstall_content = f'''@echo off
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \\"%~f0\\"' -Verb RunAs"
    exit /b
)

echo Uninstalling {app_name}...

del "%USERPROFILE%\\Desktop\\{app_name}.lnk" 2>nul
del "%PUBLIC%\\Desktop\\{app_name}.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{app_name}.lnk" 2>nul

reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul

cd /d "{install_path.parent}"
rmdir /s /q "{install_path.name}" 2>nul

echo {app_name} has been uninstalled successfully.
timeout /t 3 >nul
'''
    
    try:
        with open(uninstall_script_path, 'w', encoding='utf-8') as f:
            f.write(uninstall_content)
        return str(uninstall_script_path)
    except Exception as e:
        print(f"ERROR: Failed to create uninstaller: {e}")
        return None


def add_registry_entry(app_name: str, install_path: str, uninstall_script_path: str, icon_path: str = None) -> bool:
    """Add registry entry for Add/Remove Programs."""
    try:
        total_size = calculate_directory_size(install_path)
        size_kb = total_size // 1024 if total_size > 0 else 1024
        
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        
        # Try HKCU first (no admin required)
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstall_script_path))
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                
                if icon_path and os.path.exists(icon_path):
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            
            print(f"INFO: Registry entry created for {app_name}")
            return True
            
        except Exception:
            # Try HKLM (requires admin)
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(uninstall_script_path))
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
                
                if icon_path and os.path.exists(icon_path):
                    winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            
            print(f"INFO: Registry entry created for {app_name} in HKLM")
            return True
        
    except Exception as e:
        print(f"ERROR: Failed to add registry entry: {e}")
        return False


def setup_entries(app_name: str, install_path: str, executable: str, icon_path: str = None,
                   create_desktop: bool = False, create_startmenu: bool = False, add_registry: bool = False) -> bool:
    """Add application to Windows registry and create shortcuts."""
    success = True
    
    # Create desktop shortcut
    if create_desktop:
        desktop_path = str(Path.home() / "Desktop" / f"{app_name}.lnk")
        if not create_shortcut(executable, desktop_path, icon_path):
            success = False
    
    # Create start menu shortcut
    if create_startmenu:
        appdata = os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
        startmenu_path = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / f"{app_name}.lnk"
        if not create_shortcut(executable, str(startmenu_path), icon_path):
            success = False
    
    # Add to registry (Add/Remove Programs)
    if add_registry:
        uninstall_script_path = create_uninstaller_script(app_name, install_path)
        if uninstall_script_path:
            if not add_registry_entry(app_name, install_path, uninstall_script_path, icon_path):
                success = False
        else:
            success = False
    
    return success