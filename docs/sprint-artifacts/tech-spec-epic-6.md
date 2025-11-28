# Epic Technical Specification: Real-Time Monitoring Dashboard

Date: 2025-11-28
Author: Ragnar
Epic ID: 6
Status: Draft

---

## Overview

Epic 6 implements the Real-Time Monitoring Dashboard using PyQt5, providing users with complete visibility and control over the AutoResumeFiller system. The dashboard features five main components: real-time event feed, confirmation panel, data management tab, configuration tab, chatbot tab, and system tray integration with notifications.

The dashboard serves as the command center for the entire application, displaying detected forms, generated responses, allowing data CRUD operations, configuring AI providers, and enabling conversational profile updates via chatbot.

This epic enables 16 functional requirements (FR40-FR55) and completes the user-facing GUI alongside form filling automation (Epic 5).

## Objectives and Scope

**In Scope:**
- Real-time event log (500ms polling, last 100 events)
- Confirmation panel with approve/reject workflow for each field
- Data Management Tab: View/edit UserProfile (personal info, work experience, education, skills, projects, certifications)
- Configuration Tab: AI provider settings, API keys, backend settings, GUI preferences, backup settings
- Chatbot Tab: Messenger-style UI for conversational profile updates
- System tray icon with context menu and notifications
- Backend connectivity status indicator
- Log viewer for debugging

**Out of Scope:**
- Real-time WebSocket streaming (uses polling for MVP)
- Charts/analytics dashboard (deferred)
- Multi-language support (English only)
- Mobile/tablet GUI (desktop only)

**Success Criteria:**
- Dashboard launches in <3 seconds
- Event feed updates within 500ms of backend event
- All CRUD operations complete in <200ms
- Chatbot responses display within 3 seconds
- System tray minimization/restore works reliably

## System Architecture Alignment

Epic 6 implements the **GUI Layer** (PyQt5 Desktop Application):

**Architecture:**
```
gui/
├── main.py                      # Application entry point
├── windows/
│   ├── main_window.py           # Main dashboard window (QTabWidget)
│   └── setup_wizard.py          # First-run setup (Epic 7)
├── tabs/
│   ├── monitor_tab.py           # Real-time event feed
│   ├── confirmation_tab.py      # Field approval panel
│   ├── data_tab.py              # Data management forms
│   ├── config_tab.py            # Configuration settings
│   └── chatbot_tab.py           # Conversational updates
├── widgets/
│   ├── event_log_widget.py      # Event display component
│   ├── confirmation_widget.py   # Field preview cards
│   ├── data_form_widget.py      # User data forms
│   └── chatbot_widget.py        # Chat UI component
├── services/
│   ├── backend_client.py        # HTTP client to backend
│   ├── event_poller.py          # Polling service
│   └── system_tray.py           # Tray icon manager
└── resources/
    ├── icons/
    ├── styles.qss               # Qt stylesheet
    └── images/
```

**Communication Flow:**
```
Extension → Backend API → GUI polling → Event display
Extension → Backend → Confirmation needed → GUI shows modal
User edits data in GUI → Backend API → Update user_profile.json
```

## Detailed Design

### Tab 1: Real-Time Event Feed (Monitor Tab)

**Event Types:**
- form_detected: "Detected job application on workday.com"
- field_analyzed: "Found 25 fields on page"
- response_generated: "Generated answer for 'Why Google?'"
- field_filled: "Filled 'Email Address' with john.doe@example.com"
- manual_edit: "User manually edited 'Phone Number'"
- error: "Failed to fill dropdown 'Country' - no matching option"

**UI Components:**
```python
class EventLogWidget(QWidget):
    def __init__(self):
        self.log_display = QTextEdit(readOnly=True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        
        # Polling timer (500ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_events)
        self.timer.start(500)
    
    def fetch_events(self):
        response = requests.get('http://localhost:8765/api/events/recent')
        events = response.json()['events']
        for event in events:
            self.add_event(event)
    
    def add_event(self, event):
        color = self.get_color_for_type(event['type'])
        timestamp = event['timestamp']
        message = event['message']
        
        html = f'<span style="color: #888;">[{timestamp}]</span> '
        html += f'<span style="color: {color}; font-weight: bold;">{event["type"].upper()}</span>: '
        html += f'<span>{message}</span><br>'
        
        self.log_display.append(html)
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
```

**Backend Endpoint:**
```python
from collections import deque

recent_events = deque(maxlen=100)

@app.post("/api/events/add")
async def add_event(event: Event):
    event_data = event.dict()
    event_data['timestamp'] = datetime.now().strftime("%H:%M:%S")
    recent_events.append(event_data)
    return {"success": True}

@app.get("/api/events/recent")
async def get_recent_events(since: Optional[str] = None):
    # Return events since timestamp (or all if none)
    return {"events": list(recent_events)}
```

