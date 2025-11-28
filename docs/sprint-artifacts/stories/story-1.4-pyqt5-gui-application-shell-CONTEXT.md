# Story 1.4 Technical Context: PyQt5 GUI Application Shell

**Generated:** 2025-11-28  
**Story:** 1.4 - PyQt5 GUI Application Shell  
**For:** DEV Agent Implementation  
**Estimated Implementation Time:** 6-8 hours

---

## Overview

This document provides complete implementation guidance for Story 1.4: building a PyQt5 desktop GUI application with tabbed interface, system tray integration, and backend health check. This context includes:

1. **Complete code templates** for all files (gui/main.py, gui/windows/main_window.py, gui/requirements.txt)
2. **PyQt5 architecture patterns** (QApplication lifecycle, signal/slot connections, QSettings persistence)
3. **System tray integration** (QSystemTrayIcon, minimize-to-tray behavior, platform considerations)
4. **Backend communication** (QNetworkAccessManager async HTTP, error handling)
5. **Verification checklist** (testing steps, expected outputs, troubleshooting)

---

## Architecture Context

### Component Structure

```
gui/
├── main.py                     # QApplication entry point, system tray setup
├── windows/
│   ├── __init__.py
│   └── main_window.py          # MainWindow(QMainWindow) with tabbed interface
├── resources/
│   └── icons/
│       └── app_icon.png        # Placeholder 64x64 application icon
├── tests/
│   ├── __init__.py
│   └── test_main_window.py     # PyQt5 widget tests (future)
└── requirements.txt            # PyQt5==5.15.10, requests==2.31.0

Integration Points:
- Backend API: http://localhost:8765/api/status (GET request on startup)
- Extension: Future - "Open Dashboard" button will launch GUI (Story 1.5 or Epic 5)
- Data Layer: Future - Epic 2 (user data display in "My Data" tab)
```

### PyQt5 Architecture Patterns

**QApplication Lifecycle:**
```python
import sys
from PyQt5.QtWidgets import QApplication

# 1. Create QApplication instance (MUST be first PyQt5 call)
app = QApplication(sys.argv)

# 2. Set application metadata (affects QSettings storage location)
app.setOrganizationName("AutoResumeFiller")
app.setApplicationName("AutoResumeFiller Dashboard")

# 3. Create main window and show
window = MainWindow()
window.show()

# 4. Start event loop (blocking call until app.quit())
sys.exit(app.exec_())
```

**Signal/Slot Pattern (Event Handling):**
```python
from PyQt5.QtCore import pyqtSignal, QObject

class BackendChecker(QObject):
    # Define custom signal
    health_check_complete = pyqtSignal(bool, str)  # (is_healthy, message)
    
    def check_backend(self):
        # ... perform HTTP request ...
        self.health_check_complete.emit(True, "Connected")  # Emit signal

# Connect signal to slot (method)
checker = BackendChecker()
checker.health_check_complete.connect(main_window.update_status_bar)
```

**QSettings for Persistence:**
```python
from PyQt5.QtCore import QSettings

settings = QSettings()  # Uses org/app name from QApplication

# Save window geometry
settings.setValue("geometry", self.saveGeometry())
settings.setValue("windowState", self.saveState())
settings.setValue("lastTab", self.tab_widget.currentIndex())

# Restore on next launch
self.restoreGeometry(settings.value("geometry", b""))
self.restoreState(settings.value("windowState", b""))
self.tab_widget.setCurrentIndex(settings.value("lastTab", 0, type=int))
```

---

## File 1: gui/requirements.txt

**Purpose:** Python dependencies for PyQt5 GUI application

**Complete File Content:**
```txt
# PyQt5 GUI Framework
PyQt5==5.15.10
PyQt5-Qt5==5.15.2
PyQt5-sip==12.13.0

# HTTP Client (simpler alternative to QNetworkAccessManager)
requests==2.31.0

# Optional: PyQt5 Designer tools (for future UI design)
# pyqt5-tools==5.15.10.1.3
```

**Installation Instructions:**
```bash
# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install GUI dependencies
pip install -r gui/requirements.txt

# Verify PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 installed successfully')"
```

**Key Dependencies:**
- **PyQt5 5.15.10:** Latest stable release before Qt6 migration
- **requests 2.31.0:** Simple HTTP client (alternative to QNetworkAccessManager for MVP)

---

## File 2: gui/main.py

