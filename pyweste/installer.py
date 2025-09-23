from pathlib import Path

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
    powershell -Command "Start-Process cmd -ArgumentList '/c \"%~f0\"' -Verb RunAs"
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