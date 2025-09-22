"""
File copying and management operations for pyweste installer
"""

import shutil
import os
import sys
import ctypes
from pathlib import Path


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
        os.makedirs(os.path.dirname(dst), exist_ok=True)
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


def copy_files_with_progress(source_files, install_path, progress_callback=None):
    """
    Copy multiple files with progress tracking.
    
    Args:
        source_files: List of (source_path, relative_dest_path) tuples
        install_path: Base installation directory
        progress_callback: Function to call with progress updates (copied_files, total_files)
    """
    install_path = Path(install_path)
    total_files = len(source_files)
    copied_files = 0
    
    try:
        # Create installation directory
        install_path.mkdir(parents=True, exist_ok=True)
        print(f"Created installation directory: {install_path}")
        
        # Copy files
        for src, rel_dest in source_files:
            dest = install_path / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if is_admin():
                shutil.copy2(src, dest)
            else:
                copy_file_admin(src, str(dest))
            
            copied_files += 1
            if progress_callback:
                progress_callback(copied_files, total_files)
        
        print("Files copied successfully")
        return True
        
    except Exception as e:
        print(f"File copy failed: {e}")
        return False


def copy_directory_tree(src_dir, dst_dir, exclude_patterns=None, progress_callback=None):
    """
    Copy entire directory tree with progress tracking.
    
    Args:
        src_dir: Source directory path
        dst_dir: Destination directory path
        exclude_patterns: List of patterns to exclude (e.g., ['*.pyc', '__pycache__'])
        progress_callback: Function to call with progress updates
    """
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)
    exclude_patterns = exclude_patterns or []
    
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")
    
    # Count total files for progress
    total_files = 0
    for item in src_dir.rglob('*'):
        if item.is_file():
            # Check if file should be excluded
            should_exclude = any(item.match(pattern) for pattern in exclude_patterns)
            if not should_exclude:
                total_files += 1
    
    copied_files = 0
    
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        
        for item in src_dir.rglob('*'):
            if item.is_file():
                # Check if file should be excluded
                should_exclude = any(item.match(pattern) for pattern in exclude_patterns)
                if should_exclude:
                    continue
                
                # Calculate relative path
                rel_path = item.relative_to(src_dir)
                dest_path = dst_dir / rel_path
                
                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                if is_admin():
                    shutil.copy2(item, dest_path)
                else:
                    copy_file_admin(str(item), str(dest_path))
                
                copied_files += 1
                if progress_callback:
                    progress_callback(copied_files, total_files)
        
        print(f"Directory tree copied successfully: {src_dir} -> {dst_dir}")
        return True
        
    except Exception as e:
        print(f"Directory copy failed: {e}")
        return False


def cleanup_temp_files(temp_paths):
    """Clean up temporary files and directories."""
    for path in temp_paths:
        try:
            path = Path(path)
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
        except Exception as e:
            print(f"Failed to cleanup {path}: {e}")


def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        return Path(file_path).stat().st_size
    except:
        return 0


def get_directory_size(dir_path):
    """Get total size of directory in bytes."""
    try:
        return sum(f.stat().st_size for f in Path(dir_path).rglob('*') if f.is_file())
    except:
        return 0