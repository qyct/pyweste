import dearpygui.dearpygui as dpg
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from .utils import browse_for_folder
from .files import do_copy_files
from .shortcuts import do_desktop_shortcut, do_startmenu_shortcut
from .registry import add_to_registry


class InstallerGUI:
    def __init__(self, app_name: str = "MyApp", default_install_path: str = None, 
                 icon_path: str = None, source_files: List[Tuple[str, str]] = None):
        self.app_name = app_name
        self.default_install_path = default_install_path or f"C:/Program Files/{app_name}"
        self.icon_path = icon_path
        self.source_files = source_files
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
            
            if todo_desktop:
                # Always point shortcut to run.bat, not to the main executable
                run_bat_path = str(Path(install_path) / "run.bat")
                installed_icon_path = str(Path(install_path) / "bin" / "icon.ico")
                
                # Use installed icon if it exists, otherwise None
                icon_for_shortcut = installed_icon_path if Path(installed_icon_path).exists() else None
                
                if not do_desktop_shortcut(run_bat_path, self.app_name, icon_for_shortcut):
                    print("WARNING: Failed to create desktop shortcut")
            
            # Step 3: Create start menu shortcut
            if todo_startmenu:
                # Always point shortcut to run.bat, not to the main executable
                run_bat_path = str(Path(install_path) / "run.bat")
                installed_icon_path = str(Path(install_path) / "bin" / "icon.ico")
                
                # Use installed icon if it exists, otherwise None
                icon_for_shortcut = installed_icon_path if Path(installed_icon_path).exists() else None
                
                if not do_startmenu_shortcut(run_bat_path, self.app_name, icon_for_shortcut, self.publisher):
                    print("WARNING: Failed to create start menu shortcut")
            
            # Step 4: Add to registry (includes uninstaller creation)
            current_step += 1
            self.update_progress(current_step / total_steps, "Setting up registry...")
            
            if todo_registry:
                # For registry, use the main executable if available, otherwise use run.bat
                registry_executable = self.main_executable if self.main_executable else "run.bat"
                installed_icon_path = str(Path(install_path) / "bin" / "icon.ico")
                registry_icon = installed_icon_path if Path(installed_icon_path).exists() else None
                
                if not add_to_registry(
                    app_name=self.app_name,
                    install_path=install_path,
                    main_executable=registry_executable,
                    icon_path=registry_icon,
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
        
        dpg.set_viewport_small_icon(self.icon_path)
        dpg.set_viewport_large_icon(self.icon_path)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        return self.install_success


def start_gui_installer(app_name: str = "MyApp", default_install_path: str = None, 
                       icon_path: str = None, source_files: List[Tuple[str, str]] = None,
                       main_executable: str = None) -> bool:
    gui = InstallerGUI(
        app_name=app_name,
        default_install_path=default_install_path,
        icon_path=icon_path,
        source_files=source_files,
        main_executable=main_executable
    )
    return gui.run()


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