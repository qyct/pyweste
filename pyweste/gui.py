"""
PyWeste GUI installer module.
Handles the installer GUI interface and user interaction with icon support.
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from .utils import browse_for_folder
from .files import do_copy_files
from .shortcuts import do_desktop_shortcut, do_startmenu_shortcut
from .registry import add_to_registry


def load_icon_for_viewport(icon_path: str) -> bool:
    """
    Load icon for the DearPyGui viewport.
    
    Args:
        icon_path: Path to icon file (.ico, .png, .jpg supported)
        
    Returns:
        bool: True if icon loaded successfully
    """
    if not icon_path or not Path(icon_path).exists():
        return False
    
    try:
        # DearPyGui supports common image formats for viewport icons
        dpg.set_viewport_small_icon(icon_path)
        dpg.set_viewport_large_icon(icon_path)
        return True
    except Exception as e:
        print(f"WARNING: Failed to load icon: {e}")
        return False


class InstallerGUI:
    """GUI installer class that handles complete installation process."""
    
    def __init__(self, app_name: str = "MyApp", default_install_path: str = None, 
                 icon_path: str = None, source_files: List[Tuple[str, str]] = None,
                 publisher: str = "Unknown", main_executable: str = None):
        self.app_name = app_name
        self.default_install_path = default_install_path or f"C:/Program Files/{app_name}"
        self.icon_path = icon_path
        self.source_files = source_files or []
        self.publisher = publisher
        self.main_executable = main_executable
        self.installing = False
        self.install_success = False
        
    def browse_folder(self):
        """Browse for installation folder."""
        folder_path = browse_for_folder(
            "Select installation folder", 
            self.default_install_path
        )
        if folder_path:
            full_path = str(Path(folder_path) / self.app_name)
            dpg.set_value("install_path", full_path)
    
    def update_progress(self, progress: float, message: str):
        """Update progress bar and status message."""
        dpg.set_value("progress_bar", progress)
        dpg.set_value("progress_text", message)
        dpg.render_dearpygui_frame()
    
    def do_install(self):
        """Handle complete installation process when install button is clicked."""
        if self.installing:
            return
        
        self.installing = True
        dpg.configure_item("install_button", enabled=False)
        dpg.set_value("install_button", "Installing...")
        
        # Get user choices
        install_path = dpg.get_value("install_path")
        todo_desktop = dpg.get_value("desktop_shortcut")
        todo_startmenu = dpg.get_value("startmenu_shortcut")
        todo_registry = dpg.get_value("add_remove_programs")
        
        try:
            total_steps = 4
            current_step = 0
            
            # Step 1: Copy files
            current_step += 1
            self.update_progress(current_step / total_steps, "Copying files...")
            
            if not do_copy_files(self.source_files, install_path):
                raise Exception("File copying failed")
            
            # Step 2: Create desktop shortcut
            current_step += 1
            self.update_progress(current_step / total_steps, "Creating shortcuts...")
            
            if todo_desktop and self.main_executable:
                target_path = str(Path(install_path) / self.main_executable)
                if not do_desktop_shortcut(target_path, self.app_name, self.icon_path):
                    print("WARNING: Failed to create desktop shortcut")
            
            # Step 3: Create start menu shortcut
            if todo_startmenu and self.main_executable:
                target_path = str(Path(install_path) / self.main_executable)
                if not do_startmenu_shortcut(target_path, self.app_name, self.icon_path, self.publisher):
                    print("WARNING: Failed to create start menu shortcut")
            
            # Step 4: Add to registry (includes uninstaller creation)
            current_step += 1
            self.update_progress(current_step / total_steps, "Setting up registry...")
            
            if todo_registry:
                if not add_to_registry(
                    app_name=self.app_name,
                    install_path=install_path,
                    main_executable=self.main_executable,
                    icon_path=self.icon_path,
                    publisher=self.publisher
                ):
                    print("WARNING: Failed to add registry entry")
            
            # Final step
            current_step += 1
            self.update_progress(1.0, "Installation completed successfully!")
            
            print(f"INFO: Installation of {self.app_name} completed successfully!")
            self.install_success = True
            
            # Update button to show completion
            dpg.set_value("install_button", "Finish")
            dpg.configure_item("install_button", enabled=True)
            
        except Exception as e:
            print(f"ERROR: Installation failed: {e}")
            self.update_progress(0.0, f"Installation failed: {str(e)}")
            dpg.set_value("install_button", "Install")
            dpg.configure_item("install_button", enabled=True)
            self.installing = False
    
    def finish_clicked(self):
        """Handle finish button click after successful installation."""
        dpg.destroy_context()
    
    def install_clicked(self):
        """Handle install/finish button click."""
        if self.install_success:
            self.finish_clicked()
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
                        # dpg.add_spacer(width=150)
                        dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=270, height=25)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=100, height=25)
        
        dpg.create_viewport(title="Setup", width=470, height=320, resizable=False)
        
        # Load icon if provided
        if self.icon_path:
            load_icon_for_viewport(self.icon_path)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return self.install_success


def start_gui_installer(app_name: str = "MyApp", default_install_path: str = None, 
                       icon_path: str = None, source_files: List[Tuple[str, str]] = None,
                       publisher: str = "Unknown", main_executable: str = None) -> bool:
    """
    Start GUI installer and perform complete installation.
    
    Args:
        app_name: Name of the application
        default_install_path: Default installation path
        icon_path: Path to icon file for window title bar
        source_files: List of (source, destination) file pairs to copy
        publisher: Application publisher name
        main_executable: Main executable file for shortcuts
        
    Returns:
        bool: True if installation completed successfully, False otherwise
        
    Example:
        success = start_gui_installer(
            "MyApp", 
            source_files=[("dist/myapp.exe", "myapp.exe")],
            icon_path="icon.ico",
            main_executable="myapp.exe"
        )
    """
    gui = InstallerGUI(
        app_name=app_name,
        default_install_path=default_install_path,
        icon_path=icon_path,
        source_files=source_files,
        publisher=publisher,
        main_executable=main_executable
    )
    return gui.run()


# Legacy support - keep for backward compatibility but simplified
class ProgressTracker:
    """Simple progress tracker."""
    
    def __init__(self, total_steps: int = 4):
        self.total_steps = total_steps
        self.current_step = 0
    
    def next_step(self) -> tuple:
        if self.current_step < self.total_steps:
            self.current_step += 1
        return self.current_step, self.total_steps, "Processing..."
    
    def get_progress(self) -> float:
        return self.current_step / self.total_steps if self.total_steps > 0 else 0.0