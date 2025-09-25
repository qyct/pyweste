import os
import re
import sys
import shutil
import tomllib
import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import List, Tuple, Dict, Any

from .utils import browse_for_folder
from .reg import setup_entries


def load_toml_config(toml_path: str) -> Dict[str, Any]:
    """Load configuration from pyproject.toml file."""
    try:
        with open(toml_path, 'rb') as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"ERROR: pyproject.toml file not found: {toml_path}")
        return {}
    except Exception as e:
        print(f"ERROR: Failed to load pyproject.toml configuration: {e}")
        return {}


def copy_files(source_files: List[Tuple[str, str]], install_path: str) -> bool:
    """Copy source files to installation directory."""
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


class InstallerGUI:
    def __init__(self, app_name: str, default_install_path: str, icon_path: str, source_files: List[Tuple[str, str]]):
        self.app_name = app_name
        self.default_install_path = default_install_path
        self.icon_path = icon_path
        self.source_files = source_files
        self.installing = False
        self.install_success = False
        
    def browse_folder(self):
        """Browse for installation folder."""
        folder_path = browse_for_folder("Select installation folder")
        if folder_path:
            full_path = str(Path(folder_path) / self.app_name)
            dpg.set_value("install_path", full_path)
    
    def update_progress(self, progress: float, message: str):
        """Update progress bar and status message."""
        dpg.set_value("progress_bar", progress)
        dpg.set_value("progress_text", message)
        dpg.render_dearpygui_frame()
    
    def do_install(self):
        """Handle complete installation process."""
        if self.installing:
            return
        
        self.installing = True
        dpg.configure_item("install_button", enabled=False)
        
        install_path = dpg.get_value("install_path")
        todo_desktop = dpg.get_value("desktop_shortcut")
        todo_startmenu = dpg.get_value("startmenu_shortcut")
        todo_registry = dpg.get_value("add_remove_programs")
        
        try:
            # Step 1: Copy files
            self.update_progress(0.25, "Copying files...")
            if not copy_files(self.source_files, install_path):
                raise Exception("File copying failed")
            
            # Step 2: Create shortcuts and registry
            self.update_progress(0.75, "Creating shortcuts and registry entries...")
            if todo_desktop or todo_startmenu or todo_registry:
                run_bat_path = str(Path(install_path) / "run.bat")
                icon_path = str(Path(install_path) / "bin" / "icon.ico")
                icon_path = icon_path if Path(icon_path).exists() else None
                
                setup_entries(
                    app_name=self.app_name,
                    install_path=install_path,
                    executable=run_bat_path,
                    icon_path=icon_path,
                    create_desktop=todo_desktop,
                    create_startmenu=todo_startmenu,
                    add_registry=todo_registry
                )
            
            # Complete
            self.update_progress(1.0, "Installation completed successfully!")
            print(f"INFO: Installation of {self.app_name} completed successfully!")
            self.install_success = True
            
            # Change button to Close when installation is successful
            dpg.configure_item("install_button", label="Close", enabled=True)
            
        except Exception as e:
            print(f"ERROR: Installation failed: {e}")
            self.update_progress(0.0, f"Installation failed: {str(e)}")
            dpg.configure_item("install_button", label="Install", enabled=True)
            self.installing = False
    
    def install_clicked(self):
        """Handle install/close button click."""
        if self.install_success:
            dpg.destroy_context()
        else:
            self.do_install()
    
    def run(self) -> bool:
        dpg.create_context()
        
        with dpg.window(tag="main_window", width=450, height=300, 
                       no_resize=True, no_collapse=True, no_title_bar=True):
            
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=15)
                with dpg.group():                    
                    dpg.add_spacer(height=20)
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="install_path", default_value=self.default_install_path, width=300)
                        dpg.add_button(label="Browse", callback=self.browse_folder, width=70)
                    
                    dpg.add_spacer(height=15)
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=15)
                    dpg.add_text("Ready to install", tag="progress_text")
                    dpg.add_spacer(height=15)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=270, height=25)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=100, height=25)
        
        dpg.create_viewport(title="Setup", width=470, height=320, resizable=False)
        
        if self.icon_path and Path(self.icon_path).exists():
            dpg.set_viewport_small_icon(self.icon_path)
            dpg.set_viewport_large_icon(self.icon_path)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return self.install_success

def _sanitize_app_name(name: str) -> str:
    # Trim surrounding whitespace
    name = name.strip()
    # Replace any non-alphanumeric with space
    name = re.sub(r'[^a-zA-Z0-9]', ' ', name)
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    # Strip leading/trailing spaces again after collapsing
    name = name.strip()
    return name

def init_installer():
    """Initialize and start the installer."""
    bin_directory = os.path.dirname(sys.executable)
    bundle_root = os.path.dirname(bin_directory)
    
    toml_path = os.path.join(bin_directory, "pyproject.toml")
    config = load_toml_config(toml_path)
    
    if not config or 'project' not in config:
        print("ERROR: Invalid pyproject.toml configuration")
        return
    
    app_name = config['project']['name']
    app_name = _sanitize_app_name(app_name)

    icon_path = os.path.join(bin_directory, "icon.ico")
    default_install_path = str(Path('C:/Program Files') / app_name)
    source_files = [(bundle_root + "/", "")]  # Copy entire bundle directory contents
    
    print(f"INFO: Starting GUI installer for: {app_name}")
    print(f"INFO: Default install path: {default_install_path}")
    print(f"INFO: Will copy entire bundle directory: {bundle_root}")
    
    try:
        gui = InstallerGUI(
            app_name=app_name,
            default_install_path=default_install_path,
            icon_path=icon_path,
            source_files=source_files
        )
        gui.run()
    except Exception as e:
        print(f"ERROR: Installer failed: {e}")