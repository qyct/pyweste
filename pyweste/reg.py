import os
import winreg
from pathlib import Path
from .utils import create_shortcut, calculate_directory_size
from .uins import create_uninstaller_script

def add_registry_entry(app_name: str, install_path: str, uninstall_script_path: str, icon_path: str = None) -> bool:
    """Add registry entry for Add/Remove Programs."""
    try:
        total_size = calculate_directory_size(install_path)
        size_kb = total_size // 1024 if total_size > 0 else 1024
        
        registry_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        
        # Do HKCU only (no admin required)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_path))
            winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)

            uninstall_cmd = f'cmd.exe /c "{uninstall_script_path}"'
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_cmd)

        print(f"INFO: Registry entry created for {app_name}")
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