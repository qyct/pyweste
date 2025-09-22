"""
GUI installer using DearPyGui for pyweste
"""

import dearpygui.dearpygui as dpg
from pathlib import Path
from PIL import Image
import win32com.client
import pythoncom
import threading
import tempfile
from .lib import install_app
from .copy import copy_directory_tree


class InstallerGUI:
    def __init__(self, app_name="my-app", source_files=None, main_executable=None, 
                 icon_path=None, version="1.0.0", publisher="", bundle_dir=None):
        self.app_name = app_name
        self.install_path = f"C:/Program Files/{app_name}"
        self.source_files = source_files or []
        self.main_executable = main_executable
        self.icon_path = icon_path
        self.version = version
        self.publisher = publisher
        self.bundle_dir = bundle_dir  # For copying entire directories
        self.installing = False
        
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
    
    def update_progress(self, current, total):
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
            
        # Get values from GUI
        install_path = dpg.get_value("install_path")
        desktop_shortcut = dpg.get_value("desktop_shortcut")
        startmenu_shortcut = dpg.get_value("startmenu_shortcut")
        add_to_programs = dpg.get_value("add_remove_programs")
        
        self.install_path = install_path
        self.installing = True
        
        # Update UI
        dpg.set_value("install_button", "Installing...")
        dpg.configure_item("install_button", enabled=False)
        dpg.show_item("progress_group")
        dpg.set_value("progress_text", "Starting installation...")
        
        # Start installation in separate thread
        thread = threading.Thread(target=self.install_thread, args=(
            install_path, desktop_shortcut, startmenu_shortcut, add_to_programs
        ))
        thread.daemon = True
        thread.start()
    
    def install_thread(self, install_path, desktop_shortcut, startmenu_shortcut, add_to_programs):
        """Installation thread to avoid blocking GUI."""
        try:
            if self.bundle_dir:
                # Copy entire bundle directory
                success = copy_directory_tree(
                    self.bundle_dir, 
                    install_path,
                    exclude_patterns=['*.pyc', '__pycache__', '.git'],
                    progress_callback=self.update_progress
                )
            else:
                # Use traditional file list installation
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
                dpg.set_value("progress_bar", 1.0)
                dpg.set_value("install_button", "Close")
                dpg.configure_item("install_button", enabled=True)
            else:
                dpg.set_value("progress_text", "Installation failed!")
                dpg.set_value("install_button", "Close")
                dpg.configure_item("install_button", enabled=True)
                
        except Exception as e:
            dpg.set_value("progress_text", f"Installation failed: {str(e)}")
            dpg.set_value("install_button", "Close")
            dpg.configure_item("install_button", enabled=True)
        finally:
            self.installing = False
    
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
                possible_paths = [
                    Path(__file__).parent.parent / "core" / "icon.png",
                    Path(__file__).parent / "icon.png",
                    Path(__file__).parent / "icon.ico"
                ]
                
                icon_path = None
                for path in possible_paths:
                    if path.exists():
                        icon_path = path
                        break
                
                if not icon_path:
                    return None
                
            # Handle different image formats
            if icon_path.suffix.lower() == '.ico':
                # Use ICO file directly
                return str(icon_path)
            else:
                # Convert to ICO
                with Image.open(icon_path) as img:
                    # For viewport icon, use 16x16 or 32x32
                    img = img.resize((32, 32), Image.Resampling.LANCZOS).convert('RGBA')
                    
                    # Save as temporary ICO file
                    temp_icon_path = Path(tempfile.gettempdir()) / f"pyweste_icon_{self.app_name}.ico"
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
        
        # Main window - 420x350 to accommodate progress
        with dpg.window(tag="main_window", width=420, height=350, 
                       no_resize=True, no_collapse=True, no_title_bar=True):
            
            # Add left margin by creating a horizontal group with spacer
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=15)  # Left margin for entire content
                with dpg.group():
                    # Title
                    dpg.add_spacer(height=15)
                    dpg.add_text(f"Install {self.app_name}", color=(255, 255, 255))
                    dpg.add_separator()
                    
                    # Install location
                    dpg.add_spacer(height=20)
                    dpg.add_text("Installation Directory:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="install_path", default_value=self.install_path, width=240)
                        dpg.add_button(label="Browse", callback=self.browse_folder, width=70)
                    
                    dpg.add_spacer(height=20)
                    
                    # Options
                    dpg.add_text("Installation Options:")
                    dpg.add_checkbox(tag="desktop_shortcut", label="Create desktop shortcut", default_value=True)
                    dpg.add_checkbox(tag="startmenu_shortcut", label="Create start menu shortcut", default_value=True)
                    dpg.add_checkbox(tag="add_remove_programs", label="Add to Add/Remove Programs", default_value=True)
                    
                    dpg.add_spacer(height=20)
                    
                    # Progress group (initially hidden)
                    with dpg.group(tag="progress_group", show=False):
                        dpg.add_text("Ready to install", tag="progress_text")
                        dpg.add_progress_bar(tag="progress_bar", default_value=0.0, width=300)
                        dpg.add_spacer(height=15)
                    
                    # Buttons at bottom
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=80)
                        dpg.add_button(tag="install_button", label="Install", 
                                     callback=self.install_clicked, width=90, height=35)
                        dpg.add_spacer(width=25)
                        dpg.add_button(label="Cancel", callback=self.cancel_clicked, width=90, height=35)
        
        # Create viewport with icon if available
        if icon_path:
            dpg.create_viewport(title=f"{self.app_name} Setup", width=440, height=370, resizable=False, 
                              small_icon=icon_path, large_icon=icon_path)
        else:
            dpg.create_viewport(title=f"{self.app_name} Setup", width=440, height=370, resizable=False)
        
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()
        
        # Cleanup temp icon file
        if icon_path and 'temp' in icon_path:
            try:
                Path(icon_path).unlink(missing_ok=True)
            except:
                pass


