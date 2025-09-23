"""
PyWeste GUI installer module.
Handles the installer GUI interface and user interaction.
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import Dict, Any, Optional
from .utils import browse_for_folder


class InstallerGUI:
    """GUI installer class that returns user choices."""
    
    def __init__(self, app_name: str = "MyApp", default_install_path: str = None):
        self.app_name = app_name
        self.default_install_path = default_install_path or f"C:/Program Files/{app_name}"
        self.result = None
        self.installing = False
        
    def browse_folder(self):
        """Browse for installation folder."""
        folder_path = browse_for_folder(
            "Select installation folder", 
            self.default_install_path
        )
        if folder_path:
            full_path = str(Path(folder_path) / self.app_name)
            dpg.set_value("install_path", full_path)
    
    def install_clicked(self):
        """Handle install button click."""
        if self.installing:
            return
            
        install_path = dpg.get_value("install_path")
        todo_desktop = dpg.get_value("desktop_shortcut")
        todo_startmenu = dpg.get_value("startmenu_shortcut")
        todo_registry = dpg.get_value("add_remove_programs")
        
        self.result = {
            'todo_copy': True,  # Always copy files
            'todo_desktop': todo_desktop,
            'todo_startmenu': todo_startmenu,
            'todo_registry': todo_registry,
            'install_path': install_path
        }
        
        dpg.destroy_context()
    
    def run(self) -> Optional[Dict[str, Any]]:
        """Run the installer GUI and return user choices."""
        dpg.create_context()
        
        with dpg.window(tag="main_window", width=350, height=250, 
                       no_resize=True, no_collapse=True, no_title_bar=True):
            
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=8)
                with dpg.group():                    
                    dpg.add_spacer(height=16)
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="install_path", default_value=self.default_install_path, width=300)
                        dpg.add_button(label="...", callback=self.browse_folder, width=30)
                    
                    dpg.add_spacer(height=16)
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=16)
                    
                    with dpg.group(horizontal=True):
                        # dpg.add_spacer(width=180)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=75, height=25)
                        dpg.add_spacer(width=25)
        
        dpg.create_viewport(title=f"Setup", width=400, height=260, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return self.result


def start_gui_installer(app_name: str = "MyApp", default_install_path: str = None) -> Optional[Dict[str, Any]]:
    """
    Start GUI installer and return user choices.
    
    Args:
        app_name: Name of the application
        default_install_path: Default installation path
        
    Returns:
        Dict with keys: todo_copy, todo_desktop, todo_startmenu, todo_registry, install_path
        None if user cancelled
        
    Example:
        choices = start_gui_installer("MyApp")
        if choices:
            if choices['todo_copy']:
                do_copy_files(source_files, choices['install_path'])
            if choices['todo_registry']:
                add_to_registry("MyApp", choices['install_path'])
    """
    gui = InstallerGUI(app_name, default_install_path)
    return gui.run()


# Progress tracking classes for advanced GUI usage
class ProgressTracker:
    """Track installation progress for GUI updates."""
    
    def __init__(self, total_steps: int = 4):
        self.total_steps = total_steps
        self.current_step = 0
        self.step_names = [
            "Copying files...",
            "Creating shortcuts...", 
            "Setting up registry...",
            "Finishing installation..."
        ]
    
    def next_step(self) -> tuple:
        """Move to next step and return (current, total, description)."""
        if self.current_step < self.total_steps:
            self.current_step += 1
        
        description = self.step_names[self.current_step - 1] if self.current_step <= len(self.step_names) else "Processing..."
        return self.current_step, self.total_steps, description
    
    def get_progress(self) -> float:
        """Get progress as a float between 0.0 and 1.0."""
        return self.current_step / self.total_steps if self.total_steps > 0 else 0.0


class AdvancedInstallerGUI:
    """Advanced installer GUI with progress tracking."""
    
    def __init__(self, app_name: str = "MyApp", default_install_path: str = None):
        self.app_name = app_name
        self.default_install_path = default_install_path or f"C:/Program Files/{app_name}"
        self.result = None
        self.installing = False
        self.progress_tracker = ProgressTracker()
        
    def browse_folder(self):
        """Browse for installation folder."""
        folder_path = browse_for_folder(
            "Select installation folder", 
            self.default_install_path
        )
        if folder_path:
            full_path = str(Path(folder_path) / self.app_name)
            dpg.set_value("install_path", full_path)
    
    def update_progress(self, step_description: str = None):
        """Update progress bar and text."""
        current, total, description = self.progress_tracker.next_step()
        progress = self.progress_tracker.get_progress()
        
        dpg.set_value("progress_bar", progress)
        dpg.set_value("progress_text", step_description or description)
    
    def install_clicked(self):
        """Handle install button click - starts installation process."""
        if self.installing:
            return
            
        install_path = dpg.get_value("install_path")
        todo_desktop = dpg.get_value("desktop_shortcut")
        todo_startmenu = dpg.get_value("startmenu_shortcut")
        todo_registry = dpg.get_value("add_remove_programs")
        
        self.result = {
            'todo_copy': True,  # Always copy files
            'todo_desktop': todo_desktop,
            'todo_startmenu': todo_startmenu,
            'todo_registry': todo_registry,
            'install_path': install_path,
            'progress_callback': self.update_progress
        }
        
        self.installing = True
        dpg.set_value("install_button", "Installing...")
        dpg.configure_item("install_button", enabled=False)
        dpg.show_item("progress_group")
        dpg.set_value("progress_text", "Starting installation...")
        
        # Note: In real usage, this would trigger the actual installation
        # For now, we just return the choices
        dpg.destroy_context()
    
    def cancel_clicked(self):
        """Handle cancel button click."""
        if not self.installing:
            self.result = None
            dpg.destroy_context()
    
    def run(self) -> Optional[Dict[str, Any]]:
        """Run the advanced installer GUI."""
        dpg.create_context()
        
        with dpg.window(tag="main_window", width=450, height=350, 
                       no_resize=True, no_collapse=True, no_title_bar=True):
            
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=15)
                with dpg.group():
                    dpg.add_spacer(height=15)
                    dpg.add_text(f"Install {self.app_name}", color=(255, 255, 255))
                    dpg.add_separator()
                    
                    dpg.add_spacer(height=20)
                    dpg.add_text("Installation Directory:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="install_path", default_value=self.default_install_path, width=270)
                        dpg.add_button(label="Browse", callback=self.browse_folder, width=70)
                    
                    dpg.add_spacer(height=20)
                    dpg.add_text("Installation Options:")
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=20)
                    
                    # Progress group (hidden initially)
                    with dpg.group(tag="progress_group", show=False):
                        dpg.add_text("Ready to install", tag="progress_text")
                        dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=350)
                        dpg.add_spacer(height=15)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=100)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=90, height=35)
                        dpg.add_spacer(width=25)
                        dpg.add_button(tag="cancel_button", label="Cancel", 
                                     callback=self.cancel_clicked, width=90, height=35)
        
        dpg.create_viewport(title=f"{self.app_name} Setup", width=470, height=370, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return self.result