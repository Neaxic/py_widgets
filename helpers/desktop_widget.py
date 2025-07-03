import ctypes
from ctypes import wintypes
import tkinter as tk

class DesktopWidget:
    """
    A class to create desktop-level widgets that stay above the wallpaper 
    but behind applications.
    """
    
    def __init__(self, root):
        """
        Initialize the desktop widget with a tkinter root window.
        
        Args:
            root: tkinter.Tk() instance
        """
        self.root = root
        self.hwnd = None
        
    def setup_desktop_level(self):
        """
        Configure the window to stay at desktop level (above wallpaper, below applications).
        """
        try:
            # Get window handle
            self.hwnd = self.root.winfo_id()
            
            # Set window to be a desktop widget
            # GWL_EXSTYLE = -20, WS_EX_TOOLWINDOW = 0x00000080
            ctypes.windll.user32.SetWindowLongW(
                self.hwnd, 
                -20, 
                0x00000080
            )
            
            # Position window at desktop level
            # HWND_BOTTOM = 1, SWP_NOMOVE = 0x0002, SWP_NOSIZE = 0x0001
            HWND_BOTTOM = 1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            
            ctypes.windll.user32.SetWindowPos(
                self.hwnd, 
                HWND_BOTTOM, 
                0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE
            )
            
        except Exception as e:
            print(f"Warning: Could not set desktop level positioning: {e}")
            
    def make_draggable(self):
        """
        Make the widget draggable by clicking and dragging.
        """
        def start_drag(event):
            self.root.start_x = event.x
            self.root.start_y = event.y
            
        def drag_window(event):
            x = self.root.winfo_pointerx() - self.root.start_x
            y = self.root.winfo_pointery() - self.root.start_y
            self.root.geometry(f"+{x}+{y}")
            
        # Bind drag events to the root window
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", drag_window)
        
    def make_draggable_with_key(self, key="ctrl"):
        """
        Make the widget draggable only when holding a specific key.
        
        Args:
            key: str - "ctrl", "shift", "alt", or specific key like "m"
        """
        def start_drag(event):
            # Check if the required key is pressed
            if key == "ctrl" and event.state & 0x4:  # Ctrl key
                self.root.start_x = event.x
                self.root.start_y = event.y
                self.root.config(cursor="fleur")  # Change cursor to indicate drag mode
            elif key == "shift" and event.state & 0x1:  # Shift key
                self.root.start_x = event.x
                self.root.start_y = event.y
                self.root.config(cursor="fleur")
            elif key == "alt" and event.state & 0x8:  # Alt key
                self.root.start_x = event.x
                self.root.start_y = event.y
                self.root.config(cursor="fleur")
            else:
                self.root.config(cursor="")
                
        def drag_window(event):
            if hasattr(self.root, 'start_x') and hasattr(self.root, 'start_y'):
                x = self.root.winfo_pointerx() - self.root.start_x
                y = self.root.winfo_pointery() - self.root.start_y
                self.root.geometry(f"+{x}+{y}")
                
        def stop_drag(event):
            self.root.config(cursor="")
            if hasattr(self.root, 'start_x'):
                delattr(self.root, 'start_x')
            if hasattr(self.root, 'start_y'):
                delattr(self.root, 'start_y')
            
        # Bind drag events
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", drag_window)
        self.root.bind("<ButtonRelease-1>", stop_drag)
        
    def toggle_move_mode_on_double_click(self):
        """
        Double-click to toggle between move mode and locked mode.
        """
        self.move_mode = False
        self.original_bg = None
        
        def toggle_mode(event):
            self.move_mode = not self.move_mode
            if self.move_mode:
                # Enter move mode - change appearance
                if not self.original_bg:
                    self.original_bg = self.root.cget("bg")
                self.root.configure(relief="raised", bd=2)
                self.root.config(cursor="fleur")
                print("Move mode ON - Click and drag to move")
            else:
                # Exit move mode - restore appearance
                self.root.configure(relief="flat", bd=0)
                self.root.config(cursor="")
                print("Move mode OFF - Widget locked")
                
        def start_drag(event):
            if self.move_mode:
                self.root.start_x = event.x
                self.root.start_y = event.y
                
        def drag_window(event):
            if self.move_mode and hasattr(self.root, 'start_x'):
                x = self.root.winfo_pointerx() - self.root.start_x
                y = self.root.winfo_pointery() - self.root.start_y
                self.root.geometry(f"+{x}+{y}")
                
        # Bind events
        self.root.bind("<Double-Button-1>", toggle_mode)
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", drag_window)
        
    def enable_hover_move_key(self, key="m"):
        """
        Enable moving when hovering over widget and pressing a key.
        
        Args:
            key: str - key to press while hovering to enable move mode
        """
        self.hover_move_active = False
        
        def on_enter(event):
            self.root.focus_set()  # Give focus to receive key events
            
        def on_leave(event):
            self.hover_move_active = False
            self.root.config(cursor="")
            
        def on_key_press(event):
            if event.keysym.lower() == key.lower():
                self.hover_move_active = True
                self.root.config(cursor="fleur")
                print(f"Move mode ON - Press '{key.upper()}' + drag to move")
                
        def on_key_release(event):
            if event.keysym.lower() == key.lower():
                self.hover_move_active = False
                self.root.config(cursor="")
                print("Move mode OFF")
                
        def start_drag(event):
            if self.hover_move_active:
                self.root.start_x = event.x
                self.root.start_y = event.y
                
        def drag_window(event):
            if self.hover_move_active and hasattr(self.root, 'start_x'):
                x = self.root.winfo_pointerx() - self.root.start_x
                y = self.root.winfo_pointery() - self.root.start_y
                self.root.geometry(f"+{x}+{y}")
                
        # Bind events
        self.root.bind("<Enter>", on_enter)
        self.root.bind("<Leave>", on_leave)
        self.root.bind(f"<KeyPress-{key}>", on_key_press)
        self.root.bind(f"<KeyRelease-{key}>", on_key_release)
        self.root.bind("<Button-1>", start_drag)
        self.root.bind("<B1-Motion>", drag_window)
        
    def enable_edge_snap(self, margin=20):
        """
        Enable snapping to screen edges when dragging.
        
        Args:
            margin: int - distance from edge to trigger snap
        """
        def snap_to_edges():
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Get window position and size
            self.root.update_idletasks()
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Check for edge snapping
            new_x, new_y = x, y
            
            # Left edge
            if x < margin:
                new_x = 0
            # Right edge
            elif x + width > screen_width - margin:
                new_x = screen_width - width
                
            # Top edge
            if y < margin:
                new_y = 0
            # Bottom edge
            elif y + height > screen_height - margin:
                new_y = screen_height - height
                
            if new_x != x or new_y != y:
                self.root.geometry(f"+{new_x}+{new_y}")
                
        # Override existing drag method to include snapping
        original_drag = getattr(self.root, 'drag_window', None)
        
        def drag_with_snap(event):
            if original_drag:
                original_drag(event)
            self.root.after(50, snap_to_edges)  # Snap after brief delay
            
        self.root.drag_window = drag_with_snap
        
    def make_resizable(self):
        """
        Make the widget resizable by removing the overrideredirect restriction.
        Note: This may interfere with desktop-level positioning.
        """
        self.root.overrideredirect(False)
        
    def set_transparency(self, alpha=0.9):
        """
        Set window transparency.
        
        Args:
            alpha: float between 0.0 (fully transparent) and 1.0 (fully opaque)
        """
        self.root.attributes("-alpha", alpha)
        
    def set_click_through(self, enabled=True):
        """
        Make the window click-through (mouse events pass through to windows below).
        
        Args:
            enabled: bool to enable/disable click-through
        """
        if self.hwnd:
            try:
                # WS_EX_TRANSPARENT = 0x00000020
                if enabled:
                    # Get current extended style
                    current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
                    # Add transparent flag
                    new_style = current_style | 0x00000020
                else:
                    # Remove transparent flag
                    current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
                    new_style = current_style & ~0x00000020
                    
                ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, new_style)
            except Exception as e:
                print(f"Warning: Could not set click-through: {e}")
                
    def hide_from_taskbar(self):
        """
        Hide the window from the taskbar.
        """
        if self.hwnd:
            try:
                # Get current extended style and add WS_EX_TOOLWINDOW
                current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
                new_style = current_style | 0x00000080
                ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, new_style)
            except Exception as e:
                print(f"Warning: Could not hide from taskbar: {e}")
