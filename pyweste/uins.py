from pathlib import Path


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