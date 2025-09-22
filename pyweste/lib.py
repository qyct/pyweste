import shutil
import os
import sys
import ctypes
import winreg
import json
from pathlib import Path
import win32com.client
import pythoncom

def is_admin():
    """Check if the script is running with admin privileges (Windows only)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def copy_file_admin(src: str, dst: str):
    """
    Copies a file from src to dst with admin privileges on Windows.
    If not running as admin, prompts the user to elevate via UAC.
    """
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Source file not found: {src}")

    if is_admin():
        # Already admin, perform the copy
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied '{src}' -> '{dst}' successfully.")
    else:
        # Relaunch script as admin
        print("Requesting admin privileges...")
        params = f'"{__file__}" "{src}" "{dst}"'
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as e:
            print("Failed to elevate privileges:", e)

def create_desktop_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, description: str = ""):
    """Create a desktop shortcut in one line."""
    try:
        pythoncom.CoInitialize()
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        shortcut_path = desktop / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.Description = description
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        shortcut.save()
        print(f"Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create desktop shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def create_startmenu_shortcut(target_path: str, shortcut_name: str, icon_path: str = None, description: str = ""):
    """Create a start menu shortcut in one line."""
    try:
        pythoncom.CoInitialize()
        start_menu = Path(os.path.expandvars("%APPDATA%")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        shortcut_path = start_menu / f"{shortcut_name}.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = target_path
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.Description = description
        if icon_path and os.path.exists(icon_path):
            shortcut.IconLocation = icon_path
        shortcut.save()
        print(f"Start menu shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Failed to create start menu shortcut: {e}")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def add_to_programs_and_features(app_name: str, install_path: str, uninstall_command: str, 
                                version: str = "1.0.0", publisher: str = "", icon_path: str = ""):
    """Add application to Add/Remove Programs (Programs and Features) in one line."""
    try:
        if not is_admin():
            print("Admin privileges required to add to Programs and Features")
            return False
            
        # Registry key for uninstall information
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            # Required values
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, app_name)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, uninstall_command)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_path)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version)
            
            # Optional values
            if publisher:
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, publisher)
            if icon_path and os.path.exists(icon_path):
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
                
            # Additional useful values
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            
            # Try to get size (optional)
            try:
                size = sum(f.stat().st_size for f in Path(install_path).rglob('*') if f.is_file())
                size_kb = size // 1024
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, size_kb)
            except:
                pass
                
        print(f"Added '{app_name}' to Programs and Features")
        return True
    except Exception as e:
        print(f"Failed to add to Programs and Features: {e}")
        return False

def create_uninstall_script(app_name: str, install_path: str, script_path: str = None):
    """Create an uninstall script for the application."""
    if script_path is None:
        script_path = Path(install_path) / "uninstall.exe"
    
    uninstall_content = f'''import os
import sys
import shutil
import winreg
from pathlib import Path
import win32com.client
import pythoncom

def remove_shortcuts():
    """Remove desktop and start menu shortcuts."""
    try:
        pythoncom.CoInitialize()
        
        # Remove desktop shortcut
        desktop = Path(os.path.expanduser("~")) / "Desktop"
        desktop_shortcut = desktop / "{app_name}.lnk"
        if desktop_shortcut.exists():
            desktop_shortcut.unlink()
            print("Removed desktop shortcut")
            
        # Remove start menu shortcut
        start_menu = Path(os.path.expandvars("%APPDATA%")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        startmenu_shortcut = start_menu / "{app_name}.lnk"
        if startmenu_shortcut.exists():
            startmenu_shortcut.unlink()
            print("Removed start menu shortcut")
    except Exception as e:
        print(f"Error removing shortcuts: {{e}}")
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def remove_registry_entry():
    """Remove entry from Programs and Features."""
    try:
        key_path = "SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{app_name}"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        print("Removed from Programs and Features")
    except Exception as e:
        print(f"Error removing registry entry: {{e}}")

def main():
    install_path = "{install_path}"
    
    print("Uninstalling {app_name}...")
    
    # Remove shortcuts
    remove_shortcuts()
    
    # Remove registry entry
    remove_registry_entry()
    
    # Remove installation directory
    try:
        if Path(install_path).exists():
            shutil.rmtree(install_path)
            print(f"Removed installation directory: {{install_path}}")
    except Exception as e:
        print(f"Error removing installation directory: {{e}}")
    
    print("Uninstallation completed!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open(script_path, 'w') as f:
            f.write(uninstall_content)
        print(f"Uninstall script created: {script_path}")
        return str(script_path)
    except Exception as e:
        print(f"Failed to create uninstall script: {e}")
        return None

def install_app(app_name: str, source_files: list, install_path: str = None, 
                desktop_shortcut: bool = True, startmenu_shortcut: bool = True,
                add_to_programs: bool = True, main_executable: str = None,
                icon_path: str = None, version: str = "1.0.0", publisher: str = ""):
    """
    Complete application installer in one function.
    
    Args:
        app_name: Name of the application
        source_files: List of (source_path, relative_dest_path) tuples
        install_path: Installation directory (default: C:/Program Files/{app_name})
        desktop_shortcut: Create desktop shortcut
        startmenu_shortcut: Create start menu shortcut
        add_to_programs: Add to Programs and Features
        main_executable: Path to main executable (for shortcuts)
        icon_path: Path to icon file
        version: Application version
        publisher: Publisher name
    """
    if install_path is None:
        install_path = f"C:/Program Files/{app_name}"
    
    install_path = Path(install_path)
    
    try:
        # Create installation directory
        install_path.mkdir(parents=True, exist_ok=True)
        print(f"Created installation directory: {install_path}")
        
        # Copy files
        for src, rel_dest in source_files:
            dest = install_path / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            if is_admin():
                shutil.copy2(src, dest)
            else:
                copy_file_admin(src, str(dest))
        
        print("Files copied successfully")
        
        # Determine main executable path
        if main_executable is None:
            # Try to find an .exe file
            exe_files = list(install_path.rglob("*.exe"))
            if exe_files:
                main_executable = str(exe_files[0])
            else:
                print("Warning: No main executable specified or found")
                main_executable = str(install_path / f"{app_name}.exe")
        else:
            main_executable = str(install_path / main_executable)
        
        # Create uninstall script
        uninstall_script = create_uninstall_script(app_name, str(install_path))
        
        # Create shortcuts
        if desktop_shortcut and main_executable:
            create_desktop_shortcut(main_executable, app_name, icon_path, f"{app_name} Application")
        
        if startmenu_shortcut and main_executable:
            create_startmenu_shortcut(main_executable, app_name, icon_path, f"{app_name} Application")
        
        # Add to Programs and Features
        if add_to_programs and uninstall_script:
            add_to_programs_and_features(
                app_name, str(install_path), uninstall_script,
                version, publisher, icon_path
            )
        
        print(f"Installation of '{app_name}' completed successfully!")
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False

def remove_from_programs_and_features(app_name: str):
    """Remove application from Programs and Features."""
    try:
        if not is_admin():
            print("Admin privileges required to remove from Programs and Features")
            return False
            
        key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}"
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        print(f"Removed '{app_name}' from Programs and Features")
        return True
    except Exception as e:
        print(f"Failed to remove from Programs and Features: {e}")
        return False