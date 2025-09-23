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
    Copy files and folders to installation directory.
    
    Args:
        source_files: List of tuples (source_path, relative_destination_path)
        install_path: Target installation directory
        
    Returns:
        bool: True if all files copied successfully, False otherwise
        
    Example:
        source_files = [
            ("C:/temp/myapp.exe", "myapp.exe"),
            ("C:/temp/data/", "data/"),  # Entire folder
            ("C:/temp/config.ini", "config/config.ini")
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
            src_path = Path(src)
            
            if not src_path.exists():
                print(f"ERROR: Source file/folder not found: {src}")
                return False
            
            dest = install_path / rel_dest
            
            if src_path.is_dir():
                # Handle directory copying
                if rel_dest.endswith('/') or rel_dest.endswith('\\'):
                    # Copy contents of source directory to destination
                    dest = dest.parent / dest.name if dest.name else dest.parent
                    dest.mkdir(parents=True, exist_ok=True)
                    
                    for item in src_path.iterdir():
                        if item.is_dir():
                            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest / item.name)
                    
                    print(f"INFO: Copied directory contents: {src} -> {dest}")
                else:
                    # Copy entire directory to destination
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src_path, dest)
                    print(f"INFO: Copied directory: {src} -> {dest}")
            else:
                # Handle file copying
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
                print(f"INFO: Copied file: {src} -> {dest}")
        
        print("INFO: All files/folders copied successfully")
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


def validate_source_files(source_files: List[Tuple[str, str]], base_folder: str = None) -> List[Tuple[str, str]]:
    """
    Validate and resolve source file paths.
    
    Args:
        source_files: List of (source, dest) tuples
        base_folder: Optional base folder for relative paths
        
    Returns:
        List of validated (source, dest) tuples with resolved paths
    """
    validated_files = []
    base_path = Path(base_folder) if base_folder else Path.cwd()
    
    for src, dest in source_files:
        src_path = Path(src)
        
        # Resolve relative paths
        if not src_path.is_absolute():
            src_path = base_path / src_path
        
        # Check if source exists
        if not src_path.exists():
            print(f"WARNING: Source not found: {src_path}")
            continue
        
        validated_files.append((str(src_path), dest))
    
    return validated_files