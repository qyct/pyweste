"""
Core utility functions for PyWeste installer.
"""

import os
import sys
import ctypes
import platform
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple


# One-line admin and system detection functions
def is_admin() -> bool: return ctypes.windll.shell32.IsUserAnAdmin() != 0
def is_windows() -> bool: return platform.system() == 'Windows'
def is_64bit() -> bool: return platform.machine().endswith('64')
def get_python_version() -> str: return platform.python_version()
def get_windows_version() -> str: return platform.platform()

# One-line path utilities
def get_program_files() -> str: return os.environ.get('PROGRAMFILES', 'C:/Program Files')
def get_program_files_x86() -> str: return os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)')
def get_user_profile() -> str: return str(Path.home())
def get_appdata() -> str: return os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
def get_localappdata() -> str: return os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local'))
def get_temp_dir() -> str: return tempfile.gettempdir()
def get_desktop() -> str: return str(Path.home() / "Desktop")
def get_startmenu() -> str: return str(Path(get_appdata()) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

# Installation path utilities
def get_install_path(app_name: str, use_x86: bool = False) -> str:
    """Get default installation path for an application."""
    base = get_program_files_x86() if use_x86 else get_program_files()
    return str(Path(base) / app_name)

def get_user_install_path(app_name: str) -> str:
    """Get user-specific installation path."""
    return str(Path(get_localappdata()) / "Programs" / app_name)

def get_portable_install_path(app_name: str) -> str:
    """Get portable installation path."""
    return str(Path("C:/PortableApps") / app_name)


def request_admin(script_path: str = None, params: str = "") -> bool:
    """Request administrator privileges via UAC."""
    if is_admin():
        return True
        
    try:
        script_path = script_path or __file__
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script_path}" {params}', None, 1
        )
        return True
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False


def validate_app_name(app_name: str) -> Tuple[bool, str]:
    """Validate application name."""
    if not app_name or not app_name.strip():
        return False, "Application name cannot be empty"
    
    if len(app_name) > 50:
        return False, "Application name too long (max 50 characters)"
    
    invalid_chars = '<>:"/\\|?*'
    if any(char in app_name for char in invalid_chars):
        return False, f"Application name contains invalid characters: {invalid_chars}"
    
    return True, ""


def validate_path(path: str, must_exist: bool = False) -> Tuple[bool, str]:
    """Validate file or directory path."""
    try:
        path_obj = Path(path)
        
        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path}"
            
        if len(str(path)) > 260:  # Windows MAX_PATH
            return False, "Path too long (max 260 characters)"
            
        return True, ""
    except Exception as e:
        return False, f"Invalid path: {e}"


def get_file_version(file_path: str) -> Optional[str]:
    """Get file version information."""
    try:
        import win32api
        info = win32api.GetFileVersionInfo(file_path, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
    except:
        return None


def run_command(command: str, capture_output: bool = True) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=capture_output, text=True
        )
        return result.returncode == 0, result.stdout if capture_output else ""
    except Exception as e:
        return False, str(e)


# One-line process utilities
def is_process_running(process_name: str) -> bool: return process_name.lower() in subprocess.run(f'tasklist /FI "IMAGENAME eq {process_name}"', capture_output=True, text=True, shell=True).stdout.lower()
def kill_process(process_name: str) -> bool: return subprocess.run(f'taskkill /F /IM {process_name}', shell=True, capture_output=True).returncode == 0


def get_disk_space(path: str) -> Tuple[int, int, int]:
    """Get disk space information (total, used, free) in bytes."""
    try:
        if is_windows():
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                ctypes.pointer(free_bytes),
                ctypes.pointer(total_bytes),
                None
            )
            total = total_bytes.value
            free = free_bytes.value
            used = total - free
            return total, used, free
        else:
            stat = os.statvfs(path)
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_availi * stat.f_frsize
            used = (stat.f_blocks - stat.f_available) * stat.f_frsize
            return total, used, free
    except:
        return 0, 0, 0


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable string."""
    if size_bytes == 0:
        return "0 B"
    
    sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    while size_bytes >= 1024 and i < len(sizes) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {sizes[i]}"


def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if it doesn't."""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create directory {directory}: {e}")
        return False


def safe_remove(path: str) -> bool:
    """Safely remove file or directory."""
    try:
        path_obj = Path(path)
        if path_obj.is_file():
            path_obj.unlink()
        elif path_obj.is_dir():
            import shutil
            shutil.rmtree(path_obj)
        return True
    except Exception as e:
        print(f"Failed to remove {path}: {e}")
        return False


def find_executable(exe_name: str) -> Optional[str]:
    """Find executable in PATH."""
    try:
        result = subprocess.run(f'where {exe_name}', capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
        return None
    except:
        return None


# One-line file utilities
def file_exists(path: str) -> bool: return Path(path).exists()
def is_file(path: str) -> bool: return Path(path).is_file()
def is_directory(path: str) -> bool: return Path(path).is_dir()
def get_file_size(path: str) -> int: return Path(path).stat().st_size if Path(path).exists() else 0
def get_file_extension(path: str) -> str: return Path(path).suffix.lower()
def get_filename(path: str) -> str: return Path(path).name
def get_filename_without_ext(path: str) -> str: return Path(path).stem


def create_temp_file(suffix: str = "", prefix: str = "pyweste_", directory: str = None) -> str:
    """Create a temporary file and return its path."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=directory)
    os.close(fd)  # Close the file descriptor
    return path


def create_temp_directory(prefix: str = "pyweste_", directory: str = None) -> str:
    """Create a temporary directory and return its path."""
    return tempfile.mkdtemp(prefix=prefix, dir=directory)


# Environment information
def get_environment_info() -> dict:
    """Get comprehensive environment information."""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'is_admin': is_admin(),
        'is_64bit': is_64bit(),
        'user_profile': get_user_profile(),
        'program_files': get_program_files(),
        'temp_dir': get_temp_dir(),
    }


# Logging utilities
def log_info(message: str): print(f"INFO: {message}")
def log_warning(message: str): print(f"WARNING: {message}")
def log_error(message: str): print(f"ERROR: {message}")
def log_debug(message: str): print(f"DEBUG: {message}")


# Registry utilities (basic)
def read_registry_value(hive, key_path: str, value_name: str) -> Optional[str]:
    """Read a registry value."""
    try:
        import winreg
        with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
            value, reg_type = winreg.QueryValueEx(key, value_name)
            return value
    except:
        return None


def write_registry_value(hive, key_path: str, value_name: str, value: str, reg_type=None) -> bool:
    """Write a registry value."""
    try:
        import winreg
        reg_type = reg_type or winreg.REG_SZ
        with winreg.CreateKey(hive, key_path) as key:
            winreg.SetValueEx(key, value_name, 0, reg_type, value)
        return True
    except Exception as e:
        log_error(f"Failed to write registry value: {e}")
        return False