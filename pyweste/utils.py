import os
import sys
import ctypes
import platform
import tempfile
import subprocess
import hashlib
from pathlib import Path
from typing import Optional, Tuple, List

# One-line system detection functions
is_admin = lambda: ctypes.windll.shell32.IsUserAnAdmin() != 0
is_windows = lambda: platform.system() == 'Windows'
is_64bit = lambda: platform.machine().endswith('64')
get_python_version = lambda: platform.python_version()
get_windows_version = lambda: platform.platform()

# One-line path utilities
get_program_files = lambda: os.environ.get('PROGRAMFILES', 'C:/Program Files')
get_program_files_x86 = lambda: os.environ.get('PROGRAMFILES(X86)', 'C:/Program Files (x86)')
get_user_profile = lambda: str(Path.home())
get_appdata = lambda: os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming'))
get_localappdata = lambda: os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local'))
get_temp_dir = lambda: tempfile.gettempdir()
get_desktop = lambda: str(Path.home() / "Desktop")
get_startmenu = lambda: str(Path(get_appdata()) / "Microsoft" / "Windows" / "Start Menu" / "Programs")

# One-line file utilities
file_exists = lambda path: Path(path).exists()
is_file = lambda path: Path(path).is_file()
is_directory = lambda path: Path(path).is_dir()
get_file_size = lambda path: Path(path).stat().st_size if Path(path).exists() else 0
get_file_extension = lambda path: Path(path).suffix.lower()
get_filename = lambda path: Path(path).name
get_filename_without_ext = lambda path: Path(path).stem

# One-line process utilities
is_process_running = lambda name: name.lower() in subprocess.run(f'tasklist /FI "IMAGENAME eq {name}"', capture_output=True, text=True, shell=True).stdout.lower()
kill_process = lambda name: subprocess.run(f'taskkill /F /IM {name}', shell=True, capture_output=True).returncode == 0

# Installation path utilities
def get_install_path(app_name: str, use_x86: bool = False) -> str:
    """Get default installation path for an application."""
    base = get_program_files_x86() if use_x86 else get_program_files()
    return str(Path(base) / app_name)

def get_user_install_path(app_name: str) -> str:
    """Get user-specific installation path."""
    return str(Path(get_localappdata()) / "Programs" / app_name)

def request_admin(script_path: str = None, params: str = "") -> bool:
    """Request administrator privileges via UAC."""
    if is_admin():
        return True
    try:
        script_path = script_path or __file__
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script_path}" {params}', None, 1)
        return True
    except Exception as e:
        log_error(f"Failed to elevate privileges: {e}")
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

def get_disk_space(path: str) -> Tuple[int, int, int]:
    """Get disk space information (total, used, free) in bytes."""
    try:
        free_bytes = ctypes.c_ulonglong(0)
        total_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path), ctypes.pointer(free_bytes), ctypes.pointer(total_bytes), None
        )
        total = total_bytes.value
        free = free_bytes.value
        return total, total - free, free
    except:
        return 0, 0, 0

def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return ""

def ensure_directory(directory: str) -> bool:
    """Ensure directory exists, create if it doesn't."""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        log_error(f"Failed to create directory {directory}: {e}")
        return False

def run_command(command: str, capture_output: bool = True) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout if capture_output else ""
    except Exception as e:
        return False, str(e)

# Logging utilities
log_info = lambda msg: print(f"INFO: {msg}")
log_warning = lambda msg: print(f"WARNING: {msg}")
log_error = lambda msg: print(f"ERROR: {msg}")
log_debug = lambda msg: print(f"DEBUG: {msg}")