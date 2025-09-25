import os
import shutil
from pathlib import Path
from typing import List, Tuple


def do_copy_files(source_files: List[Tuple[str, str]], install_path: str) -> bool:
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