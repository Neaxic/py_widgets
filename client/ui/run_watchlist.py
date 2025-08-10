"""
Run Watchlist Widget
Simple script to run just the watchlist widget with iOS-style design
"""
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication

# Import from the web.py file
from web import WatchlistWidget

def main():
    app = QApplication(sys.argv)
    
    # Create watchlist widget
    widget = WatchlistWidget()
    widget.move(100, 100)
    widget.set_transparency(0.9)
    widget.show()
    
    print("🎯 Watchlist Widget loaded!")
    print("📊 Showing: TSLA, NVDA, MSFT prices")
    print()
    print("Controls:")
    print("- Ctrl+Drag: Move the widget")
    print("- Double-click: Toggle move mode")
    print("- Hover: Show controls")
    print("- ESC: Exit move mode")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
