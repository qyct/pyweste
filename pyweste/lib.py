"""
Enhanced main library module for pyweste installer
Integrates all components: copy, link, reg, and gui functionality
"""

from pathlib import Path
from .copy import copy_files_with_progress, copy_directory_tree, is_admin
from .link import create_shortcuts_for_app, remove_shortcuts_for_app
from .reg import add_to_programs_and_features, remove_from_programs_and_features


def create_uninstall_script(app_name: str, install_path: str, script_path: str = None):
    """Create an uninstall script for the application."""
    if script_path is None:
        script_path = Path(install_path) / "uninstall.bat"
    
    install_path = Path(install_path)
    
    uninstall_content = f'''@echo off
:: Uninstaller for {app_name}

:: Check for admin privileges
>nul 2>&1 "%SYSTEMROOT%\\system32\\cacls.exe" "%SYSTEMROOT%\\system32\\config\\system"

:: If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges to uninstall {app_name}...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\\getadmin.vbs"
    set params = %*:""=""
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0"" %params%", "", "runas", 1 >> "%temp%\\getadmin.vbs"
    "%temp%\\getadmin.vbs"
    del "%temp%\\getadmin.vbs"
    exit /B

:gotAdmin
    pushd "%CD%"
    CD /D "%~dp0"

echo Uninstalling {app_name}...
echo.

:: Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\\Desktop\\{app_name}.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{app_name}.lnk" 2>nul

:: Remove from Add/Remove Programs
echo Removing from Add/Remove Programs...
reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul

:: Change to parent directory before deleting
echo Removing application files...
cd /d "{install_path.parent}"

:: Force delete the installation directory with retry
set "TARGET_DIR={install_path.name}"

:: First attempt - normal deletion
rmdir /s /q "%TARGET_DIR%" 2>nul

:: Check if directory still exists and force delete
if exist "%TARGET_DIR%" (
    echo Forcing removal of remaining files...
    :: Kill any processes that might be locking files
    taskkill /f /im python.exe 2>nul
    taskkill /f /im pythonw.exe 2>nul
    :: Wait a moment
    timeout /t 2 /nobreak >nul
    :: Try again with force
    rmdir /s /q "%TARGET_DIR%" 2>nul
)

:: Final check
if exist "%TARGET_DIR%" (
    echo Warning: Some files could not be removed. They may be in use.
    echo Location: {install_path}
    echo You can manually delete this folder after closing any running applications.
) else (
    echo {app_name} has been successfully uninstalled.
)

echo.
echo Uninstall process completed.
pause
'''
    
    try:
        with open(script_path, 'w') as f:
            f.write(uninstall_content)
        print(f"Uninstall script created: {script_path}")
        return str(script_path)
    except Exception as e:
        print(f"Failed to create uninstall script: {e}")
        return None


def install_app(app_name: str, source_files: list = None, bundle_dir: str = None,
                install_path: str = None, desktop_shortcut: bool = True, 
                startmenu_shortcut: bool = True, add_to_programs: bool = True, 
                main_executable: str = None, icon_path: str = None, 
                version: str = "1.0.0", publisher: str = "", 
                startmenu_folder: str = None, progress_callback=None):
    """
    Complete application installer in one function.
    
    Args:
        app_name: Name of the application
        source_files: List of (source_path, relative_dest_path) tuples
        bundle_dir: Directory containing complete application bundle
        install_path: Installation directory (default: C:/Program Files/{app_name})
        desktop_shortcut: Create desktop shortcut
        startmenu_shortcut: Create start menu shortcut
        add_to_programs: Add to Programs and Features
        main_executable: Path to main executable (for shortcuts)
        icon_path: Path to icon file
        version: Application version
        publisher: Publisher name
        startmenu_folder: Subfolder in start menu
        progress_callback: Function to call with progress updates
    """
    if install_path is None:
        install_path = f"C:/Program Files/{app_name}"
    
    install_path = Path(install_path)
    
    try:
        # Copy files or bundle directory
        if bundle_dir:
            print(f"Installing bundle from: {bundle_dir}")
            success = copy_directory_tree(
                bundle_dir, 
                install_path,
                exclude_patterns=['*.pyc', '__pycache__', '.git', 'setup.py'],
                progress_callback=progress_callback
            )
        else:
            print(f"Installing files to: {install_path}")
            success = copy_files_with_progress(
                source_files or [], 
                install_path, 
                progress_callback
            )
        
        if not success:
            return False
        
        # Determine main executable path
        if main_executable is None:
            # Try to find an .exe file or .bat file
            exe_files = list(install_path.rglob("*.exe"))
            bat_files = list(install_path.rglob("*.bat"))
            
            if exe_files:
                main_executable = str(exe_files[0])
            elif bat_files:
                main_executable = str(bat_files[0])
            else:
                print("Warning: No main executable specified or found")
                main_executable = str(install_path / f"{app_name}.exe")
        else:
            main_executable = str(install_path / main_executable)
        
        # Create uninstall script
        uninstall_script = create_uninstall_script(app_name, str(install_path))
        
        # Create shortcuts
        if (desktop_shortcut or startmenu_shortcut) and main_executable:
            shortcut_results = create_shortcuts_for_app(
                app_name, main_executable, icon_path,
                desktop_shortcut, startmenu_shortcut, startmenu_folder
            )
            
            if not any(shortcut_results.values()):
                print("Warning: Failed to create shortcuts")
        
        # Add to Programs and Features
        if add_to_programs and uninstall_script:
            # Try system-wide first, fall back to current user
            success = add_to_programs_and_features(
                app_name, str(install_path), uninstall_script,
                version, publisher, icon_path, use_current_user=False
            )
            
            if not success:
                print("Falling back to current user registry...")
                add_to_programs_and_features(
                    app_name, str(install_path), uninstall_script,
                    version, publisher, icon_path, use_current_user=True
                )
        
        print(f"Installation of '{app_name}' completed successfully!")
        return True
        
    except Exception as e:
        print(f"Installation failed: {e}")
        return False


