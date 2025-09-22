from .utils import is_admin, request_admin, get_install_path, format_size, log_info, log_error
from .files import copy_files, copy_directory, get_size, cleanup_files, verify_integrity
from .registry import add_to_programs, remove_from_programs, add_to_startup, remove_from_startup
from .shortcuts import create_shortcut, remove_shortcut, create_all_shortcuts, remove_all_shortcuts
from .installer import install_app, uninstall_app, validate_installation_requirements
from .gui import InstallerGUI, BundleInstallerGUI, create_installer
from .progress import ProgressCallback, ConsoleProgress, GUIProgress
from .config import InstallationConfig, QuickConfig, InstallationError

# Convenience one-line functions
quick_install = lambda app_name, source_path, **kwargs: install_app(app_name, bundle_dir=source_path, **kwargs)
gui_install = lambda app_name, source_path, **kwargs: BundleInstallerGUI(app_name, source_path, **kwargs).run()
silent_install = lambda app_name, source_path, install_path=None: install_app(app_name, bundle_dir=source_path, install_path=install_path or get_install_path(app_name), show_gui=False)

__all__ = [
    'install_app', 'uninstall_app', 'validate_installation_requirements',
    'create_shortcut', 'remove_shortcut', 'create_all_shortcuts', 'remove_all_shortcuts',
    'add_to_programs', 'remove_from_programs', 'add_to_startup', 'remove_from_startup',
    'copy_files', 'copy_directory', 'get_size', 'cleanup_files', 'verify_integrity',
    'is_admin', 'request_admin', 'get_install_path', 'format_size',
    'InstallerGUI', 'BundleInstallerGUI', 'create_installer',
    'ProgressCallback', 'ConsoleProgress', 'GUIProgress',
    'InstallationConfig', 'QuickConfig', 'InstallationError',
    'quick_install', 'gui_install', 'silent_install'
]