### Tab 2: Confirmation Panel

**UI Layout:**
```python
class ConfirmationWidget(QWidget):
    def __init__(self):
        layout = QVBoxLayout()
        
        # Scroll area for multiple field previews
        scroll = QScrollArea()
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        scroll.setWidget(self.fields_container)
        
        layout.addWidget(QLabel("Review and Approve Responses"))
        layout.addWidget(scroll)
        
        # Bulk actions
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Approve All"))
        btn_layout.addWidget(QPushButton("Reject All"))
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def add_field_preview(self, field_data):
        card = FieldPreviewCard(field_data)
        card.approved.connect(self.handle_approval)
        card.rejected.connect(self.handle_rejection)
        card.edited.connect(self.handle_edit)
        self.fields_layout.addWidget(card)

class FieldPreviewCard(QWidget):
    approved = pyqtSignal(str)  # field_id
    rejected = pyqtSignal(str)
    edited = pyqtSignal(str, str)  # field_id, new_value
    
    def __init__(self, field_data):
        layout = QVBoxLayout()
        
        # Field label
        layout.addWidget(QLabel(f"<b>{field_data['label']}</b>"))
        
        # Generated value (editable)
        self.value_edit = QLineEdit(field_data['value'])
        layout.addWidget(self.value_edit)
        
        # Metadata
        metadata = field_data.get('metadata', {})
        if metadata:
            meta_text = f"Source: {metadata.get('source', 'N/A')} | "
            meta_text += f"Confidence: {metadata.get('confidence', 0):.0%}"
            layout.addWidget(QLabel(f"<small>{meta_text}</small>"))
        
        # Action buttons
        btn_layout = QHBoxLayout()
        approve_btn = QPushButton("✓ Approve")
        approve_btn.clicked.connect(lambda: self.approved.emit(field_data['field_id']))
        approve_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        reject_btn = QPushButton("✗ Reject")
        reject_btn.clicked.connect(lambda: self.rejected.emit(field_data['field_id']))
        reject_btn.setStyleSheet("background-color: #F44336; color: white;")
        
        btn_layout.addWidget(approve_btn)
        btn_layout.addWidget(reject_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
```

### Tab 3: Data Management Tab

**Sub-tabs:**
- Personal Information
- Work Experience
- Education
- Skills
- Projects
- Certifications

**Personal Info Form:**
```python
class PersonalInfoForm(QWidget):
    def __init__(self):
        layout = QFormLayout()
        
        self.first_name = QLineEdit()
        self.last_name = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.linkedin = QLineEdit()
        self.github = QLineEdit()
        
        layout.addRow("First Name:", self.first_name)
        layout.addRow("Last Name:", self.last_name)
        layout.addRow("Email:", self.email)
        layout.addRow("Phone:", self.phone)
        layout.addRow("LinkedIn URL:", self.linkedin)
        layout.addRow("GitHub URL:", self.github)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_personal_info)
        layout.addRow(save_btn)
        
        self.setLayout(layout)
        self.load_data()
    
    def load_data(self):
        response = requests.get('http://localhost:8765/api/user-data')
        data = response.json()['personal_info']
        
        self.first_name.setText(data.get('first_name', ''))
        self.last_name.setText(data.get('last_name', ''))
        self.email.setText(data.get('email', ''))
        self.phone.setText(data.get('phone', ''))
        self.linkedin.setText(data.get('linkedin_url', ''))
        self.github.setText(data.get('github_url', ''))
    
    def save_personal_info(self):
        data = {
            'first_name': self.first_name.text(),
            'last_name': self.last_name.text(),
            'email': self.email.text(),
            'phone': self.phone.text(),
            'linkedin_url': self.linkedin.text(),
            'github_url': self.github.text()
        }
        
        response = requests.put('http://localhost:8765/api/user-data/personal_info', json=data)
        if response.ok:
            QMessageBox.information(self, "Success", "Personal information saved!")
```

### Tab 4: Configuration Tab

**Sections:**
1. AI Provider Settings
2. Backend Server Settings
3. GUI Preferences
4. Backup & Data Settings

**AI Provider Config:**
```python
class AIProviderConfigWidget(QWidget):
    def __init__(self):
        layout = QVBoxLayout()
        
        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["OpenAI", "Anthropic", "Google"])
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        layout.addWidget(QLabel("Preferred AI Provider:"))
        layout.addWidget(self.provider_combo)
        
        # API Key management
        layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter API key")
        
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_input)
        
        save_key_btn = QPushButton("Save Key")
        save_key_btn.clicked.connect(self.save_api_key)
        api_key_layout.addWidget(save_key_btn)
        
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.test_api_key)
        api_key_layout.addWidget(test_btn)
        
        layout.addLayout(api_key_layout)
        
        # Model selection
        layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        layout.addWidget(self.model_combo)
        
        self.setLayout(layout)
        self.load_config()
    
    def test_api_key(self):
        provider = self.provider_combo.currentText().lower()
        api_key = self.api_key_input.text()
        
        response = requests.post('http://localhost:8765/api/ai-providers/validate', json={
            'provider': provider,
            'api_key': api_key
        })
        
        if response.ok and response.json()['valid']:
            QMessageBox.information(self, "Success", "API key is valid!")
        else:
            QMessageBox.warning(self, "Error", "Invalid API key")
```

