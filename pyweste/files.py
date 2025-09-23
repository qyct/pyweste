"""
PyWeste file operations module.
Handles file copying and directory operations.
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple


def do_copy_files(source_files: List[Tuple[str, str]], install_path: str) -> bool:
    """
    Copy files to installation directory.
    
    Args:
        source_files: List of tuples (source_path, relative_destination_path)
        install_path: Target installation directory
        
    Returns:
        bool: True if all files copied successfully, False otherwise
        
    Example:
        source_files = [
            ("C:/temp/myapp.exe", "myapp.exe"),
            ("C:/temp/data/config.ini", "config/config.ini")
        ]
        do_copy_files(source_files, "C:/Program Files/MyApp")
    """
    if not source_files:
        print("ERROR: No source files provided")
        return False
        
    install_path = Path(install_path)
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        print(f"INFO: Created installation directory: {install_path}")
        
        for src, rel_dest in source_files:
            if not Path(src).exists():
                print(f"ERROR: Source file not found: {src}")
                return False
                
            dest = install_path / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dest)
            print(f"INFO: Copied: {src} -> {dest}")
        
        print("INFO: All files copied successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: File copy operation failed: {e}")
        return False


def calculate_directory_size(directory: str) -> int:
    """Calculate total size of directory in bytes."""
    total_size = 0
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        print(f"WARNING: Failed to calculate directory size: {e}")
    
    return total_size


def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, create if necessary."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"ERROR: Failed to create directory {path}: {e}")
        return False