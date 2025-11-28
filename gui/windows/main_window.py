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

import json
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QLabel,
    QVBoxLayout,
    QStatusBar,
    QSystemTrayIcon,
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
            '• "I just got promoted to Senior Engineer at Company X"\n'
            '• "Update my skills to include React and TypeScript"\n'
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
                response_data = reply.readAll().data().decode("utf-8")
                data = json.loads(response_data)

                if data.get("status") == "healthy":
                    version = data.get("version", "unknown")
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
        # Save window state before hiding/closing
        self._save_window_state()

        # Check if system tray icon exists
        if hasattr(self, "tray_icon") and self.tray_icon is not None:
            # Minimize to tray
            event.ignore()
            self.hide()
            print("[AutoResumeFiller GUI] Window minimized to tray")

            # Optional: Show tray notification on first minimize
            if not hasattr(self, "_first_minimize_shown"):
                self.tray_icon.showMessage(
                    "AutoResumeFiller",
                    "Application minimized to system tray. Double-click icon to restore.",
                    QSystemTrayIcon.Information,
                    3000,  # 3 seconds
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