**Purpose:** QApplication entry point with system tray integration

**Complete File Content:**
```python
"""AutoResumeFiller GUI - Application Entry Point

This module initializes the PyQt5 application, creates the system tray icon,
and manages the MainWindow lifecycle. Closing the window minimizes to tray
instead of exiting the application.

Usage:
    python gui/main.py
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

# Add gui/ to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows.main_window import MainWindow


def create_placeholder_icon():
    """Create a placeholder application icon (64x64 blue square with 'ARF').
    
    Returns:
        QIcon: Icon for application window and system tray
    """
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#007bff"))  # Blue background
    
    painter = QPainter(pixmap)
    painter.setPen(QColor("#ffffff"))  # White text
    font = painter.font()
    font.setPixelSize(20)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "ARF")
    painter.end()
    
    return QIcon(pixmap)


def setup_system_tray(app, main_window):
    """Set up system tray icon with context menu.
    
    Args:
        app: QApplication instance
        main_window: MainWindow instance
        
    Returns:
        QSystemTrayIcon: System tray icon object
    """
    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("[AutoResumeFiller GUI] Warning: System tray not available on this platform")
        return None
    
    # Create system tray icon
    tray_icon = QSystemTrayIcon(create_placeholder_icon(), app)
    tray_icon.setToolTip("AutoResumeFiller")
    
    # Create tray menu
    tray_menu = QMenu()
    
    # "Show Dashboard" action
    show_action = QAction("Show Dashboard", app)
    show_action.triggered.connect(main_window.show_and_restore)
    tray_menu.addAction(show_action)
    
    tray_menu.addSeparator()
    
    # "Exit Application" action
    exit_action = QAction("Exit Application", app)
    exit_action.triggered.connect(app.quit)
    tray_menu.addAction(exit_action)
    
    tray_icon.setContextMenu(tray_menu)
    
    # Double-click to show window
    tray_icon.activated.connect(
        lambda reason: main_window.show_and_restore() 
        if reason == QSystemTrayIcon.DoubleClick 
        else None
    )
    
    # Show tray icon
    tray_icon.show()
    
    print("[AutoResumeFiller GUI] System tray icon created")
    return tray_icon


def main():
    """Main application entry point."""
    print("[AutoResumeFiller GUI] Starting application...")
    
    # Create QApplication instance (must be first PyQt5 call)
    app = QApplication(sys.argv)
    
    # Set application metadata (used by QSettings)
    app.setOrganizationName("AutoResumeFiller")
    app.setApplicationName("AutoResumeFiller Dashboard")
    app.setApplicationVersion("1.0.0")
    
    # Set application icon
    app.setWindowIcon(create_placeholder_icon())
    
    # Create main window
    main_window = MainWindow()
    
    # Set up system tray (minimize-to-tray support)
    tray_icon = setup_system_tray(app, main_window)
    
    # Store tray icon reference in main window (prevent garbage collection)
    main_window.tray_icon = tray_icon
    
    # Show main window
    main_window.show()
    
    print("[AutoResumeFiller GUI] Application launched successfully")
    print("[AutoResumeFiller GUI] Window visible, system tray icon active")
    
    # Start Qt event loop (blocking until app.quit())
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
```

**Key Implementation Details:**

1. **Placeholder Icon Generation:**
   - Uses QPainter to draw 64x64 blue square with white "ARF" text
   - Same style as extension icons (consistency)
   - Future: Replace with professional icon in Epic 7

2. **System Tray Setup:**
   - Checks `QSystemTrayIcon.isSystemTrayAvailable()` (platform compatibility)
   - Context menu with "Show Dashboard" and "Exit Application"
   - Double-click activates `show_and_restore()` method in MainWindow
   - Right-click shows context menu

3. **Application Metadata:**
   - Organization: "AutoResumeFiller"
   - Application: "AutoResumeFiller Dashboard"
   - Version: "1.0.0"
   - Used by QSettings for registry/config storage location

---

## File 3: gui/windows/__init__.py

**Purpose:** Python package marker for windows module

**Complete File Content:**
```python
"""AutoResumeFiller GUI - Windows Module

Contains QMainWindow and dialog classes for the desktop application.
"""

__all__ = ['MainWindow']

from .main_window import MainWindow
```

---

## File 4: gui/windows/main_window.py

**Purpose:** QMainWindow with tabbed interface and backend health check

