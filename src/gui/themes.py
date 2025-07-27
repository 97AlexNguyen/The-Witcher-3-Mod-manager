from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

def get_enhanced_dark_palette():
    """Enhanced Dark theme với hover effects mượt mà"""
    palette = QPalette()
    
    # Base colors - darker and more modern
    palette.setColor(QPalette.Window, QColor(32, 33, 36))
    palette.setColor(QPalette.WindowText, QColor(232, 234, 237))
    
    palette.setColor(QPalette.Base, QColor(41, 42, 45))
    palette.setColor(QPalette.AlternateBase, QColor(48, 49, 52))
    
    palette.setColor(QPalette.Text, QColor(232, 234, 237))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Button, QColor(48, 49, 52))
    palette.setColor(QPalette.ButtonText, QColor(232, 234, 237))
    
    palette.setColor(QPalette.ToolTipBase, QColor(60, 64, 67))
    palette.setColor(QPalette.ToolTipText, QColor(232, 234, 237))
    
    # Modern blue accents
    palette.setColor(QPalette.Highlight, QColor(66, 133, 244))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Link, QColor(138, 180, 248))
    palette.setColor(QPalette.LinkVisited, QColor(174, 167, 211))
    
    # Disabled states
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(154, 160, 166))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(154, 160, 166))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(154, 160, 166))
    
    return palette

def get_universe_galaxy_palette():
    """Modern Universe theme - minimalist space aesthetic"""
    palette = QPalette()
    
    # Modern dark space colors - không gradient
    palette.setColor(QPalette.Window, QColor(16, 18, 24))  # Deep space
    palette.setColor(QPalette.WindowText, QColor(224, 227, 235))  # Soft white
    
    palette.setColor(QPalette.Base, QColor(22, 24, 30))
    palette.setColor(QPalette.AlternateBase, QColor(28, 30, 36))
    
    palette.setColor(QPalette.Text, QColor(224, 227, 235))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Button, QColor(28, 30, 36))
    palette.setColor(QPalette.ButtonText, QColor(224, 227, 235))
    
    palette.setColor(QPalette.ToolTipBase, QColor(35, 37, 43))
    palette.setColor(QPalette.ToolTipText, QColor(224, 227, 235))
    
    # Subtle purple accent - modern và tinh tế
    palette.setColor(QPalette.Highlight, QColor(106, 90, 205))  # Slate blue
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Link, QColor(147, 112, 219))  # Medium purple
    palette.setColor(QPalette.LinkVisited, QColor(123, 104, 238))  # Medium slate blue
    
    # Disabled states
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 122, 128))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 122, 128))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 122, 128))
    
    return palette

def get_emerald_palette():
    """Modern Emerald theme - sophisticated green"""
    palette = QPalette()
    
    # Modern dark green base - professional
    palette.setColor(QPalette.Window, QColor(16, 24, 20))  # Dark forest
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))  # Almost white
    
    palette.setColor(QPalette.Base, QColor(22, 30, 26))
    palette.setColor(QPalette.AlternateBase, QColor(28, 36, 32))
    
    palette.setColor(QPalette.Text, QColor(236, 240, 241))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Button, QColor(28, 36, 32))
    palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
    
    palette.setColor(QPalette.ToolTipBase, QColor(35, 43, 39))
    palette.setColor(QPalette.ToolTipText, QColor(236, 240, 241))
    
    # Modern emerald accent - không quá sặc sỡ
    palette.setColor(QPalette.Highlight, QColor(52, 168, 83))  # Professional green
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    palette.setColor(QPalette.Link, QColor(26, 127, 55))  # Darker green
    palette.setColor(QPalette.LinkVisited, QColor(22, 163, 74))  # Fresh green
    
    # Disabled states
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(120, 128, 122))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(120, 128, 122))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(120, 128, 122))
    
    return palette

def get_system_palette():
    """System palette mặc định"""
    return QApplication.style().standardPalette()

