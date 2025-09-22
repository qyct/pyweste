import dearpygui.dearpygui as dpg
from pathlib import Path
from PIL import Image
import win32com.client
import pythoncom
import threading
import tempfile
from .installer import install_app
from .files import copy_directory
from .utils import log_info, log_error
from .progress import GUIProgress

class InstallerGUI:
    """Base installer GUI class."""
    
    def __init__(self, app_name: str = "MyApp", source_files: Optional[List] = None, 
                 main_executable: Optional[str] = None, icon_path: Optional[str] = None, 
                 version: str = "1.0.0", publisher: str = "", bundle_dir: Optional[str] = None):
        self.app_name = app_name
        self.install_path = f"C:/Program Files/{app_name}"
        self.source_files = source_files or []
        self.main_executable = main_executable
        self.icon_path = icon_path
        self.version = version
        self.publisher = publisher
        self.bundle_dir = bundle_dir
        self.installing = False
        
    def browse_folder(self):
        """Browse for installation folder."""
        pythoncom.CoInitialize()
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.BrowseForFolder(0, "Select installation folder", 0, 0)
            if folder:
                path = folder.Self.Path
                full_path = str(Path(path) / self.app_name)
                dpg.set_value("install_path", full_path)
                self.install_path = full_path
        finally:
            pythoncom.CoUninitialize()
    
    def update_progress(self, current: int, total: int):
        """Update progress bar and text."""
        if total > 0:
            progress = current / total
            dpg.set_value("progress_bar", progress)
            dpg.set_value("progress_text", f"Installing... ({current}/{total} files)")
    
    def install_clicked(self):
        """Handle install button click."""
        if self.installing:
            dpg.destroy_context()
            return
            
        if dpg.get_value("install_button") == "Close":
            dpg.destroy_context()
            return
            
        self.install_path = dpg.get_value("install_path")
        desktop_shortcut = dpg.get_value("desktop_shortcut")
        startmenu_shortcut = dpg.get_value("startmenu_shortcut")
        add_to_programs_registry = dpg.get_value("add_remove_programs")
        
        self.installing = True
        
        dpg.set_value("install_button", "Installing...")
        dpg.configure_item("install_button", enabled=False)
        dpg.show_item("progress_group")
        dpg.set_value("progress_text", "Starting installation...")
        
        thread = threading.Thread(target=self.install_thread, args=(
            self.install_path, desktop_shortcut, startmenu_shortcut, add_to_programs_registry
        ))
        thread.daemon = True
        thread.start()
    
    def install_thread(self, install_path: str, desktop_shortcut: bool, 
                      startmenu_shortcut: bool, add_to_programs_registry: bool):
        """Installation thread to avoid blocking GUI."""
        try:
            success = install_app(
                app_name=self.app_name,
                source_files=self.source_files,
                bundle_dir=self.bundle_dir,
                install_path=install_path,
                desktop_shortcut=desktop_shortcut,
                startmenu_shortcut=startmenu_shortcut,
                add_to_programs_registry=add_to_programs_registry,
                main_executable=self.main_executable,
                icon_path=self.icon_path,
                version=self.version,
                publisher=self.publisher,
                progress_callback=self.update_progress,
                show_gui=False
            )
            
            if success:
                dpg.set_value("progress_text", "Installation completed successfully!")
                dpg.set_value("progress_bar", 1.0)
            else:
                dpg.set_value("progress_text", "Installation failed!")
                
        except Exception as e:
            dpg.set_value("progress_text", f"Installation failed: {str(e)}")
        finally:
            dpg.set_value("install_button", "Close")
            dpg.configure_item("install_button", enabled=True)
            self.installing = False
    
    def run(self):
        """Run the installer GUI."""
        dpg.create_context()
        
        with dpg.window(tag="main_window", width=420, height=350, 
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
                        dpg.add_input_text(tag="install_path", default_value=self.install_path, width=240)
                        dpg.add_button(label="Browse", callback=self.browse_folder, width=70)
                    
                    dpg.add_spacer(height=20)
                    dpg.add_text("Installation Options:")
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=20)
                    
                    with dpg.group(tag="progress_group", show=False):
                        dpg.add_text("Ready to install", tag="progress_text")
                        dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=300)
                        dpg.add_spacer(height=15)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=80)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=90, height=35)
                        dpg.add_spacer(width=25)
                        dpg.add_button(label="Cancel", callback=lambda: dpg.destroy_context(), width=90, height=35)
        
        dpg.create_viewport(title=f"{self.app_name} Setup", width=440, height=370, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

class BundleInstallerGUI(InstallerGUI):
    """Specialized GUI for bundle installations."""
    
    def __init__(self, app_name: str, bundle_dir: str, main_executable: str = "run.bat", **kwargs):
        super().__init__(
            app_name=app_name,
            main_executable=main_executable,
            bundle_dir=bundle_dir,
            **kwargs
        )
        # Set icon path if it exists in bundle
        bin_icon = Path(bundle_dir) / "bin" / "icon.ico"
        if bin_icon.exists() and not self.icon_path:
            self.icon_path = str(bin_icon)

def create_installer(app_name: str, source_files: Optional[List] = None, bundle_dir: Optional[str] = None, 
                    main_executable: Optional[str] = None, icon_path: Optional[str] = None, 
                    version: str = "1.0.0", publisher: str = "", show_gui: bool = True):
    """Create and run an installer for your application."""
    if show_gui:
        if bundle_dir:
            gui = BundleInstallerGUI(
                app_name=app_name,
                bundle_dir=bundle_dir,
                main_executable=main_executable or "run.bat",
                icon_path=icon_path,
                version=version,
                publisher=publisher
            )
        else:
            gui = InstallerGUI(
                app_name=app_name,
                source_files=source_files,
                main_executable=main_executable,
                icon_path=icon_path,
                version=version,
                publisher=publisher
            )
        gui.run()
    else:
        return install_app(
            app_name=app_name,
            source_files=source_files,
            bundle_dir=bundle_dir,
            main_executable=main_executable,
            icon_path=icon_path,
            version=version,
            publisher=publisher,
            show_gui=False
        )