def uninstall_app(app_name: str, install_path: str = None, startmenu_folder: str = None):
    """
    Uninstall an application completely.
    
    Args:
        app_name: Name of the application
        install_path: Installation directory (if known)
        startmenu_folder: Subfolder in start menu (if used)
    """
    try:
        success = True
        
        # Remove shortcuts
        shortcut_results = remove_shortcuts_for_app(app_name, startmenu_folder)
        if not any(shortcut_results.values()):
            print("Warning: Failed to remove some shortcuts")
            success = False
        
        # Remove from Programs and Features (try both registries)
        removed_system = remove_from_programs_and_features(app_name, use_current_user=False)
        removed_user = remove_from_programs_and_features(app_name, use_current_user=True)
        
        if not (removed_system or removed_user):
            print("Warning: Failed to remove from Programs and Features")
            success = False
        
        # Remove installation directory if provided
        if install_path:
            install_path = Path(install_path)
            if install_path.exists():
                import shutil
                shutil.rmtree(install_path)
                print(f"Removed installation directory: {install_path}")
        
        if success:
            print(f"Uninstallation of '{app_name}' completed successfully!")
        else:
            print(f"Uninstallation of '{app_name}' completed with warnings.")
            
        return success
        
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        return False


def validate_installation_requirements(app_name: str, source_files: list = None, 
                                     bundle_dir: str = None, install_path: str = None):
    """
    Validate installation requirements before proceeding.
    
    Args:
        app_name: Name of the application
        source_files: List of source files to install
        bundle_dir: Bundle directory to install
        install_path: Target installation path
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Validate app name
    if not app_name or not app_name.strip():
        errors.append("Application name cannot be empty")
    
    # Validate sources
    if not source_files and not bundle_dir:
        errors.append("Either source_files or bundle_dir must be provided")
    
    if source_files:
        for i, (src, dest) in enumerate(source_files):
            if not Path(src).exists():
                errors.append(f"Source file {i+1} not found: {src}")
    
    if bundle_dir:
        bundle_path = Path(bundle_dir)
        if not bundle_path.exists():
            errors.append(f"Bundle directory not found: {bundle_dir}")
        elif not bundle_path.is_dir():
            errors.append(f"Bundle path is not a directory: {bundle_dir}")
    
    # Validate install path
    if install_path:
        install_path = Path(install_path)
        try:
            # Try to create parent directory to test permissions
            install_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create installation directory: {e}")
    
    return len(errors) == 0, errors


class InstallationConfig:
    """Configuration class for installations."""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.version = "1.0.0"
        self.publisher = ""
        self.install_path = f"C:/Program Files/{app_name}"
        self.source_files = []
        self.bundle_dir = None
        self.main_executable = None
        self.icon_path = None
        self.desktop_shortcut = True
        self.startmenu_shortcut = True
        self.startmenu_folder = None
        self.add_to_programs = True
        self.show_gui = True
    
    def add_source_file(self, source_path: str, dest_path: str):
        """Add a source file to the installation."""
        self