def apply_enhanced_dark_style(app):
    """Enhanced Dark theme - Modern flat design với rounded corners"""
    app.setStyle("Fusion")
    
    enhanced_dark_stylesheet = """
    /* Modern Flat Menu Bar - Rounded */
    QMenuBar {
        background-color: #202124;
        border: none;
        padding: 6px;
        color: #e8eaed;
        border-radius: 3px;
        margin: 2px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 10px 16px;
        border-radius: 3px;
        margin: 2px;
        font-weight: 500;
    }
    
    QMenuBar::item:hover {
        background-color: rgba(138, 180, 248, 0.15);
        color: #ffffff;
    }
    
    QMenuBar::item:pressed {
        background-color: rgba(138, 180, 248, 0.25);
    }
    
    /* Modern Card-style Menu */
    QMenu {
        background-color: #303134;
        border: none;
        border-radius: 3px;
        padding: 8px;
        color: #e8eaed;
        /* Card shadow effect */
        qproperty-windowOpacity: 0.98;
    }
    
    QMenu::item {
        background-color: transparent;
        padding: 12px 20px;
        margin: 2px;
        border-radius: 3px;
        font-weight: 500;
    }
    
    QMenu::item:hover {
        background-color: rgba(138, 180, 248, 0.2);
        color: #ffffff;
    }
    
    QMenu::item:selected {
        background-color: #4285f4;
        color: #ffffff;
    }
    
    QMenu::separator {
        height: 2px;
        background-color: rgba(255, 255, 255, 0.1);
        margin: 6px 12px;
        border-radius: 1px;
    }
    
    /* Modern Glass Buttons */
    QPushButton {
        background-color: rgba(48, 49, 52, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        padding: 12px 20px;
        color: #e8eaed;
        font-weight: 600;
    }
    
    QPushButton:hover {
        background-color: rgba(138, 180, 248, 0.15);
        border-color: #4285f4;
    }
    
    QPushButton:pressed {
        background-color: rgba(138, 180, 248, 0.25);
    }
    
    /* Modern Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #292a2d;
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        padding: 10px 16px;
        color: #e8eaed;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #4285f4;
        background-color: #303134;
    }
    
    /* Modern Tree Widget */
    QTreeWidget {
        background-color: #292a2d;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        color: #e8eaed;
        outline: none;
        padding: 4px;
    }
    
    QTreeWidget::item {
        padding: 8px;
        border-radius: 3px;
        margin: 1px;
    }
    
    QTreeWidget::item:hover {
        background-color: rgba(138, 180, 248, 0.12);
    }
    
    QTreeWidget::item:selected {
        background-color: #4285f4;
        color: #ffffff;
    }
    
    /* Modern Thin Scrollbars */
    QScrollBar:vertical {
        background: transparent;
        width: 8px;
        border-radius: 4px;
    }
    
    QScrollBar::handle:vertical {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    """
    
    app.setStyleSheet(enhanced_dark_stylesheet)