**Complete File Content:**
```python
"""AutoResumeFiller GUI - Main Window

This module defines the MainWindow class - the primary desktop application window
with tabbed interface (Monitor, My Data, Settings, Chatbot), status bar for
backend connection indicator, and window geometry persistence via QSettings.

Features:
- 4-tab interface with placeholder content (Epic 6 will implement actual functionality)
- Backend health check on startup (GET /api/status)
- Minimize-to-tray behavior (closeEvent override)
- Window geometry persistence (size, position, selected tab)
"""
import sys
import json
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout,
    QStatusBar, QMessageBox
)
from PyQt5.QtCore import QSettings, QTimer, QUrl, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtGui import QFont


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        """Initialize MainWindow with tabs, status bar, and backend health check."""
        super().__init__()
        
        # Initialize network manager for backend communication
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_network_response)
        
        # Initialize UI components
        self._init_ui()
        
        # Restore window geometry from previous session
        self._restore_window_state()
        
        # Start backend health check (delayed 500ms after window shown)
        QTimer.singleShot(500, self.check_backend_health)
        
        print("[AutoResumeFiller GUI] MainWindow initialized")
    
    def _init_ui(self):
        """Initialize UI components (tabs, status bar, layout)."""
        # Set window properties
        self.setWindowTitle("AutoResumeFiller Dashboard")
        self.setMinimumSize(600, 400)  # Minimum size
        self.resize(800, 600)  # Default size
        
        # Create central widget with tab interface
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create 4 placeholder tabs
        self._create_monitor_tab()
        self._create_data_tab()
        self._create_settings_tab()
        self._create_chatbot_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Backend: Checking...")
        self.status_bar.addPermanentWidget(self.status_label)
        
        print("[AutoResumeFiller GUI] UI components initialized")
    
    def _create_monitor_tab(self):
        """Create Monitor tab with placeholder content."""
        monitor_widget = QWidget()
        layout = QVBoxLayout()
        
        # Placeholder label
        label = QLabel(
            "📊 Real-time form-filling activity will appear here.\n\n"
            "This tab will display:\n"
            "• Detected job application pages\n"
            "• Form fields identified and auto-filled\n"
            "• AI-generated responses\n"
            "• Submission confirmations\n\n"
            "(Epic 6 - Story 6.1: Real-Time Event Feed)"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #6c757d; padding: 40px;")
        
        layout.addWidget(label)
        monitor_widget.setLayout(layout)
        
        self.tab_widget.addTab(monitor_widget, "Monitor")
    
    def _create_data_tab(self):
        """Create My Data tab with placeholder content."""
        data_widget = QWidget()
        layout = QVBoxLayout()
        
        # Placeholder label
        label = QLabel(
            "📝 View and edit your personal information here.\n\n"
            "This tab will display:\n"
            "• Personal profile (name, email, phone, location)\n"
            "• Work experience history\n"
            "• Education and certifications\n"
            "• Skills and technologies\n"
            "• Resume/cover letter upload and management\n\n"
            "(Epic 6 - Story 6.3: Data Management Tab)"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #6c757d; padding: 40px;")
        
        layout.addWidget(label)
        data_widget.setLayout(layout)
        
        self.tab_widget.addTab(data_widget, "My Data")
    
    def _create_settings_tab(self):
        """Create Settings tab with placeholder content."""
        settings_widget = QWidget()
        layout = QVBoxLayout()
        
        # Placeholder label
        label = QLabel(
            "⚙️ Configure AutoResumeFiller settings here.\n\n"
            "This tab will include:\n"
            "• AI provider selection (OpenAI, Anthropic, Google Gemini)\n"
            "• API key management\n"
            "• Auto-fill behavior preferences\n"
            "• Extension settings\n"
            "• Data backup/export options\n\n"
            "(Epic 6 - Story 6.4: Configuration Tab)"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #6c757d; padding: 40px;")
        
        layout.addWidget(label)
        settings_widget.setLayout(layout)
        
        self.tab_widget.addTab(settings_widget, "Settings")
    
    def _create_chatbot_tab(self):
        """Create Chatbot tab with placeholder content."""
        chatbot_widget = QWidget()
        layout = QVBoxLayout()
        
        # Placeholder label
        label = QLabel(
            "💬 Chat with AI to update your data conversationally.\n\n"
            "This tab will feature:\n"
            "• Natural language interface for data updates\n"
            "• \"I just got promoted to Senior Engineer at Company X\"\n"
            "• \"Update my skills to include React and TypeScript\"\n"
            "• Conversational history and suggestions\n\n"
            "(Epic 6 - Story 6.5: Chatbot Tab)"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #6c757d; padding: 40px;")
        
        layout.addWidget(label)
        chatbot_widget.setLayout(layout)
        
        self.tab_widget.addTab(chatbot_widget, "Chatbot")
    
    def check_backend_health(self):
        """Check backend health by sending GET request to /api/status.
        
        This method is called on startup (500ms delay) and uses QNetworkAccessManager
        for async HTTP. Response is handled in _handle_network_response().
        """
        print("[AutoResumeFiller GUI] Checking backend health...")
        self.status_label.setText("Backend: Checking...")
        self.status_label.setStyleSheet("color: #856404;")  # Yellow
        
        # Create GET request to backend health check endpoint
        url = QUrl("http://localhost:8765/api/status")
        request = QNetworkRequest(url)
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        
        # Send async GET request (response handled by signal/slot)
        self.network_manager.get(request)
        
        # Set timeout (5 seconds)
        QTimer.singleShot(5000, self._handle_health_check_timeout)
    
    def _handle_network_response(self, reply):
        """Handle network response from backend health check.
        
        Args:
            reply: QNetworkReply object with response data
        """
        if reply.error() == QNetworkReply.NoError:
            # Success - parse JSON response
            try:
                response_data = reply.readAll().data().decode('utf-8')
                data = json.loads(response_data)
                
                if data.get('status') == 'healthy':
                    version = data.get('version', 'unknown')
                    print(f"[AutoResumeFiller GUI] Backend connected (version {version})")
                    self.status_label.setText(f"Backend: Connected ✅ (v{version})")
                    self.status_label.setStyleSheet("color: #155724;")  # Green
                else:
                    print(f"[AutoResumeFiller GUI] Backend unhealthy: {data.get('status')}")
                    self.status_label.setText("Backend: Unhealthy ⚠️")
                    self.status_label.setStyleSheet("color: #856404;")  # Yellow
            
            except json.JSONDecodeError as e:
                print(f"[AutoResumeFiller GUI] Invalid JSON response: {e}")
                self.status_label.setText("Backend: Invalid Response ❌")
                self.status_label.setStyleSheet("color: #721c24;")  # Red
        
        else:
            # Error - connection failed
            error_string = reply.errorString()
            print(f"[AutoResumeFiller GUI] Backend health check failed: {error_string}")
            self.status_label.setText("Backend: Disconnected ❌")
            self.status_label.setStyleSheet("color: #721c24;")  # Red
        
        reply.deleteLater()  # Clean up reply object
    
    def _handle_health_check_timeout(self):
        """Handle timeout if backend doesn't respond within 5 seconds."""
        if self.status_label.text() == "Backend: Checking...":
            print("[AutoResumeFiller GUI] Backend health check timeout")
            self.status_label.setText("Backend: Timeout ❌")
            self.status_label.setStyleSheet("color: #721c24;")  # Red
    
    def show_and_restore(self):
        """Show and restore window from system tray.
        
        This method is called when user double-clicks tray icon or selects
        "Show Dashboard" from tray menu.
        """
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()
        print("[AutoResumeFiller GUI] Window restored from tray")
    
    def closeEvent(self, event):
        """Override close event to minimize to tray instead of exiting.
        
        Args:
            event: QCloseEvent object
        """
        # Check if system tray icon exists
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            # Minimize to tray
            event.ignore()
            self.hide()
            print("[AutoResumeFiller GUI] Window minimized to tray")
            
            # Optional: Show tray notification on first minimize
            if not hasattr(self, '_first_minimize_shown'):
                self.tray_icon.showMessage(
                    "AutoResumeFiller",
                    "Application minimized to system tray. Double-click icon to restore.",
                    QSystemTrayIcon.Information,
                    3000  # 3 seconds
                )
                self._first_minimize_shown = True
        else:
            # No tray icon - allow normal close
            event.accept()
            print("[AutoResumeFiller GUI] Window closed (no tray icon)")
    
    def _restore_window_state(self):
        """Restore window geometry and selected tab from previous session."""
        settings = QSettings()
        
        # Restore window geometry (size and position)
        geometry = settings.value("geometry", None)
        if geometry is not None:
            self.restoreGeometry(geometry)
            print("[AutoResumeFiller GUI] Window geometry restored")
        
        # Restore window state (maximized, etc.)
        window_state = settings.value("windowState", None)
        if window_state is not None:
            self.restoreState(window_state)
        
        # Restore last selected tab
        last_tab = settings.value("lastTab", 0, type=int)
        if 0 <= last_tab < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(last_tab)
            print(f"[AutoResumeFiller GUI] Restored to tab {last_tab}")
    
    def _save_window_state(self):
        """Save window geometry and selected tab for next session."""
        settings = QSettings()
        
        # Save window geometry
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Save selected tab
        settings.setValue("lastTab", self.tab_widget.currentIndex())
        
        print("[AutoResumeFiller GUI] Window state saved")
    
    def __del__(self):
        """Destructor - save window state before object destruction."""
        try:
            self._save_window_state()
        except:
            pass  # Ignore errors during cleanup
```