### Tab 5: Chatbot Tab

**Messenger-Style UI:**
```python
class ChatbotWidget(QWidget):
    def __init__(self):
        layout = QVBoxLayout()
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message...")
        self.message_input.returnPressed.connect(self.send_message)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        self.setLayout(layout)
        
        self.add_bot_message("Hi! I'm here to help you update your profile. "
                            "Try saying 'Add Python to my skills' or 'I worked at Google from 2020 to 2022'.")
    
    def send_message(self):
        user_message = self.message_input.text().strip()
        if not user_message:
            return
        
        self.add_user_message(user_message)
        self.message_input.clear()
        
        # Send to backend
        response = requests.post('http://localhost:8765/api/chatbot/message', json={
            'message': user_message
        })
        
        if response.ok:
            bot_response = response.json()
            self.handle_bot_response(bot_response)
    
    def add_user_message(self, message):
        self.chat_display.append(
            f'<div style="text-align: right; margin: 10px;">'
            f'<span style="background-color: #0084ff; color: white; '
            f'padding: 8px 12px; border-radius: 18px; display: inline-block;">'
            f'{message}</span></div>'
        )
    
    def add_bot_message(self, message):
        self.chat_display.append(
            f'<div style="text-align: left; margin: 10px;">'
            f'<span style="background-color: #e4e6eb; color: black; '
            f'padding: 8px 12px; border-radius: 18px; display: inline-block;">'
            f'{message}</span></div>'
        )
```

### System Tray Integration

```python
class SystemTrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(QIcon('resources/icons/tray_icon.png'))
        
        # Context menu
        menu = QMenu()
        menu.addAction("Show Dashboard", self.main_window.show)
        menu.addAction("Hide Dashboard", self.main_window.hide)
        menu.addSeparator()
        menu.addAction("Backend Status", self.check_backend_status)
        menu.addSeparator()
        menu.addAction("Quit", self.quit_application)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_clicked)
        self.tray_icon.show()
    
    def show_notification(self, title, message):
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
```

## Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| Dashboard launch time | <3 seconds |
| Event feed update latency | <500ms |
| Tab switching | <100ms |
| CRUD operation response | <200ms |

### Usability

- Keyboard shortcuts (Ctrl+1-5 for tab switching)
- Responsive layout (resizable window, minimum 1024x768)
- High contrast text for readability
- Tooltips on all buttons

## Acceptance Criteria (Authoritative)

### AC1: Event Feed Real-Time
**Given** backend generates event  
**When** GUI polls within 500ms  
**Then** event appears in monitor tab  
**And** auto-scrolls to bottom  
**And** colored by event type

### AC2: Confirmation Workflow Works
**Given** 10 fields need approval  
**When** confirmation panel displays fields  
**Then** each field shows label, value, approve/reject buttons  
**When** user approves field  
**Then** backend notified, field filled in browser

### AC3: Data Management CRUD
**Given** personal info loaded  
**When** user edits email field  
**And** clicks "Save Changes"  
**Then** `PUT /api/user-data/personal_info` called  
**And** changes persisted to user_profile.json  
**And** success message displayed

### AC4: AI Provider Config
**Given** user selects "Anthropic"  
**When** enters API key and clicks "Test Connection"  
**Then** backend validates key  
**And** "Valid" or "Invalid" message shown

### AC5: Chatbot Updates Data
**Given** user types "Add React to my skills"  
**When** chatbot processes message  
**Then** bot suggests: "I'll add React to your skills. Confirm?"  
**When** user confirms  
**Then** backend updates skills list  
**And** confirmation message displayed

### AC6: System Tray Works
**Given** dashboard minimized  
**When** user clicks tray icon  
**Then** dashboard restored and activated  
**When** backend detects form  
**Then** tray notification shown

## Summary

Epic 6 delivers comprehensive GUI dashboard with:
- ✅ Real-time event monitoring (500ms polling)
- ✅ Field-by-field confirmation workflow
- ✅ Complete data management (CRUD)
- ✅ AI provider configuration
- ✅ Conversational profile updates
- ✅ System tray integration

**Next Epic:** Epic 7 (Production Readiness & Distribution) packages the application for end-user distribution.

**Status:** Ready for implementation.
