# Widget manager for handling multiple widgets
import tkinter as tk
from helpers.desktop_widget import DesktopWidget
from ui.widget_ui import WidgetUI
from ui.menu_handler import MenuHandler
from config.settings import UI_CONFIG

class WidgetManager:
    """
    Manages multiple widgets and their calculators.
    """
    
    def __init__(self):
        """Initialize the widget manager."""
        self.widgets = {}
        self.next_widget_id = 1
        
    def create_widget(self, calculator, position_offset=(0, 0)):
        """
        Create a new widget with the given calculator.
        
        Args:
            calculator: BaseCalculator - The calculator to use
            position_offset: tuple - (x, y) offset for positioning
            
        Returns:
            str: Widget ID
        """
        widget_id = f"widget_{self.next_widget_id}"
        self.next_widget_id += 1
        
        # Create new window
        root = tk.Tk()
        
        # Create UI components
        ui = WidgetUI(root)
        
        # Create menu handler
        menu_handler = MenuHandler(
            root, 
            calculator, 
            update_callback=lambda: self.reset_widget(widget_id)
        )
        
        # Create desktop widget
        desktop_widget = DesktopWidget(root)
        
        # Store widget info
        widget_info = {
            'id': widget_id,
            'root': root,
            'calculator': calculator,
            'ui': ui,
            'menu_handler': menu_handler,
            'desktop_widget': desktop_widget,
            'is_running': False
        }
        
        self.widgets[widget_id] = widget_info
        
        # Setup the widget
        self._setup_widget(widget_info, position_offset)
        
        return widget_id
        
    def _setup_widget(self, widget_info, position_offset):
        """Setup a widget with all its components."""
        root = widget_info['root']
        calculator = widget_info['calculator']
        ui = widget_info['ui']
        menu_handler = widget_info['menu_handler']
        desktop_widget = widget_info['desktop_widget']
        
        # Set window title
        root.title(f"{calculator.name} - {widget_info['id']}")
        
        # Apply position offset
        x_offset, y_offset = position_offset
        current_geo = root.geometry()
        if '+' in current_geo:
            size_part = current_geo.split('+')[0]
            root.geometry(f"{size_part}+{100 + x_offset}+{100 + y_offset}")
        
        # Setup desktop widget behavior
        root.after(100, desktop_widget.setup_desktop_level)
        desktop_widget.make_draggable_with_key("ctrl")
        desktop_widget.enable_edge_snap(margin=UI_CONFIG['edge_snap_margin'])
        desktop_widget.set_transparency(UI_CONFIG['transparency'])
        
        # Setup menu system
        ui.bind_all_events(menu_handler.show_context_menu)
        ui.add_status_bar()
        
        # Add widget-specific menu options
        self._add_widget_menu_options(menu_handler, widget_info['id'])
        
    def _add_widget_menu_options(self, menu_handler, widget_id):
        """Add widget-specific menu options."""
        original_create_context_menu = menu_handler.create_context_menu
        
        def enhanced_create_context_menu():
            menu = original_create_context_menu()
            menu.add_separator()
            menu.add_command(label="📋 Clone Widget", command=lambda: self.clone_widget(widget_id))
            menu.add_command(label="🗑️ Close Widget", command=lambda: self.close_widget(widget_id))
            menu.add_command(label="📊 Show All Widgets", command=self.show_all_widgets_info)
            return menu
            
        menu_handler.create_context_menu = enhanced_create_context_menu
        
    def start_widget(self, widget_id):
        """Start the update loop for a widget."""
        if widget_id not in self.widgets:
            return
            
        widget_info = self.widgets[widget_id]
        if widget_info['is_running']:
            return
            
        widget_info['is_running'] = True
        self._update_widget(widget_id)
        
    def _update_widget(self, widget_id):
        """Update a specific widget."""
        if widget_id not in self.widgets:
            return
            
        widget_info = self.widgets[widget_id]
        if not widget_info['is_running']:
            return
            
        try:
            calculator = widget_info['calculator']
            ui = widget_info['ui']
            
            # Update calculator
            calculator.calculate_current_value()
            
            # Update display
            display_text = calculator.get_display_text()
            ui.update_display(display_text)
            
            # Schedule next update
            widget_info['root'].after(UI_CONFIG['update_interval'], lambda: self._update_widget(widget_id))
            
        except tk.TclError:
            # Widget was closed
            self.close_widget(widget_id)
            
    def stop_widget(self, widget_id):
        """Stop the update loop for a widget."""
        if widget_id in self.widgets:
            self.widgets[widget_id]['is_running'] = False
            
    def reset_widget(self, widget_id):
        """Reset a widget's calculator."""
        if widget_id in self.widgets:
            self.widgets[widget_id]['calculator'].reset()
            
    def clone_widget(self, widget_id):
        """Clone an existing widget."""
        if widget_id not in self.widgets:
            return
            
        original_widget = self.widgets[widget_id]
        calculator = original_widget['calculator']
        
        # Create new instance of the same calculator type
        new_calculator = calculator.__class__()
        
        # Create new widget with offset
        offset = (len(self.widgets) * 50, len(self.widgets) * 50)
        new_widget_id = self.create_widget(new_calculator, offset)
        
        # Start the new widget
        self.start_widget(new_widget_id)
        
        return new_widget_id
        
    def close_widget(self, widget_id):
        """Close a specific widget."""
        if widget_id in self.widgets:
            widget_info = self.widgets[widget_id]
            widget_info['is_running'] = False
            
            try:
                widget_info['root'].destroy()
            except:
                pass
                
            del self.widgets[widget_id]
            
    def close_all_widgets(self):
        """Close all widgets."""
        widget_ids = list(self.widgets.keys())
        for widget_id in widget_ids:
            self.close_widget(widget_id)
            
    def get_widget_info(self, widget_id):
        """Get information about a specific widget."""
        if widget_id in self.widgets:
            widget_info = self.widgets[widget_id]
            return {
                'id': widget_id,
                'calculator_name': widget_info['calculator'].name,
                'calculator_type': widget_info['calculator'].__class__.__name__,
                'is_running': widget_info['is_running']
            }
        return None
        
    def list_widgets(self):
        """List all widgets."""
        return [self.get_widget_info(widget_id) for widget_id in self.widgets.keys()]
        
    def show_all_widgets_info(self):
        """Show information about all widgets."""
        widgets_info = self.list_widgets()
        
        message = "🖥️ ACTIVE WIDGETS 🖥️\n\n"
        
        if not widgets_info:
            message += "No widgets currently running."
        else:
            for info in widgets_info:
                status = "🟢 Running" if info['is_running'] else "🔴 Stopped"
                message += f"• {info['calculator_name']} ({info['id']})\n"
                message += f"  Type: {info['calculator_type']}\n"
                message += f"  Status: {status}\n\n"
        
        # Create info window
        info_window = tk.Toplevel()
        info_window.title("Widget Manager")
        info_window.geometry("400x300")
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, message)
        text_widget.config(state=tk.DISABLED)
        
        close_btn = tk.Button(info_window, text="Close", command=info_window.destroy)
        close_btn.pack(pady=5)
