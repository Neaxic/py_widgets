# Widget Startup System

A flexible system to launch multiple desktop widgets at once with configuration management.

## 🚀 Quick Start

### Windows (Easy Way):
1. **Double-click** `start_widgets.bat` to launch all widgets
2. Or right-click → "Run with PowerShell" on `start_widgets.ps1`

### Command Line:
```bash
# Start all enabled widgets
python startup.py

# Show current configuration
python startup.py config

# Edit configuration file
python startup.py edit

# Reset to defaults
python startup.py reset

# Show help
python startup.py help
```

## ⚙️ Configuration

The system uses `startup_config.json` to control which widgets to launch:

```json
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
      "transparency": 0.9
    }
  ],
  "startup_delay": 500,
  "auto_position": true
}
```

### Configuration Options:

- **`type`**: Widget type (`cpu`, `watchlist`, `stocks`)
- **`enabled`**: Whether to start this widget (true/false)
- **`transparency`**: Widget opacity (0.0 to 1.0)
- **`startup_delay`**: Delay between launching widgets (milliseconds)
- **`auto_position`**: Automatically offset widget positions

## 📋 Available Widget Types

| Type | Description | Size |
|------|-------------|------|
| `cpu` | CPU usage monitor | 260x120 |
| `watchlist` | Stock price tracker | 160x160 |
| `stocks` | Alias for watchlist | 160x160 |

## 🎯 Usage Scenarios

### 1. Minimal Setup (CPU only):
```json
{
  "widgets": [
    {"type": "cpu", "enabled": true, "transparency": 0.9}
  ],
  "startup_delay": 0
}
```

### 2. Trading Setup (Stocks only):
```json
{
  "widgets": [
    {"type": "watchlist", "enabled": true, "transparency": 0.95}
  ],
  "startup_delay": 0
}
```

### 3. Full Setup (All widgets):
```json
{
  "widgets": [
    {"type": "cpu", "enabled": true, "transparency": 0.9},
    {"type": "watchlist", "enabled": true, "transparency": 0.9}
  ],
  "startup_delay": 800
}
```

## 🔧 Advanced Features

### Startup Delay
Widgets launch with a configurable delay to prevent overwhelming the system:
- `0ms`: All widgets start immediately
- `500ms`: Half-second delay between widgets (recommended)
- `1000ms`: One-second delay (for slower systems)

### Transparency Control
Each widget can have individual transparency:
- `1.0`: Completely opaque
- `0.9`: Slight transparency (recommended)
- `0.7`: More transparent
- `0.5`: Very transparent

### Auto-disable Widgets
Temporarily disable widgets without removing configuration:
```json
{
  "type": "watchlist",
  "enabled": false,  // ← Widget won't start
  "transparency": 0.9
}
```

## 🖥️ Windows Integration

### Add to Startup Folder:
1. Press `Win + R`, type `shell:startup`
2. Copy `start_widgets.bat` to the startup folder
3. Widgets will launch automatically when Windows starts

### Create Desktop Shortcut:
1. Right-click desktop → New → Shortcut
2. Browse to `start_widgets.bat`
3. Name it "Desktop Widgets"

## 🎛️ Widget Controls

Once launched, all widgets support:
- **Ctrl+Drag**: Move widget
- **Double-click**: Toggle move mode 
- **ESC**: Exit move mode
- **Hover**: Show controls
- **Automatic position saving**

## 📁 Files

- `startup.py` - Main startup manager
- `startup_config.json` - Widget configuration
- `start_widgets.bat` - Windows batch launcher
- `start_widgets.ps1` - PowerShell launcher
- `ui/web.py` - Widget implementations

## 🔄 Updates & Maintenance

### Reset Configuration:
```bash
python startup.py reset
```

### Backup Configuration:
Copy `startup_config.json` to a safe location

### Add New Widgets:
1. Edit `startup.py` and add to `widget_map`
2. Update configuration file with new widget type
3. Restart with `python startup.py`