class BundleInstallerGUI(InstallerGUI):
    """Specialized GUI for bundle installations (like from inst.py)."""
    
    def __init__(self, app_name, bundle_dir, main_executable="run.bat", **kwargs):
        super().__init__(
            app_name=app_name,
            main_executable=main_executable,
            bundle_dir=bundle_dir,
            **kwargs
        )
        # Set icon path to bin/icon.ico if it exists
        bin_icon = Path(bundle_dir) / "bin" / "icon.ico"
        if bin_icon.exists():
            self.icon_path = str(bin_icon)
    
    def create_run_script(self, install_path):
        """Create run.bat script for the bundle."""
        run_script_content = f"""@echo off
cd /d "%~dp0"
bin\\python.exe main.py
"""
        
        try:
            run_path = Path(install_path) / "run.bat"
            with open(run_path, 'w') as f:
                f.write(run_script_content)
            print(f"Created run script: {run_path}")
            return True
        except Exception as e:
            print(f"Failed to create run script: {e}")
            return False
    
    def install_thread(self, install_path, desktop_shortcut, startmenu_shortcut, add_to_programs):
        """Override install thread for bundle-specific installation."""
        try:
            # Copy bundle directory
            dpg.set_value("progress_text", "Copying application files...")
            success = copy_directory_tree(
                self.bundle_dir, 
                install_path,
                exclude_patterns=['*.pyc', '__pycache__', '.git', 'setup.py'],
                progress_callback=self.update_progress
            )
            
            if not success:
                raise Exception("Failed to copy application files")
            
            # Create run script
            dpg.set_value("progress_text", "Creating run script...")
            self.create_run_script(install_path)
            
            # Create shortcuts and registry entries
            main_exe_path = Path(install_path) / self.main_executable
            
            if desktop_shortcut:
                dpg.set_value("progress_text", "Creating desktop shortcut...")
                from .link import create_desktop_shortcut
                create_desktop_shortcut(
                    str(main_exe_path), 
                    self.app_name, 
                    self.icon_path, 
                    f"{self.app_name} Application"
                )
            
            if startmenu_shortcut:
                dpg.set_value("progress_text", "Creating start menu shortcut...")
                from .link import create_startmenu_shortcut
                create_startmenu_shortcut(
                    str(main_exe_path), 
                    self.app_name, 
                    self.icon_path, 
                    f"{self.app_name} Application"
                )
            
            if add_to_programs:
                dpg.set_value("progress_text", "Adding to Add/Remove Programs...")
                from .reg import add_to_programs_and_features
                
                # Create uninstaller
                uninstall_path = self.create_uninstaller(install_path)
                
                add_to_programs_and_features(
                    self.app_name, 
                    install_path, 
                    uninstall_path,
                    self.version, 
                    self.publisher, 
                    self.icon_path,
                    use_current_user=True  # Use current user registry
                )
            
            dpg.set_value("progress_text", "Installation completed successfully!")
            dpg.set_value("progress_bar", 1.0)
            dpg.set_value("install_button", "Close")
            dpg.configure_item("install_button", enabled=True)
            
        except Exception as e:
            dpg.set_value("progress_text", f"Installation failed: {str(e)}")
            dpg.set_value("install_button", "Close")
            dpg.configure_item("install_button", enabled=True)
        finally:
            self.installing = False
    
    def create_uninstaller(self, install_path):
        """Create uninstaller batch script."""
        uninstall_lines = [
            "@echo off",
            f":: Uninstaller for {self.app_name}",
            "",
            f"echo Uninstalling {self.app_name}...",
            "echo.",
            "",
            ":: Remove shortcuts",
            "echo Removing shortcuts...",
            f"del \"%USERPROFILE%\\Desktop\\{self.app_name}.lnk\" 2>nul",
            f"del \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{self.app_name}.lnk\" 2>nul",
            "",
            ":: Remove from Add/Remove Programs",
            "echo Removing from Add/Remove Programs...",
            f"reg delete \"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}\" /f 2>nul",
            "",
            ":: Change to parent directory before deleting",
            "echo Removing application files...",
            f"cd /d \"{Path(install_path).parent}\"",
            "",
            f":: Force delete the installation directory",
            f"rmdir /s /q \"{Path(install_path).name}\" 2>nul",
            "",
            f"echo {self.app_name} has been uninstalled.",
            "echo.",
            "pause"
        ]
        
        uninstall_content = "\n".join(uninstall_lines)
        uninstall_path = Path(install_path) / "uninstall.bat"
        
        try:
            with open(uninstall_path, 'w') as f:
                f.write(uninstall_content)
            return str(uninstall_path)
        except Exception as e:
            print(f"Failed to create uninstaller: {e}")
            return None


# Example usage functions
def create_installer(app_name, source_files=None, bundle_dir=None, main_executable=None, 
                    icon_path=None, version="1.0.0", publisher="", show_gui=True):
    """
    Create and run an installer for your application.
    
    Args:
        app_name: Name of your application
        source_files: List of (source_path, relative_dest_path) tuples
        bundle_dir: Directory containing complete application bundle
        main_executable: Relative path to main executable in installation
        icon_path: Path to application icon
        version: Application version
        publisher: Publisher name
        show_gui: Whether to show GUI or install silently
    """
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
        # Silent installation
        from .lib import install_app
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


def create_bundle_installer(app_name, bundle_dir, **kwargs):
    """
    Create installer specifically for bundle directories.
    
    Args:
        app_name: Name of the application
        bundle_dir: Path to bundle directory containing the application
        **kwargs: Additional arguments passed to BundleInstallerGUI
    """
    gui = BundleInstallerGUI(app_name=app_name, bundle_dir=bundle_dir, **kwargs)
    gui.run()