**Key Implementation Details:**

1. **Async Backend Communication:**
   - Uses `QNetworkAccessManager` for non-blocking HTTP
   - Signal/slot pattern: `finished` signal → `_handle_network_response()` slot
   - 5-second timeout via `QTimer.singleShot()`

2. **Status Bar Styling:**
   - Checking: Yellow text (#856404)
   - Connected: Green text (#155724) with ✅
   - Disconnected: Red text (#721c24) with ❌

3. **Minimize-to-Tray:**
   - Overrides `closeEvent()` to call `event.ignore()` and `self.hide()`
   - Shows tray notification on first minimize (user education)
   - Only works if `self.tray_icon` exists (set in main.py)

4. **Window Geometry Persistence:**
   - `QSettings()` uses org/app name from QApplication metadata
   - Saves: geometry (size, position), window state (maximized), last tab index
   - Restores on `__init__()`, saves on `__del__()`

---

## System Tray Integration Deep Dive

### Platform-Specific Behavior

**Windows:**
- System tray icon appears in taskbar notification area (bottom-right)
- Right-click shows context menu
- Double-click shows/restores window
- Icon persists when window closed

**Linux (GNOME/KDE):**
- System tray icon appears in top panel (GNOME) or bottom panel (KDE)
- Behavior identical to Windows
- Some desktop environments (GNOME 3.26+) removed legacy tray support - use TopIcons extension

**macOS:**
- System tray appears as menu bar icon (top-right)
- Right-click shows context menu
- No double-click support (menu bar standard is single-click)

### QSystemTrayIcon API

```python
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction

# Check availability
if not QSystemTrayIcon.isSystemTrayAvailable():
    print("System tray not supported")

# Create icon
tray = QSystemTrayIcon(QIcon("icon.png"))
tray.setToolTip("Hover text")

# Context menu
menu = QMenu()
action = QAction("Menu Item", app)
action.triggered.connect(callback_function)
menu.addAction(action)
tray.setContextMenu(menu)

# Activation signal (click events)
tray.activated.connect(lambda reason: 
    callback() if reason == QSystemTrayIcon.DoubleClick else None
)

# Show icon
tray.show()

# Show balloon notification
tray.showMessage("Title", "Message", QSystemTrayIcon.Information, 3000)
```

---

## Backend Communication Patterns

### Option 1: QNetworkAccessManager (Async, PyQt5-Native)

**Pros:**
- Non-blocking GUI (runs in Qt event loop)
- No threading complexity
- Integrated with Qt signals/slots

**Cons:**
- More verbose API than requests
- Requires understanding of QNetworkReply lifecycle

**Implementation:**
```python
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import QUrl

class MainWindow(QMainWindow):
    def __init__(self):
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_response)
    
    def make_request(self):
        url = QUrl("http://localhost:8765/api/status")
        request = QNetworkRequest(url)
        self.network_manager.get(request)  # Async - returns immediately
    
    def handle_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data().decode('utf-8')
            print(f"Response: {data}")
        else:
            print(f"Error: {reply.errorString()}")
        reply.deleteLater()  # Clean up
```

### Option 2: requests + QThread (Simpler, Requires Threading)

**Pros:**
- Simple requests API (familiar to Python developers)
- Less boilerplate code

**Cons:**
- Requires QThread for async execution
- More complex thread management

**Implementation:**
```python
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class BackendChecker(QThread):
    result_ready = pyqtSignal(bool, str)  # (success, message)
    
    def run(self):
        try:
            response = requests.get("http://localhost:8765/api/status", timeout=5)
            data = response.json()
            if data.get('status') == 'healthy':
                self.result_ready.emit(True, f"Connected (v{data.get('version')})")
            else:
                self.result_ready.emit(False, "Unhealthy")
        except requests.exceptions.RequestException as e:
            self.result_ready.emit(False, str(e))

# Usage in MainWindow
self.checker = BackendChecker()
self.checker.result_ready.connect(self.update_status_bar)
self.checker.start()  # Run in background thread
```

**Recommendation:** Use QNetworkAccessManager for Story 1.4 (learning opportunity, PyQt5-native). Consider requests + QThread for future complex HTTP operations in Epic 3 (AI API calls).

---

## Verification Checklist

### Installation Verification

1. **Install Dependencies:**
   ```bash
   cd C:\Users\basha\Desktop\root\AutoResumeFiller
   pip install -r gui/requirements.txt
   ```
   
   **Expected Output:**
   ```
   Successfully installed PyQt5-5.15.10 PyQt5-Qt5-5.15.2 PyQt5-sip-12.13.0 requests-2.31.0
   ```

2. **Verify PyQt5 Installation:**
   ```bash
   python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
   ```
   
   **Expected Output:**
   ```
   PyQt5 OK
   ```

### Functional Verification

3. **Start Backend (Terminal 1):**
   ```bash
   cd C:\Users\basha\Desktop\root\AutoResumeFiller
   uvicorn backend.main:app --host 127.0.0.1 --port 8765
   ```
   
   **Expected Output:**
   ```
   INFO: Uvicorn running on http://127.0.0.1:8765
   ```

4. **Launch GUI (Terminal 2):**
   ```bash
   cd C:\Users\basha\Desktop\root\AutoResumeFiller
   python gui/main.py
   ```
   
   **Expected Output (Console):**
   ```
   [AutoResumeFiller GUI] Starting application...
   [AutoResumeFiller GUI] MainWindow initialized
   [AutoResumeFiller GUI] UI components initialized
   [AutoResumeFiller GUI] System tray icon created
   [AutoResumeFiller GUI] Application launched successfully
   [AutoResumeFiller GUI] Window visible, system tray icon active
   [AutoResumeFiller GUI] Window geometry restored
   [AutoResumeFiller GUI] Restored to tab 0
   [AutoResumeFiller GUI] Checking backend health...
   [AutoResumeFiller GUI] Backend connected (version 1.0.0)
   ```
   
   **Expected GUI:**
   - Window opens within 5 seconds
   - Title: "AutoResumeFiller Dashboard"
   - 4 tabs: Monitor, My Data, Settings, Chatbot
   - Status bar: "Backend: Connected ✅ (v1.0.0)" in green
   - System tray icon visible (Windows taskbar notification area)

5. **Test Tab Switching:**
   - Click "My Data" tab → content switches to data placeholder
   - Click "Settings" tab → content switches to settings placeholder
   - Click "Chatbot" tab → content switches to chatbot placeholder
   - Click "Monitor" tab → returns to monitor placeholder

6. **Test Minimize to Tray:**
   - Click window close button (X)
   - Window disappears (not closed)
   - Application still running (Terminal 2 still active)
   - System tray icon still visible
   - **Tray notification appears:** "Application minimized to system tray. Double-click icon to restore."

7. **Test Restore from Tray:**
   - Double-click system tray icon
   - Window reappears in previous position
   - Selected tab preserved (if "Settings" was open, it's still open)
   - Console output: `[AutoResumeFiller GUI] Window restored from tray`

8. **Test Backend Disconnection:**
   - Stop backend (Terminal 1: Ctrl+C)
   - Close GUI window (minimize to tray)
   - Double-click tray icon to restore
   - Wait 5 seconds
   - Status bar updates: "Backend: Disconnected ❌" in red

9. **Test Window Geometry Persistence:**
   - Resize window to 1000x700
   - Move window to different screen position
   - Select "Settings" tab
   - Right-click tray icon → "Exit Application"
   - Restart GUI: `python gui/main.py`
   - Window opens at 1000x700 in same position
   - "Settings" tab is selected

10. **Test Exit Application:**
    - Right-click system tray icon
    - Select "Exit Application"
    - Application exits completely
    - Window closes
    - Tray icon disappears
    - Terminal 2 shows exit message

### Expected Test Results

| Test | Pass Criteria | Fail Indicator |
|------|--------------|----------------|
| Installation | No pip errors, PyQt5 imports successfully | ImportError, missing dependencies |
| GUI Launch | Window opens <5 seconds, no exceptions | Timeout, traceback in console |
| Tab Switching | Content changes, no errors | Tabs unresponsive, crash |
| Backend Health Check | Status bar shows "Connected ✅" in <2 seconds | "Disconnected ❌" when backend running |
| Minimize to Tray | Window hides, tray icon visible | Application exits, no tray icon |
| Restore from Tray | Window reappears on double-click | No response, tray icon unresponsive |
| Geometry Persistence | Size/position/tab restored on relaunch | Window resets to default |
| Exit Application | Process exits, tray icon disappears | Application hangs, tray icon persists |

---

## Troubleshooting Guide

### Issue 1: PyQt5 Installation Fails

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement PyQt5==5.15.10
```

**Cause:** Python version incompatibility (PyQt5 5.15.10 requires Python 3.7-3.11)

**Solution:**
```bash
# Check Python version
python --version
# Should be 3.9+ but <3.12

# If Python 3.12+, downgrade PyQt5 version
pip install PyQt5==5.15.9
```

### Issue 2: System Tray Icon Not Appearing

**Symptom:** GUI launches, but no tray icon visible

**Cause:** Platform doesn't support system tray (some Linux desktop environments)

**Solution:**
- **Windows:** Should always work - check taskbar notification area settings
- **Linux GNOME 3.26+:** Install TopIcons GNOME extension
- **macOS:** Look for menu bar icon (top-right) instead of dock
- **Workaround:** Application still functional without tray icon (close button will exit instead of minimizing)

### Issue 3: Backend Health Check Shows "Disconnected ❌"

**Symptom:** Status bar shows red "Disconnected ❌" when backend is running

**Cause:** Backend not running on localhost:8765, or CORS blocking request

**Solution:**
```bash
# Verify backend is running
curl http://localhost:8765/api/status
# Should return: {"status":"healthy","version":"1.0.0"}

# Check backend CORS configuration
# In backend/config/settings.py:
# CORS_ORIGINS: List[str] = ["chrome-extension://*"]
# GUI uses localhost, which is automatically allowed (same-origin)

# If still failing, check firewall settings
# Windows: Allow Python through Windows Defender Firewall
```

### Issue 4: GUI Freezes During Backend Check

**Symptom:** Window becomes unresponsive for 5 seconds during health check

**Cause:** Using synchronous `requests.get()` instead of async QNetworkAccessManager

**Solution:** Verify `gui/windows/main_window.py` uses `QNetworkAccessManager` (provided template is async)

### Issue 5: Window Geometry Not Restored

**Symptom:** Window resets to 800x600 on every launch

**Cause:** QSettings not saving properly, or `__del__()` not called

**Solution:**
```python
# Add explicit save in closeEvent() instead of __del__()
def closeEvent(self, event):
    self._save_window_state()  # Add this line
    if hasattr(self, 'tray_icon') and self.tray_icon is not None:
        event.ignore()
        self.hide()
    else:
        event.accept()
```

### Issue 6: ImportError: No module named 'windows'

**Symptom:**
```
ImportError: No module named 'windows'
```

**Cause:** Missing `gui/windows/__init__.py` file

**Solution:**
```bash
# Create __init__.py file
touch gui/windows/__init__.py

# Or create with content (provided in File 3 above)
```

### Issue 7: Multiple GUI Instances Running

**Symptom:** Clicking tray icon opens new window instead of restoring existing

**Cause:** Application doesn't enforce single-instance constraint

**Solution (Future Enhancement):**
```python
# Add to gui/main.py (optional for Story 1.4)
from PyQt5.QtNetwork import QLocalServer, QLocalSocket

class SingleInstance:
    def __init__(self, key):
        self.key = key
        self.socket = QLocalSocket()
        self.socket.connectToServer(key)
        
        if self.socket.waitForConnected(500):
            self.is_running = True
        else:
            self.is_running = False
            self.server = QLocalServer()
            self.server.listen(key)

# Usage in main()
instance = SingleInstance("AutoResumeFiller")
if instance.is_running:
    print("Application already running!")
    sys.exit(0)
```

---

## Testing Instructions for DEV Agent

### Unit Tests (Future - Epic 1 Story 1.6)

```python
# gui/tests/test_main_window.py
import pytest
from PyQt5.QtWidgets import QApplication
from gui.windows.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    """Fixture to create QApplication."""
    return QApplication([])

def test_main_window_creation(qtbot):
    """Test MainWindow initializes without errors."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "AutoResumeFiller Dashboard"
    assert window.tab_widget.count() == 4

def test_tab_labels(qtbot):
    """Test tab labels are correct."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.tab_widget.tabText(0) == "Monitor"
    assert window.tab_widget.tabText(1) == "My Data"
    assert window.tab_widget.tabText(2) == "Settings"
    assert window.tab_widget.tabText(3) == "Chatbot"
```

### Manual Testing Script

```python
# scripts/test_gui_launch.py
"""Quick test script to verify GUI launches successfully."""
import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

sys.path.insert(0, 'gui')
from windows.main_window import MainWindow

def test_launch():
    """Test GUI launch and auto-close after 3 seconds."""
    print("[TEST] Creating QApplication...")
    app = QApplication(sys.argv)
    
    print("[TEST] Creating MainWindow...")
    window = MainWindow()
    window.show()
    
    print("[TEST] Window visible, waiting 3 seconds...")
    QTimer.singleShot(3000, app.quit)
    
    print("[TEST] Starting event loop...")
    app.exec_()
    
    print("[TEST] GUI test complete - no errors!")

if __name__ == "__main__":
    test_launch()
```

Run test:
```bash
python scripts/test_gui_launch.py
```

---

## Implementation Checklist for DEV Agent

### Pre-Implementation
- [ ] Verify Python 3.9+ installed: `python --version`
- [ ] Verify backend running: `curl http://localhost:8765/api/status`
- [ ] Review PyQt5 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/

### File Creation (in order)
1. [ ] Create `gui/requirements.txt` (copy from File 1 above)
2. [ ] Install dependencies: `pip install -r gui/requirements.txt`
3. [ ] Verify PyQt5: `python -c "from PyQt5.QtWidgets import QApplication; print('OK')"`
4. [ ] Create `gui/windows/__init__.py` (copy from File 3 above)
5. [ ] Create `gui/windows/main_window.py` (copy from File 4 above)
6. [ ] Create `gui/main.py` (copy from File 2 above)

### Testing (in order)
7. [ ] Test launch: `python gui/main.py`
8. [ ] Verify window opens <5 seconds
9. [ ] Verify 4 tabs present with placeholder text
10. [ ] Verify status bar shows "Backend: Connected ✅" (green) if backend running
11. [ ] Test tab switching (click each tab, verify content changes)
12. [ ] Test minimize to tray (click X, verify window hides, tray icon visible)
13. [ ] Test restore from tray (double-click icon, verify window reappears)
14. [ ] Test tray menu (right-click icon, verify "Show Dashboard" and "Exit Application")
15. [ ] Test exit application (right-click icon → Exit, verify process exits)
16. [ ] Test backend disconnection (stop backend, verify status bar shows "Disconnected ❌" in red)
17. [ ] Test window geometry persistence (resize, move, switch tab, restart GUI, verify restored)

### Documentation
18. [ ] Update README.md with GUI launch instructions
19. [ ] Add screenshots of GUI to docs/ (window, tabs, system tray)
20. [ ] Document keyboard shortcuts (if any)

### Git Commit
21. [ ] Stage files: `git add gui/`
22. [ ] Commit: `git commit -m "Story 1.4: Implement PyQt5 GUI Application Shell"`
23. [ ] Verify all tests pass before pushing

---

## Summary

This technical context provides complete implementation guidance for Story 1.4:

✅ **3 Python files:** gui/main.py (144 lines), gui/windows/main_window.py (293 lines), gui/windows/__init__.py (8 lines)  
✅ **1 requirements file:** gui/requirements.txt (4 dependencies)  
✅ **8 Acceptance Criteria:** All testable with provided verification checklist  
✅ **System Tray Integration:** Platform-specific behavior documented  
✅ **Backend Communication:** Async QNetworkAccessManager with error handling  
✅ **Window Persistence:** QSettings for geometry/state restoration  
✅ **Troubleshooting Guide:** 7 common issues with solutions  
✅ **Testing Instructions:** Manual verification + future unit test examples

**Estimated Implementation Time:** 6-8 hours (reduced with complete templates)

**Next Step:** Run `*dev-story` to implement GUI application using these templates.
