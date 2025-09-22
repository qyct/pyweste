from pathlib import Path
from typing import Optional, List, Tuple, Callable
from .files import copy_files, copy_directory, cleanup_files
from .shortcuts import create_all_shortcuts, remove_all_shortcuts
from .registry import add_to_programs, remove_from_programs, add_to_startup, remove_from_startup, add_to_path
from .utils import log_info, log_error, ensure_directory, validate_app_name

def create_uninstaller(app_name: str, install_path: str) -> str:
    """Create an uninstaller script for the application."""
    install_path = Path(install_path)
    uninstall_script = install_path / "uninstall.bat"
    
    uninstall_content = f'''@echo off
:: Uninstaller for {app_name}
echo Uninstalling {app_name}...

:: Remove shortcuts
del "%USERPROFILE%\\Desktop\\{app_name}.lnk" 2>nul
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{app_name}.lnk" 2>nul

:: Remove from registry
reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul
reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{app_name}" /f 2>nul

:: Remove installation directory
cd /d "{install_path.parent}"
rmdir /s /q "{install_path.name}" 2>nul

echo {app_name} has been uninstalled.
pause
'''
    
    try:
        with open(uninstall_script, 'w') as f:
            f.write(uninstall_content)
        log_info(f"Uninstaller created: {uninstall_script}")
        return str(uninstall_script)
    except Exception as e:
        log_error(f"Failed to create uninstaller: {e}")
        return None

def install_app(app_name: str, source_files: Optional[List[Tuple[str, str]]] = None, 
                bundle_dir: Optional[str] = None, install_path: Optional[str] = None,
                desktop_shortcut: bool = True, startmenu_shortcut: bool = True, 
                add_to_programs_registry: bool = True, main_executable: Optional[str] = None,
                icon_path: Optional[str] = None, version: str = "1.0.0", 
                publisher: str = "", startmenu_folder: Optional[str] = None, 
                progress_callback: Optional[Callable] = None, show_gui: bool = True) -> bool:
    """Complete application installer in one function."""
    
    # Validate app name
    is_valid, error_msg = validate_app_name(app_name)
    if not is_valid:
        log_error(error_msg)
        return False
    
    if install_path is None:
        from .utils import get_install_path
        install_path = get_install_path(app_name)
    
    install_path = Path(install_path)
    
    try:
        log_info(f"Starting installation of '{app_name}'")
        
        # Copy files or bundle directory
        if bundle_dir:
            log_info(f"Installing bundle from: {bundle_dir}")
            success = copy_directory(bundle_dir, str(install_path), 
                                   exclude_patterns=['*.pyc', '__pycache__', '.git'], 
                                   progress_callback=progress_callback)
        elif source_files:
            log_info(f"Installing files to: {install_path}")
            success = copy_files(source_files, str(install_path), progress_callback)
        else:
            log_error("No source files or bundle directory provided")
            return False
        
        if not success:
            log_error("File installation failed")
            return False
        
        # Determine main executable
        if main_executable is None:
            exe_files = list(install_path.rglob("*.exe"))
            bat_files = list(install_path.rglob("*.bat"))
            
            if exe_files:
                main_executable = str(exe_files[0])
            elif bat_files:
                main_executable = str(bat_files[0])
            else:
                # Create a default run.bat for Python apps
                if bundle_dir and Path(bundle_dir).joinpath("main.py").exists():
                    run_bat = install_path / "run.bat"
                    with open(run_bat, 'w') as f:
                        f.write("@echo off\ncd /d \"%~dp0\"\npython main.py\n")
                    main_executable = str(run_bat)
                else:
                    log_error("No main executable found or specified")
                    main_executable = str(install_path / f"{app_name}.exe")
        else:
            main_executable = str(install_path / main_executable)
        
        # Create uninstaller
        uninstaller_path = create_uninstaller(app_name, str(install_path))
        
        # Create shortcuts
        if desktop_shortcut or startmenu_shortcut:
            shortcut_results = create_all_shortcuts(
                app_name, main_executable, icon_path,
                desktop_shortcut, startmenu_shortcut, startmenu_folder
            )
            log_info(f"Shortcut creation results: {shortcut_results}")
        
        # Add to Programs and Features
        if add_to_programs_registry and uninstaller_path:
            success = add_to_programs(app_name, str(install_path), uninstaller_path,
                                    version, publisher, icon_path, use_current_user=True)
            if not success:
                log_info("Failed to add to Programs and Features")
        
        log_info(f"Installation of '{app_name}' completed successfully!")
        return True
        
    except Exception as e:
        log_error(f"Installation failed: {e}")
        return False

def uninstall_app(app_name: str, install_path: Optional[str] = None, 
                 startmenu_folder: Optional[str] = None) -> bool:
    """Uninstall an application completely."""
    try:
        log_info(f"Starting uninstallation of '{app_name}'")
        
        success = True
        
        # Remove shortcuts
        shortcut_results = remove_all_shortcuts(app_name, startmenu_folder)
        if not any(shortcut_results.values()):
            log_error("Failed to remove shortcuts")
            success = False
        
        # Remove from Programs and Features
        removed = remove_from_programs(app_name, use_current_user=True)
        if not removed:
            removed = remove_from_programs(app_name, use_current_user=False)
        if not removed:
            log_error("Failed to remove from Programs and Features")
            success = False
        
        # Remove installation directory
        if install_path:
            install_path = Path(install_path)
            if install_path.exists():
                import shutil
                shutil.rmtree(install_path, ignore_errors=True)
                log_info(f"Removed installation directory: {install_path}")
        
        if success:
            log_info(f"Uninstallation of '{app_name}' completed successfully!")
        else:
            log_error(f"Uninstallation of '{app_name}' completed with errors")
            
        return success
        
    except Exception as e:
        log_error(f"Uninstallation failed: {e}")
        return False

def validate_installation_requirements(app_name: str, source_files: Optional[List[Tuple[str, str]]] = None, 
                                     bundle_dir: Optional[str] = None, 
                                     install_path: Optional[str] = None) -> Tuple[bool, List[str]]:
    """Validate installation requirements before proceeding."""
    errors = []
    
    # Validate app name
    is_valid, error_msg = validate_app_name(app_name)
    if not is_valid:
        errors.append(error_msg)
    
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
    if install_path and len(install_path) > 260:
        errors.append("Installation path too long (max 260 characters)")
    
    return len(errors) == 0, errors