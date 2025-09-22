import shutil
import os
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional, Callable
from .utils import is_admin, request_admin, log_error, log_info, ensure_directory

# One-line file operation functions
get_size = lambda path: Path(path).stat().st_size if Path(path).exists() else 0
get_directory_size = lambda path: sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file()) if Path(path).exists() else 0
remove_file = lambda path: Path(path).unlink(missing_ok=True) or True
remove_directory = lambda path: shutil.rmtree(path, ignore_errors=True) or True

def copy_file_admin(src: str, dst: str) -> bool:
    """Copy a file with admin privileges if needed."""
    if not Path(src).exists():
        log_error(f"Source file not found: {src}")
        return False
    
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        
        if is_admin():
            shutil.copy2(src, dst)
            log_info(f"Copied: {src} -> {dst}")
            return True
        else:
            try:
                shutil.copy2(src, dst)
                log_info(f"Copied: {src} -> {dst}")
                return True
            except PermissionError:
                log_info("Requesting admin privileges for file copy...")
                return request_admin(__file__, f'"{src}" "{dst}"')
    except Exception as e:
        log_error(f"Failed to copy {src} to {dst}: {e}")
        return False

def copy_files(source_files: List[Tuple[str, str]], install_path: str, 
               progress_callback: Optional[Callable] = None) -> bool:
    """Copy multiple files with progress tracking."""
    if not source_files:
        return True
        
    install_path = Path(install_path)
    total_files = len(source_files)
    copied_files = 0
    
    try:
        install_path.mkdir(parents=True, exist_ok=True)
        log_info(f"Created installation directory: {install_path}")
        
        for src, rel_dest in source_files:
            dest = install_path / rel_dest
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            if not copy_file_admin(src, str(dest)):
                return False
            
            copied_files += 1
            if progress_callback:
                progress_callback(copied_files, total_files)
        
        log_info("All files copied successfully")
        return True
        
    except Exception as e:
        log_error(f"File copy operation failed: {e}")
        return False

def copy_directory(src_dir: str, dst_dir: str, exclude_patterns: Optional[List[str]] = None, 
                  progress_callback: Optional[Callable] = None) -> bool:
    """Copy entire directory tree with progress tracking."""
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    exclude_patterns = exclude_patterns or ['*.pyc', '__pycache__', '.git', '.DS_Store', '*.tmp']
    
    if not src_path.exists():
        log_error(f"Source directory not found: {src_dir}")
        return False
    
    try:
        files_to_copy = []
        for item in src_path.rglob('*'):
            if item.is_file() and not any(item.match(pattern) for pattern in exclude_patterns):
                rel_path = item.relative_to(src_path)
                files_to_copy.append((str(item), str(rel_path)))
        
        total_files = len(files_to_copy)
        copied_files = 0
        
        dst_path.mkdir(parents=True, exist_ok=True)
        log_info(f"Copying directory: {src_dir} -> {dst_dir}")
        
        for src_file, rel_path in files_to_copy:
            dest_file = dst_path / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not copy_file_admin(src_file, str(dest_file)):
                return False
            
            copied_files += 1
            if progress_callback:
                progress_callback(copied_files, total_files)
        
        log_info(f"Directory copied successfully: {copied_files} files")
        return True
        
    except Exception as e:
        log_error(f"Directory copy failed: {e}")
        return False

def cleanup_files(file_paths: List[str]) -> bool:
    """Clean up multiple files and directories safely."""
    success = True
    for path in file_paths:
        try:
            path_obj = Path(path)
            if path_obj.is_file():
                path_obj.unlink(missing_ok=True)
            elif path_obj.is_dir():
                shutil.rmtree(path_obj, ignore_errors=True)
        except Exception as e:
            log_error(f"Failed to cleanup {path}: {e}")
            success = False
    return success

def verify_integrity(file_path: str, expected_size: Optional[int] = None, 
                    expected_checksum: Optional[str] = None) -> bool:
    """Verify file integrity using size and/or checksum."""
    if not Path(file_path).exists():
        return False
    
    try:
        if expected_size is not None:
            actual_size = get_size(file_path)
            if actual_size != expected_size:
                log_error(f"Size mismatch for {file_path}: expected {expected_size}, got {actual_size}")
                return False
        
        if expected_checksum is not None:
            actual_checksum = calculate_md5(file_path)
            if actual_checksum.lower() != expected_checksum.lower():
                log_error(f"Checksum mismatch for {file_path}")
                return False
        
        return True
    except Exception as e:
        log_error(f"Error verifying file integrity: {e}")
        return False

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

def create_file_list(directory: str, exclude_patterns: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """Create a list of files from a directory for installation."""
    directory = Path(directory)
    exclude_patterns = exclude_patterns or []
    file_list = []
    
    if not directory.exists():
        return file_list
    
    for item in directory.rglob('*'):
        if item.is_file() and not any(item.match(pattern) for pattern in exclude_patterns):
            rel_path = item.relative_to(directory)
            file_list.append((str(item), str(rel_path)))
    
    return file_list