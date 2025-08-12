"""
Widget Startup Manager
Launches multiple desktop widgets at once with flexible configuration.
"""

import sys
import json
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Import widgets from current structure (web.py)
from ui.web import WatchlistWidget, DesktopWebWidget


class WidgetStartupManager:
    """Manages startup of multiple widgets with configuration."""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'startup_config.json')
        self.widgets = []
        self.app = None
        
    def load_config(self):
        """Load startup configuration from JSON file."""
        default_config = {
            "widgets": [
                {
                    "type": "cpu",
                    "enabled": True,
                    "transparency": 0.9
                },
                {
                    "type": "watchlist", 
                    "enabled": True,
                    "transparency": 0.9
                }
            ],
            "startup_delay": 500,  # Delay between widget launches (ms)
            "auto_position": True   # Automatically offset widget positions
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default config file
                self.save_config(default_config)
                print(f"Created default config file: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
            
    def save_config(self, config):
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def create_widget(self, widget_type):
        """Create a widget instance based on type."""
        widget_map = {
            'cpu': DesktopWebWidget,
            'watchlist': WatchlistWidget,
            'stocks': WatchlistWidget  # Alias
        }
        
        if widget_type.lower() in widget_map:
            return widget_map[widget_type.lower()]()
        else:
            print(f"Warning: Unknown widget type '{widget_type}'")
            return None
            
    def launch_widgets(self, config=None):
        """Launch widgets based on configuration."""
        if config is None:
            config = self.load_config()
            
        self.app = QApplication(sys.argv)
        
        enabled_widgets = [w for w in config['widgets'] if w.get('enabled', True)]
        
        if not enabled_widgets:
            print("No widgets enabled in configuration.")
            return
            
        print(f"Starting {len(enabled_widgets)} widgets...")
        
        # Launch widgets with delays
        for i, widget_config in enumerate(enabled_widgets):
            widget_type = widget_config['type']
            transparency = widget_config.get('transparency', 0.9)
            
            # Use QTimer to delay widget creation
            QTimer.singleShot(
                i * config.get('startup_delay', 500),
                lambda t=widget_type, a=transparency: self._create_and_show_widget(t, a)
            )
            
        print("Widget startup initiated!")
        print("Controls (all widgets):")
        print("- Ctrl+Drag: Move widget")
        print("- Double-click: Toggle move mode")
        print("- ESC: Exit move mode")
        print("- Positions automatically saved")
        print(f"\nConfiguration file: {self.config_file}")
        
        # Run the application
        sys.exit(self.app.exec_())
        
    def _create_and_show_widget(self, widget_type, transparency):
        """Create and show a single widget (called by QTimer)."""
        widget = self.create_widget(widget_type)
        if widget:
            widget.set_transparency(transparency)
            widget.show()
            self.widgets.append(widget)
            print(f"✓ {widget_type.title()} widget started")
            
    def list_widgets(self):
        """List all running widgets."""
        if not self.widgets:
            print("No widgets currently running.")
            return
            
        print(f"Running widgets ({len(self.widgets)}):")
        for i, widget in enumerate(self.widgets, 1):
            widget_name = getattr(widget, 'widget_name', 'unknown')
            pos = widget.pos()
            print(f"  {i}. {widget_name} at ({pos.x()}, {pos.y()})")


def main():
    """Main entry point for startup manager."""
    manager = WidgetStartupManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "config":
            # Show current configuration
            config = manager.load_config()
            print("Current configuration:")
            print(json.dumps(config, indent=2))
            
        elif command == "edit":
            # Open config file for editing
            config_path = manager.config_file
            print(f"Edit configuration file: {config_path}")
            if os.name == 'nt':  # Windows
                os.system(f'notepad "{config_path}"')
            else:  # Unix-like
                os.system(f'nano "{config_path}"')
                
        elif command == "reset":
            # Reset to default configuration
            if os.path.exists(manager.config_file):
                os.remove(manager.config_file)
                print("Configuration reset to defaults.")
            else:
                print("Configuration file doesn't exist.")
                
        elif command in ["help", "h", "?"]:
            print_help()
            
        else:
            print(f"Unknown command: {command}")
            print_help()
    else:
        # Default: launch widgets
        manager.launch_widgets()


def print_help():
    """Print help information."""
    print("""
Desktop Widget Startup Manager

Usage:
    python startup.py           # Launch all enabled widgets
    python startup.py config    # Show current configuration
    python startup.py edit      # Edit configuration file
    python startup.py reset     # Reset configuration to defaults
    python startup.py help      # Show this help

Configuration File:
    - Located at: startup_config.json
    - Controls which widgets to start
    - Set transparency, delays, and other options
    - Auto-created with defaults if missing

Example Configuration:
{
  "widgets": [
    {
      "type": "cpu",
      "enabled": true,
      "transparency": 0.9
    },
    {
      "type": "watchlist",
      "enabled": true,
      "transparency": 0.85
    }
  ],
  "startup_delay": 500,
  "auto_position": true
}

Available Widget Types:
    - cpu        # CPU usage monitor
    - watchlist  # Stock price tracker
    - stocks     # Alias for watchlist
""")


# Predefined startup configurations
def create_minimal_config():
    """Create a minimal configuration with just essential widgets."""
    return {
        "widgets": [
            {"type": "cpu", "enabled": True, "transparency": 0.9}
        ],
        "startup_delay": 0,
        "auto_position": True
    }

def create_full_config():
    """Create a full configuration with all widgets."""
    return {
        "widgets": [
            {"type": "cpu", "enabled": True, "transparency": 0.9},
            {"type": "watchlist", "enabled": True, "transparency": 0.9}
        ],
        "startup_delay": 800,
        "auto_position": True
    }

def create_trading_config():
    """Create a trading-focused configuration."""
    return {
        "widgets": [
            {"type": "watchlist", "enabled": True, "transparency": 0.95}
        ],
        "startup_delay": 0,
        "auto_position": True
    }


if __name__ == "__main__":
    main()
