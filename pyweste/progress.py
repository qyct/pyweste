import sys
from typing import Callable, Optional
from abc import ABC, abstractmethod

class ProgressCallback(ABC):
    """Abstract base class for progress callbacks."""
    
    @abstractmethod
    def __call__(self, current: int, total: int, message: str = ""):
        pass

class ConsoleProgress(ProgressCallback):
    """Console-based progress display."""
    
    def __init__(self, show_percentage: bool = True, show_bar: bool = True, width: int = 50):
        self.show_percentage = show_percentage
        self.show_bar = show_bar
        self.width = width
        self.last_message = ""
    
    def __call__(self, current: int, total: int, message: str = ""):
        if total == 0:
            return
        
        percentage = (current / total) * 100
        filled_width = int((current / total) * self.width)
        
        output_parts = []
        
        if self.show_bar:
            bar = "█" * filled_width + "░" * (self.width - filled_width)
            output_parts.append(f"[{bar}]")
        
        if self.show_percentage:
            output_parts.append(f"{percentage:.1f}%")
        
        if message and message != self.last_message:
            output_parts.append(message)
            self.last_message = message
        
        output_parts.append(f"({current}/{total})")
        
        output = " ".join(output_parts)
        print(f"\r{output}", end="", flush=True)
        
        if current == total:
            print()  # New line when complete

class GUIProgress(ProgressCallback):
    """GUI progress callback for use with DearPyGui or other GUI frameworks."""
    
    def __init__(self, progress_bar_tag: str = None, text_tag: str = None):
        self.progress_bar_tag = progress_bar_tag
        self.text_tag = text_tag
    
    def __call__(self, current: int, total: int, message: str = ""):
        if total == 0:
            return
        
        progress = current / total
        
        try:
            import dearpygui.dearpygui as dpg
            
            if self.progress_bar_tag:
                dpg.set_value(self.progress_bar_tag, progress)
            
            if self.text_tag:
                text = message or f"Progress: {current}/{total}"
                dpg.set_value(self.text_tag, text)
        except ImportError:
            # Fallback to console if DearPyGui not available
            ConsoleProgress()(current, total, message)

# One-line progress functions
create_console_progress = lambda **kwargs: ConsoleProgress(**kwargs)
create_gui_progress = lambda progress_tag=None, text_tag=None: GUIProgress(progress_tag, text_tag)