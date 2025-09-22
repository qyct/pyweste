import shutil
import os
import sys
import ctypes

def is_admin():
    """Check if the script is running with admin privileges (Windows only)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def copy_file_admin(src: str, dst: str):
    """
    Copies a file from src to dst with admin privileges on Windows.
    If not running as admin, prompts the user to elevate via UAC.
    """
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Source file not found: {src}")

    if is_admin():
        # Already admin, perform the copy
        shutil.copy2(src, dst)
        print(f"Copied '{src}' -> '{dst}' successfully.")
    else:
        # Relaunch script as admin
        print("Requesting admin privileges...")
        params = f'"{__file__}" "{src}" "{dst}"'
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        except Exception as e:
            print("Failed to elevate privileges:", e)
