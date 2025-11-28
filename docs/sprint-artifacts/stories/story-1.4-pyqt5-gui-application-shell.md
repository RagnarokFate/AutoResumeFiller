# Story 1.4: PyQt5 GUI Application Shell

**Epic:** Epic 1 - Foundation & Core Infrastructure  
**Story ID:** 1.4  
**Title:** PyQt5 GUI Application Shell  
**Status:** Drafted  
**Created:** 2025-11-28  
**Story Points:** 5  
**Priority:** High  
**Assigned To:** DEV Agent  

---

## Story Description

### User Story

**As a** developer building AutoResumeFiller  
**I want** a PyQt5 desktop GUI application with tabbed interface and system tray integration  
**So that** users can monitor form-filling activity in real-time, manage their data, configure settings, and interact with the chatbot for conversational updates

### Context

Story 1.3 delivered the Chrome Extension with popup interface and backend communication. Story 1.4 builds the desktop GUI dashboard that serves as the central control panel for AutoResumeFiller.

The GUI provides a professional desktop application experience with:

1. **Main Window (QMainWindow)** - Tabbed interface with 4 tabs: Monitor, My Data, Settings, Chatbot
2. **System Tray Integration** - Minimize-to-tray behavior (closing window doesn't exit, icon stays in system tray)
3. **Backend Health Check** - On startup, ping `http://localhost:8765/api/status` and display connection status
4. **Placeholder Tabs** - Each tab shows a simple QLabel with descriptive text (actual implementation in Epic 6)

The GUI communicates with the backend via HTTP REST API using PyQt5's `QNetworkAccessManager` for async requests. While this story doesn't implement the actual tab functionality (form monitoring, data management, etc.), it creates the GUI shell that all future features will build upon.

Key integration point: Extension's "Open Dashboard" button (currently a placeholder alert) will eventually launch this GUI via native messaging or system command.

### Dependencies

- ✅ **Story 1.1:** Project Initialization & Repository Setup (COMPLETED)
  - Requires `gui/` directory structure
  - Requires `.gitignore` to exclude PyQt5 compiled resources

- ✅ **Story 1.2:** Python Backend Scaffolding (COMPLETED)
  - Backend must be running on `localhost:8765`
  - Health check endpoint (`GET /api/status`) must be operational

- 📦 **External Dependencies:**
  - Python 3.9+ with pip
  - PyQt5 library (pip install PyQt5)
  - QNetworkAccessManager for HTTP communication

### Technical Approach

**Implementation Strategy:**

1. **Create `gui/requirements.txt`** with PyQt5 dependencies:
   ```
   PyQt5==5.15.10
   requests==2.31.0  # For simpler HTTP calls (alternative to QNetworkAccessManager)
   ```

2. **Implement `gui/main.py`** (QApplication entry point):
   - Initialize QApplication
   - Set application name, organization, icon (placeholder)
   - Create MainWindow instance
   - Create system tray icon with QSystemTrayIcon
   - Configure tray icon menu (Show/Hide, Exit)
   - Set window close event to minimize to tray instead of exiting
   - Start Qt event loop with `app.exec_()`

3. **Implement `gui/windows/main_window.py`** (QMainWindow class):
   - Create QMainWindow subclass with 800x600 default size
   - Set window title: "AutoResumeFiller Dashboard"
   - Create QTabWidget with 4 tabs:
     * **Monitor Tab:** QLabel("Real-time form-filling activity will appear here. (Epic 6 - Story 6.1)")
     * **My Data Tab:** QLabel("View and edit your personal information here. (Epic 6 - Story 6.3)")
     * **Settings Tab:** QLabel("Configure AutoResumeFiller settings here. (Epic 6 - Story 6.4)")
     * **Chatbot Tab:** QLabel("Chat with AI to update your data conversationally. (Epic 6 - Story 6.5)")
   - Add status bar with backend connection indicator
   - Implement `checkBackendHealth()` method using QNetworkAccessManager
   - Override `closeEvent()` to minimize to tray instead of exiting

4. **Create system tray integration** (in `gui/main.py`):
   - Generate placeholder icon (16x16 PNG, simple colored square)
   - QSystemTrayIcon with context menu
   - Menu actions: "Show Dashboard", "Exit Application"
   - Double-click tray icon → show/restore window
   - Right-click tray icon → show context menu

5. **Backend communication** (QNetworkAccessManager):
   - Create GET request to `http://localhost:8765/api/status`
   - Parse JSON response: `{"status": "healthy", "version": "1.0.0"}`
   - Update status bar: "Backend: Connected ✅" or "Backend: Disconnected ❌"
   - Handle network errors gracefully (timeout, connection refused)

**Key Design Decisions:**

- **PyQt5 over Tkinter:** Modern appearance, better widget library, professional desktop app experience
- **QNetworkAccessManager over requests:** Async HTTP, non-blocking GUI, PyQt5-native (though requests is simpler for MVP)
- **Minimize to tray on close:** Common desktop app pattern - users expect dashboard to stay running in background
- **Placeholder tabs with descriptive labels:** Clear indication of future functionality, prevents "empty window" confusion
- **800x600 default window size:** Standard desktop app size, works on most screen resolutions
- **Status bar for backend health:** Immediate visual feedback on backend connection status

---

## Acceptance Criteria

### AC1: GUI Launches Successfully

**Given** GUI dependencies are installed (`pip install -r gui/requirements.txt`)  
**When** developer runs `python gui/main.py`  
**Then** PyQt5 window opens within 5 seconds  
**And** window title is "AutoResumeFiller Dashboard"  
**And** window size is 800x600 pixels  
**And** no errors appear in terminal/console

### AC2: Tabbed Interface Displayed

**Given** GUI window is open  
**When** viewing the main window  
**Then** 4 tabs are visible with labels: "Monitor", "My Data", "Settings", "Chatbot"  
**And** each tab contains a QLabel with placeholder text describing future functionality  
**And** tabs are clickable and switch content when selected  
**And** default tab is "Monitor" (first tab selected on startup)

**Example Placeholder Text:**
- Monitor: "Real-time form-filling activity will appear here. (Epic 6 - Story 6.1)"
- My Data: "View and edit your personal information here. (Epic 6 - Story 6.3)"
- Settings: "Configure AutoResumeFiller settings here. (Epic 6 - Story 6.4)"
- Chatbot: "Chat with AI to update your data conversationally. (Epic 6 - Story 6.5)"

### AC3: System Tray Icon Appears

**Given** GUI is launched on Windows or Linux  
**When** application starts  
**Then** system tray icon appears in taskbar notification area  
**And** hovering over icon shows tooltip: "AutoResumeFiller"  
**And** double-clicking icon shows/restores window from tray  
**And** right-clicking icon shows context menu with "Show Dashboard" and "Exit Application" options

**macOS Note:** System tray may appear as menu bar icon (platform-specific behavior)

### AC4: Minimize to Tray Behavior

**Given** GUI window is open  
**When** user clicks window close button (X)  
**Then** window hides (not destroyed)  
**And** application continues running (process does not exit)  
**And** system tray icon remains visible  
**And** double-clicking tray icon restores window

**When** user selects "Exit Application" from tray menu  
**Then** application exits completely (QApplication.quit())

### AC5: Backend Health Check on Startup

**Given** backend is running on `localhost:8765`  
**When** GUI launches  
**Then** GUI sends GET request to `http://localhost:8765/api/status` within 2 seconds of startup  
**And** status bar displays "Backend: Connected ✅" if response is `{"status": "healthy"}`  
**And** status bar displays "Backend: Disconnected ❌" if request fails (timeout, connection refused, non-200 response)

### AC6: Window Geometry Persistence

**Given** user resizes or moves window  
**When** closing and reopening GUI  
**Then** window restores to previous size and position  
**And** selected tab is remembered (e.g., if "Settings" tab was open, it remains selected on relaunch)

**Implementation:** Use QSettings to save/restore window geometry and last selected tab index

### AC7: Async Backend Communication

**Given** GUI is performing backend health check  
**When** network request is in progress  
**Then** GUI remains responsive (no freezing/blocking)  
**And** status bar shows "Checking backend..." during request  
**And** request completes within 5 seconds (with timeout)

**Implementation:** Use QNetworkAccessManager with signal/slot pattern for async HTTP

### AC8: Error Handling for Backend Unavailable

**Given** backend is NOT running (localhost:8765 unreachable)  
**When** GUI launches and performs health check  
**Then** status bar displays "Backend: Disconnected ❌"  
**And** no application crash or exception dialog  
**And** error message logged to console: `[AutoResumeFiller GUI] Backend health check failed: Connection refused`  
**And** GUI remains functional (tabs clickable, tray icon works)

---

## Dependencies and References

### Links to Epic Tech Spec
- **Epic 1 Tech Spec Section 3.2 (Services and Modules):** gui/main.py, gui/windows/main_window.py
- **Epic 1 Tech Spec Section 4.3 (Data Models → Repository Structure):** gui/ directory with windows/, resources/, tests/
- **Epic 1 Tech Spec Section 5.3 (APIs → GUI → Backend HTTP):** QNetworkAccessManager example code

### Links to Architecture
- **Architecture Section 2.1 (Technology Stack):** PyQt5 for desktop GUI
- **Architecture Section 4.2 (Component Structure → GUI):** Tabbed interface, system tray integration
- **Architecture Section 5.2 (Communication Patterns → GUI ↔ Backend):** HTTP REST via localhost:8765

### Links to Epic
- **Epic 1 Overview:** Foundation & Core Infrastructure
- **Epic 1 Objective:** Deliver GUI shell with tabbed interface for future feature implementation

### Related Stories
- **Story 1.1:** Project Initialization & Repository Setup (PREREQUISITE - provides gui/ directory)
- **Story 1.2:** Python Backend Scaffolding (PREREQUISITE - provides backend API for health check)
- **Story 1.3:** Chrome Extension Manifest & Basic Structure (RELATED - extension "Open Dashboard" will launch GUI)
- **Story 6.1:** Real-Time Event Feed - Monitor Tab (BUILDS ON - implements Monitor tab content)
- **Story 6.3:** Data Management Tab (BUILDS ON - implements My Data tab content)
- **Story 6.4:** Configuration Tab (BUILDS ON - implements Settings tab content)
- **Story 6.5:** Chatbot Tab (BUILDS ON - implements Chatbot tab content)

---

## Estimates

**Story Points:** 5  
**Estimated Time:** 6-8 hours

**Breakdown:**
- PyQt5 installation and verification: 30 minutes
- gui/main.py implementation (QApplication, system tray): 90 minutes
- gui/windows/main_window.py implementation (QMainWindow, tabs): 120 minutes
- Backend health check with QNetworkAccessManager: 60 minutes
- Window geometry persistence (QSettings): 30 minutes
- System tray icon generation (placeholder): 20 minutes
- Testing (launch, tray behavior, backend communication): 60 minutes
- Documentation (README update with GUI launch instructions): 30 minutes
- Git commit and code review prep: 20 minutes

**Risk Factors:**
- ⚠️ First time using PyQt5 (learning curve for QMainWindow, QTabWidget, QSystemTrayIcon)
- ⚠️ System tray behavior platform-specific (Windows vs. Linux vs. macOS)
- ⚠️ QNetworkAccessManager async patterns more complex than requests library
- ✅ PyQt5 well-documented with extensive examples online
- ✅ Placeholder tabs are simple (just QLabel widgets)

**Confidence:** Medium (65%) - PyQt5 learning curve, platform-specific tray behavior, async HTTP complexity

---

## Notes

### Implementation Tips
1. **Start with simple window:** Create basic QMainWindow with single tab, then add complexity (tray, health check, geometry persistence)
2. **Use requests library for MVP:** QNetworkAccessManager is complex - consider using requests library with QThread for async HTTP (simpler for solo developer)
3. **Test tray icon early:** System tray behavior varies by OS - test on target platform (Windows) first
4. **Use Qt Designer:** For complex layouts in future tabs (Epic 6), Qt Designer can generate .ui files for visual design
5. **Log everything:** PyQt5 errors can be cryptic - add print statements liberally during development

### Future Enhancements (Out of Scope)
- ❌ Real-time form monitoring with WebSocket (Epic 6 - Story 6.1)
- ❌ Data management table/form widgets (Epic 6 - Story 6.3)
- ❌ Settings page with configuration options (Epic 6 - Story 6.4)
- ❌ Chatbot interface with message history (Epic 6 - Story 6.5)
- ❌ Native messaging for extension → GUI communication (Story 1.5 or Epic 5)
- ❌ Dark mode theme support (Epic 7 - Production Readiness)

### Open Questions
- ✅ **Q:** Should we use QNetworkAccessManager or requests library for HTTP?  
  **A:** QNetworkAccessManager for learning/async benefits, but requests + QThread acceptable for MVP. Choose based on complexity tolerance.

- ✅ **Q:** Should system tray icon be same as extension icon?  
  **A:** Yes, use same placeholder icon (blue square with "ARF" text) for consistency. Professional icon design in Epic 7.

- ✅ **Q:** Should window geometry persistence use QSettings or custom JSON file?  
  **A:** Use QSettings (PyQt5-native). Stores in platform-specific location (Windows Registry, macOS plist, Linux ~/.config).

- ✅ **Q:** Should "Exit Application" in tray menu show confirmation dialog?  
  **A:** No for MVP - direct exit. Add confirmation in Epic 6 if users report accidental closes.

- ⚠️ **Q:** How should extension "Open Dashboard" button launch GUI?  
  **A:** Deferred to Story 1.5 or Epic 5. Options: native messaging, system command (`python gui/main.py`), or HTTP endpoint to trigger launch.

---

**Story Drafted By:** SM Agent (Scrum Master)  
**Reviewed By:** PM Agent (Product Manager) [Pending]  
**Approved By:** Ragnar [Pending]  
**Ready for Development:** Yes (Story context created 2025-11-28)  
**Implementation Complete:** Yes (2025-11-28)

---

## Dev Agent Record

### Debug Log

**2025-11-28 - Implementation Started**

**Implementation Plan:**
1. ✅ Created `gui/requirements.txt` with PyQt5 5.15.10 dependencies
2. ✅ Created `gui/windows/__init__.py` package marker
3. ✅ Implemented `gui/windows/main_window.py` (QMainWindow with tabs, health check, persistence)
4. ✅ Implemented `gui/main.py` (QApplication with system tray integration)
5. ✅ Installed PyQt5 dependencies (6 packages, ~57 MB)
6. ✅ Verified installation with import test
7. ✅ Launched GUI and verified all 8 acceptance criteria

**Key Design Decisions:**
- Used QNetworkAccessManager for async HTTP (non-blocking GUI)
- QPainter to generate placeholder icon (64x64 blue square with "ARF" text)
- QSettings for window geometry persistence (Windows Registry)
- closeEvent override for minimize-to-tray behavior
- 5-second timeout for backend health check

**Implementation Notes:**
- Tab placeholders include emoji and Epic 6 story references for clarity
- Status bar uses color-coded text (green Connected, red Disconnected, yellow Checking)
- System tray notification on first minimize (user education)
- No single-instance constraint (allows multiple GUI windows for MVP)

### Completion Notes

**Story 1.4 Implementation Complete**

**Files Created (4 files):**
1. `gui/requirements.txt` (9 lines) - PyQt5 dependencies
2. `gui/windows/__init__.py` (8 lines) - Package marker
3. `gui/windows/main_window.py` (293 lines) - QMainWindow with tabs and health check
4. `gui/main.py` (144 lines) - QApplication entry point with system tray

**Total Changes:** ~454 lines of code

**Validation Results:**
✅ PyQt5 5.15.10 installed successfully (6 packages)
✅ GUI launches within 5 seconds
✅ All 4 tabs displayed with placeholder text
✅ System tray icon appears with context menu
✅ Minimize-to-tray behavior works correctly
✅ Backend health check shows "Connected ✅" when backend running
✅ Window geometry persistence via QSettings verified
✅ Async communication (GUI remains responsive)
✅ Error handling when backend unavailable (no crash)

**All 8 Acceptance Criteria Met:**
- AC1: GUI launches successfully ✓
- AC2: Tabbed interface displayed ✓
- AC3: System tray icon appears ✓
- AC4: Minimize to tray behavior ✓
- AC5: Backend health check on startup ✓
- AC6: Window geometry persistence ✓
- AC7: Async backend communication ✓
- AC8: Error handling for backend unavailable ✓

**Console Logs (Backend Available):**
```
[AutoResumeFiller GUI] Starting application...
[AutoResumeFiller GUI] UI components initialized
[AutoResumeFiller GUI] Window geometry restored
[AutoResumeFiller GUI] Restored to tab 0
[AutoResumeFiller GUI] MainWindow initialized
[AutoResumeFiller GUI] System tray icon created
[AutoResumeFiller GUI] Application launched successfully
[AutoResumeFiller GUI] Window visible, system tray icon active
[AutoResumeFiller GUI] Checking backend health...
[AutoResumeFiller GUI] Backend connected (version 1.0.0)
```

**Console Logs (Backend Unavailable):**
```
[AutoResumeFiller GUI] Starting application...
[AutoResumeFiller GUI] UI components initialized
[AutoResumeFiller GUI] Restored to tab 0
[AutoResumeFiller GUI] MainWindow initialized
[AutoResumeFiller GUI] System tray icon created
[AutoResumeFiller GUI] Application launched successfully
[AutoResumeFiller GUI] Window visible, system tray icon active
[AutoResumeFiller GUI] Checking backend health...
[AutoResumeFiller GUI] Backend health check failed: Connection refused
```

**Backend Health Check Verification:**
Backend logs confirm GUI health check request received:
```
INFO:     127.0.0.1:53948 - "GET /api/status HTTP/1.1" 200 OK
```

**Story Ready for Code Review**

Git commit: `a9f2f40` - "Story 1.4: Implement PyQt5 GUI Application Shell"

---

## Change Log

- **2025-11-28 (Update):** Story 1.4 implementation completed by DEV Agent. All 8 acceptance criteria verified. PyQt5 GUI with 4-tab interface, system tray integration, backend health check, window geometry persistence. Files created: gui/requirements.txt, gui/windows/__init__.py, gui/windows/main_window.py, gui/main.py. Total: ~454 lines. Story moved to review status. Git commit: a9f2f40.
- **2025-11-28:** Story 1.4 drafted by SM Agent. PyQt5 GUI application shell with 4 tabbed interface, system tray integration, backend health check on startup, window geometry persistence. Story points: 5, estimated time: 6-8 hours. Prerequisites: Stories 1.1, 1.2 complete. Ready for PM review and approval.

---

## Status

**Current Status:** Review  
**Previous Status:** In Progress  
**Date Updated:** 2025-11-28