def apply_universe_style(app):
    """Universe theme - Futuristic với neon accents và geometric shapes"""
    app.setStyle("Fusion")
    
    universe_stylesheet = """
    /* Futuristic Geometric Menu Bar */
    QMenuBar {
        background-color: #0a0c0f;
        border: 2px solid #6a5acd;
        padding: 4px;
        color: #e0e3eb;
        /* Make it angular/geometric */
        border-radius: 0px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 8px 14px;
        /* Angular design */
        border: 1px solid transparent;
        margin: 1px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    QMenuBar::item:hover {
        background-color: rgba(106, 90, 205, 0.3);
        border: 1px solid #6a5acd;
        color: #ffffff;
    }
    
    QMenuBar::item:pressed {
        background-color: rgba(106, 90, 205, 0.5);
    }
    
    /* Sci-Fi Angular Menu */
    QMenu {
        background-color: #0f1419;
        border: 2px solid #9370db;
        /* Angular corners */
        border-radius: 0px;
        padding: 4px;
        color: #e0e3eb;
    }
    
    QMenu::item {
        background-color: transparent;
        padding: 10px 16px;
        margin: 1px;
        /* Angular selection */
        border: 1px solid transparent;
        font-weight: 500;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.5px;
    }
    
    QMenu::item:hover {
        background-color: rgba(106, 90, 205, 0.25);
        border: 1px solid #6a5acd;
        color: #ffffff;
    }
    
    QMenu::item:selected {
        background-color: #6a5acd;
        border: 1px solid #9370db;
        color: #ffffff;
    }
    
    QMenu::separator {
        height: 2px;
        background-color: #6a5acd;
        margin: 4px 8px;
        /* Angular separator */
        border-radius: 0px;
    }
    
    /* Neon Glow Buttons */
    QPushButton {
        background-color: #0f1419;
        border: 2px solid #6a5acd;
        /* Angular buttons */
        border-radius: 0px;
        padding: 10px 18px;
        color: #e0e3eb;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    QPushButton:hover {
        background-color: rgba(106, 90, 205, 0.2);
        border-color: #9370db;
        color: #ffffff;
        /* Neon glow effect simulation */
        font-weight: 800;
    }
    
    QPushButton:pressed {
        background-color: rgba(106, 90, 205, 0.4);
        border-color: #ba55d3;
    }
    
    /* Sci-Fi Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #0a0c0f;
        border: 2px solid #483d8b;
        /* Angular inputs */
        border-radius: 0px;
        padding: 8px 12px;
        color: #e0e3eb;
        font-family: 'Courier New', monospace;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #6a5acd;
        background-color: #0f1419;
        color: #ffffff;
    }
    
    /* Angular Tree Widget */
    QTreeWidget {
        background-color: #0a0c0f;
        border: 2px solid #483d8b;
        /* Angular tree */
        border-radius: 0px;
        color: #e0e3eb;
        outline: none;
        font-family: 'Courier New', monospace;
    }
    
    QTreeWidget::item {
        padding: 6px;
        /* Angular items */
        border-radius: 0px;
        margin: 0px;
        border: 1px solid transparent;
    }
    
    QTreeWidget::item:hover {
        background-color: rgba(106, 90, 205, 0.15);
        border: 1px solid #6a5acd;
    }
    
    QTreeWidget::item:selected {
        background-color: #6a5acd;
        border: 1px solid #9370db;
        color: #ffffff;
    }
    
    /* Neon Scrollbars */
    QScrollBar:vertical {
        background: #0a0c0f;
        width: 16px;
        border: 1px solid #483d8b;
        /* Angular scrollbar */
        border-radius: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: #6a5acd;
        border: 1px solid #9370db;
        /* Angular handle */
        border-radius: 0px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #9370db;
        border-color: #ba55d3;
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    """
    
    app.setStyleSheet(universe_stylesheet)

