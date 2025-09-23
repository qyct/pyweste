"""Internal utilities for PyWeste."""

import ctypes
import sys


def is_admin() -> bool:
    """Check if running with administrator privileges."""
    return ctypes.windll.shell32.IsUserAnAdmin() != 0


def request_admin(script_path: str = None, params: str = "") -> bool:
    """Request administrator privileges via UAC."""
    if is_admin():
        return True
    try:
        script_path = script_path or __file__
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, 
            f'"{script_path}" {params}', None, 1
        )
        return True
    except Exception as e:
        print(f"ERROR: Failed to elevate privileges: {e}")
        return False