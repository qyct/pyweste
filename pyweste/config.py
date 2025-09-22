"""
Configuration classes and exceptions for PyWeste installer.
"""

from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any


class InstallationError(Exception):
    """Custom exception for installation errors."""
    pass


class InstallationConfig:
    """Complete configuration class for installations."""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.publisher = ""
        self.description = f"{app_name} Application"
        self.install_path = f"C:/Program Files/{app_name}"
        self.source_files: List[Tuple[str, str]] = []
        self.bundle_dir: Optional[str] = None
        self.main_executable: Optional[str] = None
        self.icon_path: Optional[str] = None
        self.license_file: Optional[str] = None
        
        # Installation options
        self.desktop_shortcut = True
        self.startmenu_shortcut = True
        self.startmenu_folder: Optional[str] = None
        self.add_to_programs = True
        self.add_to_startup = False
        self.add_to_path = False
        
        # File associations
        self.file_associations: Dict[str, str] = {}  # {extension: description}
        
        # GUI options
        self.show_gui = True
        self.custom_icon = None
        self.require_admin = False
        
        # Advanced options
        self.exclude_patterns = ['*.pyc', '__pycache__', '.git', '.gitignore', '*.tmp']
        self.create_uninstaller = True
        self.compress_files = False
        self.verify_signature = False
        
    # One-line configuration methods (fluent interface)
    def set_publisher(self, publisher: str): self.publisher = publisher; return self
    def set_description(self, description: str): self.description = description; return self
    def set_install_path(self, path: str): self.install_path = path; return self
    def set_bundle_dir(self, path: str): self.bundle_dir = path; return self
    def set_main_executable(self, path: str): self.main_executable = path; return self
    def set_icon_path(self, path: str): self.icon_path = path; return self
    def set_license_file(self, path: str): self.license_file = path; return self
    def enable_desktop_shortcut(self, enabled: bool = True): self.desktop_shortcut = enabled; return self
    def enable_startmenu_shortcut(self, enabled: bool = True): self.startmenu_shortcut = enabled; return self
    def set_startmenu_folder(self, folder: str): self.startmenu_folder = folder; return self
    def enable_add_to_programs(self, enabled: bool = True): self.add_to_programs = enabled; return self
    def enable_add_to_startup(self, enabled: bool = True): self.add_to_startup = enabled; return self
    def enable_add_to_path(self, enabled: bool = True): self.add_to_path = enabled; return self
    def enable_gui(self, enabled: bool = True): self.show_gui = enabled; return self
    def require_admin_privileges(self, required: bool = True): self.require_admin = required; return self
    def enable_compression(self, enabled: bool = True): self.compress_files = enabled; return self
    def enable_signature_verification(self, enabled: bool = True): self.verify_signature = enabled; return self

    def add_source_file(self, source_path: str, dest_path: str):
        """Add a source file to the installation."""
        self.source_files.append((source_path, dest_path))
        return self

    def add_file_association(self, extension: str, description: str):
        """Add a file association."""
        self.file_associations[extension] = description
        return self

    def add_exclude_pattern(self, pattern: str):
        """Add a file exclusion pattern."""
        self.exclude_patterns.append(pattern)
        return self

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration and return (is_valid, errors)."""
        errors = []
        
        # Validate app name
        if not self.app_name or not self.app_name.strip():
            errors.append("Application name cannot be empty")
            
        # Validate sources
        if not self.source_files and not self.bundle_dir:
            errors.append("Either source_files or bundle_dir must be provided")
        
        # Validate source files
        if self.source_files:
            for i, (src, dest) in enumerate(self.source_files):
                if not Path(src).exists():
                    errors.append(f"Source file {i+1} not found: {src}")
        
        # Validate bundle directory
        if self.bundle_dir:
            bundle_path = Path(self.bundle_dir)
            if not bundle_path.exists():
                errors.append(f"Bundle directory not found: {self.bundle_dir}")
            elif not bundle_path.is_dir():
                errors.append(f"Bundle path is not a directory: {self.bundle_dir}")
        
        # Validate install path
        try:
            Path(self.install_path).parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create installation directory: {e}")
        
        # Validate icon path
        if self.icon_path and not Path(self.icon_path).exists():
            errors.append(f"Icon file not found: {self.icon_path}")
            
        # Validate main executable
        if self.main_executable and self.bundle_dir:
            exe_path = Path(self.bundle_dir) / self.main_executable
            if not exe_path.exists():
                errors.append(f"Main executable not found: {exe_path}")
        
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {k: v for k, v in self.__dict__.items()}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create configuration from dictionary."""
        config = cls(data['app_name'])
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    def copy(self):
        """Create a copy of the configuration."""
        return self.from_dict(self.to_dict())


# Quick configuration templates
class QuickConfig:
    """Quick configuration templates."""
    
    @staticmethod
    def python_app(app_name: str, bundle_dir: str):
        """Configuration for Python applications."""
        return InstallationConfig(app_name).set_bundle_dir(bundle_dir).set_main_executable("run.bat")
    
    @staticmethod
    def portable_app(app_name: str, bundle_dir: str):
        """Configuration for portable applications."""
        return (InstallationConfig(app_name)
               .set_bundle_dir(bundle_dir)
               .enable_add_to_programs(False)
               .set_install_path(f"C:/PortableApps/{app_name}"))
    
    @staticmethod
    def system_tool(app_name: str, bundle_dir: str):
        """Configuration for system tools."""
        return (InstallationConfig(app_name)
               .set_bundle_dir(bundle_dir)
               .enable_add_to_path(True)
               .require_admin_privileges(True))
    
    @staticmethod
    def game_app(app_name: str, bundle_dir: str):
        """Configuration for games."""
        return (InstallationConfig(app_name)
               .set_bundle_dir(bundle_dir)
               .set_install_path(f"C:/Games/{app_name}")
               .enable_add_to_programs(True))


# Constants
class Constants:
    """Constants used throughout the installer."""
    
    DEFAULT_INSTALL_PATH = "{program_files}/{app_name}"
    DESKTOP_PATH = "{user_profile}/Desktop"
    STARTMENU_PATH = "{appdata}/Microsoft/Windows/Start Menu/Programs"
    UNINSTALL_REGISTRY_PATH = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    STARTUP_REGISTRY_PATH = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
    
    SUPPORTED_EXECUTABLE_EXTENSIONS = ['.exe', '.bat', '.cmd', '.msi', '.py']
    SUPPORTED_ICON_EXTENSIONS = ['.ico', '.png', '.jpg', '.jpeg', '.bmp']
    SUPPORTED_ARCHIVE_EXTENSIONS = ['.zip', '.tar', '.tar.gz', '.7z']
    
    MAX_PATH_LENGTH = 260
    MAX_APP_NAME_LENGTH = 50
    MIN_DISK_SPACE_MB = 10