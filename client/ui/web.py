import sys
import psutil
import ctypes
from ctypes import wintypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QCursor
import time

# Basic HTML template styled like iOS battery widget
html_template = """
<html>
<head>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #f0f0f0;
    user-select: none;
    -webkit-user-select: none;
    pointer-events: none;  /* Make HTML non-interactive for dragging */
    background: transparent;
  }}
  .container {{
    background: rgba(20, 20, 20, 0.85);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 15px 20px;
    width: 220px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
    border: {border_style};
    cursor: {cursor_style};
  }}
  .title {{
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 10px;
    color: #ffffff;
  }}
  .bar-container {{
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    overflow: hidden;
    height: 16px;
  }}
  .bar {{
    height: 100%;
    background: linear-gradient(to right, #4cd964, #34c759);
    width: {cpu_percent}%;
    transition: width 0.4s ease;
  }}
  .label {{
    margin-top: 8px;
    font-size: 13px;
    text-align: right;
    color: #cccccc;
  }}
  .help-text {{
    font-size: 10px;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 5px;
    text-align: center;
    opacity: {help_opacity};
    transition: opacity 0.3s ease;
  }}
</style>
</head>
<body>
  <div class="container">
    <div class="title">CPU Usage</div>
    <div class="bar-container">
      <div class="bar"></div>
    </div>
    <div class="label">{cpu_percent}%</div>
    <div class="help-text">Ctrl+Drag to move • Double-click to lock/unlock</div>
  </div>
</body>
</html>
"""

# Watchlist widget template with iOS styling
watchlist_template = """
<html>
<head>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    user-select: none;
    -webkit-user-select: none;
    pointer-events: none;
    background: transparent;
  }}
  .widget {{
    border-radius: 16px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    width: 128px;
    height: 128px;
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(31, 41, 55, 0.3);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.6);
    border: {border_style};
    cursor: {cursor_style};
  }}
  .header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }}
  .title {{
    color: #d1d5db;
    font-size: 12px;
    font-weight: 500;
  }}
  .icon {{
    font-size: 16px;
    opacity: 0.7;
  }}
  .watchlist-content {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex: 1;
    justify-content: space-evenly;
  }}
  .watchlist-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .secondary {{
    color: #9ca3af;
    font-size: 12px;
  }}
  .price-section {{
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .price {{
    color: white;
    font-size: 12px;
  }}
  .green {{ color: #4ade80; }}
  .red {{ color: #f87171; }}
</style>
</head>
<body>
  <div class="widget">
    <div class="header">
      <div class="title">Watchlist</div>
      <div class="icon">💲</div>
    </div>
    <div class="watchlist-content">
      <div class="watchlist-row">
        <div class="secondary">TSLA</div>
        <div class="price-section">
          <span class="price">${tsla_price}</span>
          <span class="{tsla_color}">{tsla_arrow}</span>
        </div>
      </div>
      <div class="watchlist-row">
        <div class="secondary">NVDA</div>
        <div class="price-section">
          <span class="price">${nvda_price}</span>
          <span class="{nvda_color}">{nvda_arrow}</span>
        </div>
      </div>
      <div class="watchlist-row">
        <div class="secondary">MSFT</div>
        <div class="price-section">
          <span class="price">${msft_price}</span>
          <span class="{msft_color}">{msft_arrow}</span>
        </div>
      </div>
      <div class="watchlist-row">
        <div class="secondary">AAPL</div>
        <div class="price-section">
          <span class="price">${aapl_price}</span>
          <span class="{aapl_color}">{aapl_arrow}</span>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

class DragOverlay(QWidget):
    """Transparent overlay widget to handle dragging."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.main_widget = parent
        self.setGeometry(parent.rect())
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
        
        # Dragging state
        self.is_dragging = False
        self.drag_position = QPoint()
        self.last_click_time = 0
        
        # Make sure we get mouse events
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            print(f"Overlay mouse press at: {event.pos()}")
            
            # Check for double-click
            current_time = time.time()
            if current_time - self.last_click_time < 0.3:
                print("Double-click detected!")
                self.main_widget.toggle_move_mode()
                return
                
            self.last_click_time = current_time
            
            # Check if we should start dragging
            modifiers = QApplication.keyboardModifiers()
            if (modifiers & Qt.ControlModifier) or self.main_widget.is_move_mode:
                print("Starting drag from overlay")
                self.is_dragging = True
                self.drag_position = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                self.main_widget.setCursor(Qt.ClosedHandCursor)
                
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.is_dragging:
            # Calculate new position
            delta = event.pos() - self.drag_position
            new_pos = self.main_widget.pos() + delta
            
            # Apply edge snapping
            new_pos = self.main_widget.apply_edge_snap(new_pos)
            
            print(f"Moving widget to: {new_pos}")
            self.main_widget.move(new_pos)
            
            # Reapply desktop level after moving
            if self.main_widget.hwnd:
                QTimer.singleShot(10, self.main_widget._reapply_desktop_level)
                
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton and self.is_dragging:
            print("Ending drag from overlay")
            self.is_dragging = False
            if not self.main_widget.is_move_mode:
                self.setCursor(Qt.ArrowCursor)
                self.main_widget.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.OpenHandCursor)
                self.main_widget.setCursor(Qt.OpenHandCursor)
                
    def enterEvent(self, event):
        """Show help when hovering."""
        self.main_widget.show_help()
        
    def leaveEvent(self, event):
        """Hide help when leaving."""
        self.main_widget.hide_help()

class WatchlistWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Widget state - initialize all state variables first
        self.is_dragging = False
        self.is_move_mode = False
        self.snap_margin = 30
        self.hwnd = None
        self.help_visible = True
        
        # Mock stock data - replace with real API calls
        self.stocks = {
            'TSLA': {'price': 248.50, 'change': 1.2},
            'NVDA': {'price': 875.30, 'change': -0.8},
            'MSFT': {'price': 378.85, 'change': 0.5},
            'AAPL': {'price': 189.25, 'change': 1.84}
        }
        
        self.setup_window()
        self.setup_web_view()
        self.setup_overlay()
        self.setup_timer()
        self.setup_desktop_level()
        
        # Show help initially, then fade after 3 seconds
        QTimer.singleShot(3000, self.fade_help)
        
    def setup_window(self):
        """Configure the main window properties."""
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(160, 160)  # Small widget size
        
    def setup_web_view(self):
        """Set up the web engine view."""
        self.view = QWebEngineView(self)
        self.view.setStyleSheet("background: transparent;")
        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.page().setBackgroundColor(Qt.transparent)
        self.view.setGeometry(self.rect())
        self.update_html()
        
    def setup_overlay(self):
        """Set up the transparent drag overlay."""
        self.overlay = DragOverlay(self)
        self.overlay.show()
        
    def setup_timer(self):
        """Set up the update timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_html)
        self.timer.start(5000)  # Update every 5 seconds
        
    def setup_desktop_level(self):
        """Configure desktop-level positioning (Windows only)."""
        try:
            QTimer.singleShot(200, self._apply_desktop_level)
        except Exception as e:
            print(f"Warning: Could not set desktop level positioning: {e}")
            
    def _apply_desktop_level(self):
        """Apply desktop level positioning to stay behind applications."""
        try:
            self.hwnd = int(self.winId())
            
            HWND_BOTTOM = 1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            
            current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
            new_style = current_style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, new_style)
            
            ctypes.windll.user32.SetWindowPos(
                self.hwnd, 
                HWND_BOTTOM, 
                0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
            
        except Exception as e:
            print(f"Warning: Desktop level setup failed: {e}")
            
    def _reapply_desktop_level(self):
        """Reapply desktop level after moving."""
        if self.hwnd:
            try:
                HWND_BOTTOM = 1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                
                ctypes.windll.user32.SetWindowPos(
                    self.hwnd, 
                    HWND_BOTTOM, 
                    0, 0, 0, 0, 
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                )
            except:
                pass
                
    def fade_help(self):
        """Fade out the help text."""
        if not self.is_move_mode:
            self.help_visible = False
            self.update_html()
            
    def show_help(self):
        """Show help text."""
        if not self.is_move_mode:
            self.help_visible = True
            self.update_html()
            
    def hide_help(self):
        """Hide help text."""
        if not self.is_move_mode:
            self.help_visible = False
            self.update_html()
            
    def update_html(self):
        """Update the HTML content with watchlist data."""
        import random
        
        # Simulate stock price changes
        data = {}
        for symbol, stock in self.stocks.items():
            # Simulate slight changes
            change_factor = 1 + (random.random() - 0.5) * 0.02  # ±1% variation
            current_change = stock['change'] * change_factor
            current_price = stock['price'] * (1 + current_change/100)
            
            is_positive = current_change >= 0
            symbol_lower = symbol.lower()
            
            data[f'{symbol_lower}_price'] = f"{current_price:.2f}"
            data[f'{symbol_lower}_color'] = 'green' if is_positive else 'red'
            data[f'{symbol_lower}_arrow'] = '↗' if is_positive else '↘'
        
        # Determine styling based on mode
        if self.is_move_mode:
            data['border_style'] = "2px solid rgba(255, 255, 255, 0.5)"
            data['cursor_style'] = "move"
        else:
            data['border_style'] = "1px solid rgba(31, 41, 55, 0.3)"
            data['cursor_style'] = "default"
        
        html = watchlist_template.format(**data)
        self.view.setHtml(html)
        
    def toggle_move_mode(self):
        """Toggle between move mode and locked mode."""
        self.is_move_mode = not self.is_move_mode
        
        if self.is_move_mode:
            print("Move mode ON - Click and drag to move, or hold Ctrl+drag")
            self.setCursor(Qt.OpenHandCursor)
            self.overlay.setCursor(Qt.OpenHandCursor)
            self.help_visible = True
        else:
            print("Move mode OFF - Widget locked. Hold Ctrl+drag to move")
            self.setCursor(Qt.ArrowCursor)
            self.overlay.setCursor(Qt.ArrowCursor)
            self.help_visible = False
            
        self.update_html()
        
    def apply_edge_snap(self, pos):
        """Apply edge snapping to position."""
        screen = QApplication.desktop().screenGeometry()
        widget_rect = self.frameGeometry()
        
        if pos.x() <= self.snap_margin:
            pos.setX(0)
        elif pos.x() + widget_rect.width() >= screen.width() - self.snap_margin:
            pos.setX(screen.width() - widget_rect.width())
            
        if pos.y() <= self.snap_margin:
            pos.setY(0)
        elif pos.y() + widget_rect.height() >= screen.height() - self.snap_margin:
            pos.setY(screen.height() - widget_rect.height())
            
        return pos
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            if self.is_move_mode:
                self.toggle_move_mode()
        super().keyPressEvent(event)
        
    def resizeEvent(self, event):
        """Handle resize events to update overlay."""
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(self.rect())
        if hasattr(self, 'view'):
            self.view.setGeometry(self.rect())
        
    def set_transparency(self, alpha=0.9):
        """Set window transparency."""
        self.setWindowOpacity(alpha)


class DesktopWebWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Widget state - initialize all state variables first
        self.is_dragging = False
        self.is_move_mode = False
        self.snap_margin = 30
        self.hwnd = None
        self.help_visible = True
        
        self.setup_window()
        self.setup_web_view()
        self.setup_overlay()
        self.setup_timer()
        self.setup_desktop_level()
        
        # Show help initially, then fade after 3 seconds
        QTimer.singleShot(3000, self.fade_help)
        
    def setup_window(self):
        """Configure the main window properties."""
        # Remove WindowStaysOnTopHint since we want desktop level
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(260, 120)
        
    def setup_web_view(self):
        """Set up the web engine view."""
        self.view = QWebEngineView(self)
        self.view.setStyleSheet("background: transparent;")
        self.view.setAttribute(Qt.WA_TranslucentBackground)
        self.view.page().setBackgroundColor(Qt.transparent)
        self.view.setGeometry(self.rect())
        self.update_html()
        
    def setup_overlay(self):
        """Set up the transparent drag overlay."""
        self.overlay = DragOverlay(self)
        self.overlay.show()
        print("Drag overlay created and shown")
        
    def setup_timer(self):
        """Set up the update timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_html)
        self.timer.start(1000)  # Update every second
        
    def setup_desktop_level(self):
        """Configure desktop-level positioning (Windows only)."""
        try:
            QTimer.singleShot(200, self._apply_desktop_level)
        except Exception as e:
            print(f"Warning: Could not set desktop level positioning: {e}")
            
    def _apply_desktop_level(self):
        """Apply desktop level positioning to stay behind applications."""
        try:
            self.hwnd = int(self.winId())
            
            # Set window to desktop level (behind applications, above wallpaper)
            HWND_BOTTOM = 1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            SWP_NOACTIVATE = 0x0010
            
            # Set extended window style
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            
            current_style = ctypes.windll.user32.GetWindowLongW(self.hwnd, -20)
            new_style = current_style | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongW(self.hwnd, -20, new_style)
            
            # Position at bottom of Z-order (desktop level)
            ctypes.windll.user32.SetWindowPos(
                self.hwnd, 
                HWND_BOTTOM, 
                0, 0, 0, 0, 
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
            
            print("Widget positioned at desktop level - applications will appear on top")
            
        except Exception as e:
            print(f"Warning: Desktop level setup failed: {e}")
            
    def _reapply_desktop_level(self):
        """Reapply desktop level after moving."""
        if self.hwnd:
            try:
                HWND_BOTTOM = 1
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOACTIVATE = 0x0010
                
                ctypes.windll.user32.SetWindowPos(
                    self.hwnd, 
                    HWND_BOTTOM, 
                    0, 0, 0, 0, 
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
                )
            except:
                pass
                
    def fade_help(self):
        """Fade out the help text."""
        if not self.is_move_mode:
            self.help_visible = False
            self.update_html()
            
    def show_help(self):
        """Show help text."""
        if not self.is_move_mode:
            self.help_visible = True
            self.update_html()
            
    def hide_help(self):
        """Hide help text."""
        if not self.is_move_mode:
            self.help_visible = False
            self.update_html()
        
    def update_html(self):
        """Update the HTML content."""
        cpu = int(psutil.cpu_percent())
        
        # Determine styling based on mode
        if self.is_move_mode:
            border_style = "2px solid rgba(255, 255, 255, 0.5)"
            cursor_style = "move"
        else:
            border_style = "none"
            cursor_style = "default"
            
        help_opacity = "1" if self.help_visible or self.is_move_mode else "0"
        
        html = html_template.format(
            cpu_percent=cpu,
            border_style=border_style,
            cursor_style=cursor_style,
            help_opacity=help_opacity
        )
        self.view.setHtml(html)
        
    def toggle_move_mode(self):
        """Toggle between move mode and locked mode."""
        self.is_move_mode = not self.is_move_mode
        
        if self.is_move_mode:
            print("Move mode ON - Click and drag to move, or hold Ctrl+drag")
            self.setCursor(Qt.OpenHandCursor)
            self.overlay.setCursor(Qt.OpenHandCursor)
            self.help_visible = True
        else:
            print("Move mode OFF - Widget locked. Hold Ctrl+drag to move")
            self.setCursor(Qt.ArrowCursor)
            self.overlay.setCursor(Qt.ArrowCursor)
            self.help_visible = False
            
        self.update_html()
        
    def apply_edge_snap(self, pos):
        """Apply edge snapping to position."""
        screen = QApplication.desktop().screenGeometry()
        widget_rect = self.frameGeometry()
        
        # Snap to left edge
        if pos.x() <= self.snap_margin:
            pos.setX(0)
        # Snap to right edge
        elif pos.x() + widget_rect.width() >= screen.width() - self.snap_margin:
            pos.setX(screen.width() - widget_rect.width())
            
        # Snap to top edge  
        if pos.y() <= self.snap_margin:
            pos.setY(0)
        # Snap to bottom edge
        elif pos.y() + widget_rect.height() >= screen.height() - self.snap_margin:
            pos.setY(screen.height() - widget_rect.height())
            
        return pos
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            if self.is_move_mode:
                self.toggle_move_mode()
        super().keyPressEvent(event)
        
    def resizeEvent(self, event):
        """Handle resize events to update overlay."""
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(self.rect())
        if hasattr(self, 'view'):
            self.view.setGeometry(self.rect())
        
    def set_transparency(self, alpha=0.9):
        """Set window transparency."""
        self.setWindowOpacity(alpha)

def main():
    import sys
    app = QApplication(sys.argv)
    
    # Check command line argument to choose widget type
    widget_type = "cpu"  # default
    if len(sys.argv) > 1:
        widget_type = sys.argv[1].lower()
    
    if widget_type == "watchlist":
        # Create watchlist widget
        w = WatchlistWidget()
        w.move(320, 50)  # Position it differently from CPU widget
        print("Watchlist Widget loaded!")
        print("Shows: TSLA, NVDA, MSFT prices")
    else:
        # Create CPU widget (default)
        w = DesktopWebWidget()
        w.move(50, 50)
        print("CPU Widget loaded!")
    
    w.show()
    w.set_transparency(0.9)
    
    print("Controls:")
    print("- Ctrl+Drag: Move the widget")
    print("- Double-click: Toggle move mode (easier dragging)")
    print("- Hover: Show controls")
    print("- ESC: Exit move mode")
    print()
    print("Usage:")
    print("- python web.py          (CPU widget)")
    print("- python web.py watchlist (Watchlist widget)")
    
    sys.exit(app.exec_())

def run_both():
    """Run both widgets at the same time"""
    app = QApplication(sys.argv)
    
    # Create CPU widget
    cpu_widget = DesktopWebWidget()
    cpu_widget.move(50, 50)
    cpu_widget.set_transparency(0.9)
    cpu_widget.show()
    
    # Create Watchlist widget
    watchlist_widget = WatchlistWidget()
    watchlist_widget.move(320, 50)
    watchlist_widget.set_transparency(0.9)
    watchlist_widget.show()
    
    print("Both widgets loaded!")
    print("- CPU Widget (left)")
    print("- Watchlist Widget (right)")
    print("Controls work on both widgets")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()