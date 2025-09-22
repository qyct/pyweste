"""
PyWeste - Windows Installer Library
A comprehensive Python library for creating Windows installers with GUI support.
"""

# Core functionality imports
from .installer import install_app, uninstall_app, validate_installation
from .shortcuts import create_shortcut, remove_shortcut, create_all_shortcuts
from .registry import add_to_programs, remove_from_programs, add_to_startup
from .files import copy_files, copy_directory, get_size, cleanup_files
from .utils import is_admin, request_admin, get_install_path

# GUI imports
from .gui import InstallerGUI, BundleInstallerGUI
from .progress import ProgressCallback, ConsoleProgress

# Configuration
from .config import InstallationConfig, InstallationError

# Convenience one-line functions
def quick_install(app_name: str, source_path: str, **kwargs): return install_app(app_name, bundle_dir=source_path, **kwargs)
def gui_install(app_name: str, source_path: str, **kwargs): return BundleInstallerGUI(app_name, source_path, **kwargs).run()
def silent_install(app_name: str, source_path: str, install_path: str = None): return install_app(app_name, bundle_dir=source_path, install_path=install_path or get_install_path(app_name), show_gui=False)

# Main exports
__all__ = [
    # Core functions
    'install_app', 'uninstall_app', 'validate_installation',
    'create_shortcut', 'remove_shortcut', 'create_all_shortcuts',
    'add_to_programs', 'remove_from_programs', 'add_to_startup',
    'copy_files', 'copy_directory', 'get_size', 'cleanup_files',
    'is_admin', 'request_admin', 'get_install_path',
    
    # GUI classes
    'InstallerGUI', 'BundleInstallerGUI',
    'ProgressCallback', 'ConsoleProgress',
    
    # Configuration
    'InstallationConfig', 'InstallationError',
    
    # Convenience functions
    'quick_install', 'gui_install', 'silent_install'
]