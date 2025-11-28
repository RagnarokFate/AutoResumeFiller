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
        lambda reason: (
            main_window.show_and_restore() if reason == QSystemTrayIcon.DoubleClick else None
        )
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
