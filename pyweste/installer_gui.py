import dearpygui.dearpygui as dpg
from pathlib import Path
from PIL import Image
import win32com.client
import pythoncom
from .lib import install_app

class InstallerGUI:
    def __init__(self, app_name="my-app", source_files=None, main_executable=None, 
                 icon_path=None, version="1.0.0", publisher=""):
        self.app_name = app_name
        self.install_path = f"C:/Program Files/{app_name}"
        self.source_files = source_files or []
        self.main_executable = main_executable
        self.icon_path = icon_path
        self.version = version
        self.publisher = publisher
        
    def browse_folder(self):
        """Browse for installation folder."""
        # Initialize COM (important for GUI apps like DearPyGui)
        pythoncom.CoInitialize()
        
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.BrowseForFolder(0, "Select installation folder", 0, 0)
            if folder:
                path = folder.Self.Path
                # Append app name to the selected path
                full_path = str(Path(path) / self.app_name)
                dpg.set_value("install_path", full_path)
                self.install_path = full_path
        finally:
            pythoncom.CoUninitialize()  # cleanup
    
    def install_clicked(self):
        """Handle install button click."""
        # Get values from GUI
        install_path = dpg.get_value("install_path")
        desktop_shortcut = dpg.get_value("desktop_shortcut")
        startmenu_shortcut = dpg.get_value("startmenu_shortcut")
        add_to_programs = dpg.get_value("add_remove_programs")
        
        # Update progress
        dpg.set_value("progress_text", "Installing...")
        dpg.show_item("progress_group")
        
        # Perform installation using the enhanced lib functions
        success = install_app(
            app_name=self.app_name,
            source_files=self.source_files,
            install_path=install_path,
            desktop_shortcut=desktop_shortcut,
            startmenu_shortcut=startmenu_shortcut,
            add_to_programs=add_to_programs,
            main_executable=self.main_executable,
            icon_path=self.icon_path,
            version=self.version,
            publisher=self.publisher
        )
        
        if success:
            dpg.set_value("progress_text", "Installation completed successfully!")
            # Show completion message for 2 seconds then close
            import time
            time.sleep(2)
            dpg.destroy_context()
        else:
            dpg.set_value("progress_text", "Installation failed!")
            dpg.hide_item("progress_group")
    
    def cancel_clicked(self):
        """Handle cancel button click."""
        dpg.destroy_context()
    
    def load_icon(self):
        """Load and prepare icon for the application."""
        try:
            if self.icon_path and Path(self.icon_path).exists():
                icon_path = Path(self.icon_path)
            else:
                # Try default locations
                icon_path = Path(__file__).parent.parent / "core" / "icon.png"
                if not icon_path.exists():
                    icon_path = Path(__file__).parent / "icon.png"
                if not icon_path.exists():
                    return None
                
            with Image.open(icon_path) as img:
                # For viewport icon, use 16x16 or 32x32
                img = img.resize((32, 32), Image.Resampling.LANCZOS).convert('RGBA')
                
                # Save as temporary file for viewport icon
                temp_icon_path = Path(__file__).parent / "temp_icon.ico"
                img.save(temp_icon_path, format='ICO', sizes=[(16,16), (32,32)])
                return str(temp_icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
            return None
    
    def run(self):
        """Run the installer GUI."""
        dpg.create_context()
        
        # Load icon for titlebar
        icon_path = self.load_icon()
        
        # Main window - 400x300 to accommodate progress
        with dpg.window(tag="main_window", width=400, height=300, 
                       no_resize=True, no_collapse=True, no_title_bar=True):
            
            # Add left margin by creating a horizontal group with spacer
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)  # Left margin for entire content
                with dpg.group():
                    # Title
                    dpg.add_spacer(height=10)
                    dpg.add_text(f"Install {self.app_name}", color=(255, 255, 255))
                    dpg.add_separator()
                    
                    # Install location
                    dpg.add_spacer(height=15)
                    dpg.add_text("Installation Directory:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="install_path", default_value=self.install_path, width=220)
                        dpg.add_button(label="Browse", callback=self.browse_folder, width=60)
                    
                    dpg.add_spacer(height=15)
                    
                    # Options
                    dpg.add_text("Installation Options:")
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=15)
                    
                    # Progress group (initially hidden)
                    with dpg.group(tag="progress_group", show=False):
                        dpg.add_text("", tag="progress_text")
                        dpg.add_spacer(height=10)
                    
                    # Buttons at bottom
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=60)
                        dpg.add_button(label="Install", callback=self.install_clicked, width=80, height=30)
                        dpg.add_spacer(width=20)
                        dpg.add_button(label="Cancel", callback=self.cancel_clicked, width=80, height=30)
        
        # Create viewport with icon if available
        if icon_path:
            dpg.create_viewport(title=f"{self.app_name} Setup", width=420, height=320, resizable=False, 
                              small_icon=icon_path, large_icon=icon_path)
        else:
            dpg.create_viewport(title=f"{self.app_name} Setup", width=420, height=320, resizable=False)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

# Example usage function
def create_installer(app_name, source_files, main_executable=None, icon_path=None, 
                    version="1.0.0", publisher="", show_gui=True):
    """
    Create and run an installer for your application.
    
    Args:
        app_name: Name of your application
        source_files: List of (source_path, relative_dest_path) tuples
        main_executable: Relative path to main executable in installation
        icon_path: Path to application icon
        version: Application version
        publisher: Publisher name
        show_gui: Whether to show GUI or install silently
    
    Example:
        create_installer(
            app_name="MyApp",
            source_files=[
                ("dist/myapp.exe", "myapp.exe"),
                ("assets/config.ini", "config.ini"),
                ("assets/icon.png", "icon.png")
            ],
            main_executable="myapp.exe",
            icon_path="assets/icon.png",
            version="1.2.0",
            publisher="My Company"
        )
    """
    if show_gui:
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
        # Silent installation
        return install_app(
            app_name=app_name,
            source_files=source_files,
            desktop_shortcut=True,
            startmenu_shortcut=True,
            add_to_programs=True,
            main_executable=main_executable,
            icon_path=icon_path,
            version=version,
            publisher=publisher
        )