def apply_emerald_style(app):
    """Emerald theme - Organic curves với nature-inspired design"""
    app.setStyle("Fusion")
    
    emerald_stylesheet = """
    /* Organic Curved Menu Bar */
    QMenuBar {
        background-color: #0d1a0e;
        border: none;
        padding: 8px;
        color: #ecf0f1;
        /* Organic rounded shape */
        border-radius: 3px;
        margin: 4px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 10px 18px;
        /* Very rounded organic shape */
        border-radius: 3px;
        margin: 2px;
        font-weight: 500;
    }
    
    QMenuBar::item:hover {
        background-color: rgba(52, 168, 83, 0.2);
        color: #ffffff;
    }
    
    QMenuBar::item:pressed {
        background-color: rgba(52, 168, 83, 0.35);
    }
    
    /* Organic Bubble Menu */
    QMenu {
        background-color: #152a16;
        border: 3px solid rgba(34, 139, 34, 0.3);
        /* Very rounded organic menu */
        border-radius: 3px;
        padding: 12px;
        color: #ecf0f1;
    }
    
    QMenu::item {
        background-color: transparent;
        padding: 12px 24px;
        margin: 3px;
        /* Pill-shaped items */
        border-radius: 3px;
        font-weight: 500;
    }
    
    QMenu::item:hover {
        background-color: rgba(52, 168, 83, 0.25);
        color: #ffffff;
    }
    
    QMenu::item:selected {
        background-color: #228b22;
        color: #ffffff;
    }
    
    QMenu::separator {
        height: 2px;
        background-color: rgba(34, 139, 34, 0.3);
        margin: 8px 16px;
        /* Rounded separator */
        border-radius: 1px;
    }
    
    /* Organic Pill Buttons */
    QPushButton {
        background-color: #1a2f1b;
        border: 2px solid rgba(34, 139, 34, 0.4);
        /* Pill shape */
        border-radius: 3px;
        padding: 12px 24px;
        color: #ecf0f1;
        font-weight: 600;
    }
    
    QPushButton:hover {
        background-color: rgba(52, 168, 83, 0.2);
        border-color: #32cd32;
        color: #ffffff;
    }
    
    QPushButton:pressed {
        background-color: rgba(52, 168, 83, 0.35);
        border-color: #00ff7f;
    }
    
    /* Organic Leaf Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #0f1e10;
        border: 2px solid rgba(34, 139, 34, 0.2);
        /* Organic leaf shape */
        border-radius: 3px;
        padding: 12px 18px;
        color: #ecf0f1;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #228b22;
        background-color: #152a16;
        border-width: 3px;
    }
    
    /* Organic Tree Widget */
    QTreeWidget {
        background-color: #0f1e10;
        border: 3px solid rgba(34, 139, 34, 0.2);
        /* Organic tree shape */
        border-radius: 3px;
        color: #ecf0f1;
        outline: none;
        padding: 8px;
    }
    
    QTreeWidget::item {
        padding: 8px 12px;
        /* Rounded organic items */
        border-radius: 3px;
        margin: 2px;
    }
    
    QTreeWidget::item:hover {
        background-color: rgba(52, 168, 83, 0.15);
    }
    
    QTreeWidget::item:selected {
        background-color: #228b22;
        color: #ffffff;
    }
    
    /* Organic Vine Scrollbars */
    QScrollBar:vertical {
        background: rgba(15, 30, 16, 0.8);
        width: 18px;
        /* Organic vine shape */
        border-radius: 3px;
        border: 1px solid rgba(34, 139, 34, 0.2);
    }
    
    QScrollBar::handle:vertical {
        background: rgba(34, 139, 34, 0.6);
        /* Organic handle */
        border-radius: 3px;
        min-height: 30px;
        border: 1px solid rgba(50, 205, 50, 0.3);
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(34, 139, 34, 0.8);
        border-color: #32cd32;
    }
    
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    """
    
    app.setStyleSheet(emerald_stylesheet)

# Setup functions cho từng theme
def setup_enhanced_dark_theme(app):
    """Setup Enhanced Dark theme"""
    apply_enhanced_dark_style(app)
    app.setPalette(get_enhanced_dark_palette())

def setup_universe_theme(app):
    """Setup Universe/Galaxy theme"""
    apply_universe_style(app)
    app.setPalette(get_universe_galaxy_palette())

def setup_emerald_theme(app):
    """Setup Emerald theme"""
    apply_emerald_style(app)
    app.setPalette(get_emerald_palette())

# Legacy functions để tương thích
def get_dark_palette():
    """Legacy function - sử dụng enhanced dark palette"""
    return get_enhanced_dark_palette()

def get_light_palette():
    """Legacy function - deprecated, sẽ fallback về enhanced dark"""
    return get_enhanced_dark_palette()

def get_modern_dark_palette():
    """Alias cho enhanced dark palette"""
    return get_enhanced_dark_palette()

def get_modern_light_palette():
    """Deprecated - fallback về enhanced dark"""
    return get_enhanced_dark_palette()

def setup_modern_dark_theme(app):
    """Alias cho enhanced dark theme"""
    setup_enhanced_dark_theme(app)

def setup_modern_light_theme(app):
    """Deprecated - fallback về enhanced dark"""
    setup_enhanced_dark_theme(app)