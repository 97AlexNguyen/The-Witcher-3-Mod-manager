'''Enhanced Dialog Preferences and Configuration'''

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QLabel, QGroupBox, QRadioButton, QButtonGroup
from src.globals.constants import translate


class DialogPreferencesDialog(QDialog):
    '''Dialog for configuring file dialog preferences'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translate("MainWindow", "File Dialog Preferences"))
        self.setModal(True)
        self.resize(500, 400)
        
        self.setupUI()
        self.loadCurrentSettings()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Dialog Type Group
        dialog_group = QGroupBox(translate("MainWindow", "Dialog Type"))
        dialog_layout = QVBoxLayout(dialog_group)
        
        self.dialog_button_group = QButtonGroup(self)
        
        self.native_radio = QRadioButton(translate("MainWindow", "Native Windows Dialog (Recommended)"))
        self.native_radio.setToolTip(translate("MainWindow", 
            "Uses Windows native file dialog with all features:\n"
            "• Quick access to common folders\n"
            "• Recently used folders and favorites\n"
            "• Network locations and drives\n"
            "• Full context menu support\n"
            "• Address bar for direct navigation\n"
            "• Previous versions support\n"
            "• Preview pane and thumbnails"))
        
        self.qt_radio = QRadioButton(translate("MainWindow", "Qt Dialog (Basic)"))
        self.qt_radio.setToolTip(translate("MainWindow", 
            "Uses Qt's built-in dialog with basic features"))
        
        self.auto_radio = QRadioButton(translate("MainWindow", "Automatic (Native on Windows, Qt elsewhere)"))
        self.auto_radio.setToolTip(translate("MainWindow", 
            "Automatically chooses the best dialog for your platform"))
        
        self.dialog_button_group.addButton(self.native_radio, 0)
        self.dialog_button_group.addButton(self.qt_radio, 1)
        self.dialog_button_group.addButton(self.auto_radio, 2)
        
        dialog_layout.addWidget(self.native_radio)
        dialog_layout.addWidget(self.qt_radio)
        dialog_layout.addWidget(self.auto_radio)
        
        layout.addWidget(dialog_group)
        
        # Additional Features Group
        features_group = QGroupBox(translate("MainWindow", "Additional Features"))
        features_layout = QVBoxLayout(features_group)
        
        self.remember_last_path = QCheckBox(translate("MainWindow", "Remember last used folder"))
        self.remember_last_path.setToolTip(translate("MainWindow", 
            "Automatically navigate to the last used folder in file dialogs"))
        
        self.show_hidden_files = QCheckBox(translate("MainWindow", "Show hidden files and folders"))
        self.show_hidden_files.setToolTip(translate("MainWindow", 
            "Display hidden files and folders in file dialogs"))
        
        self.detailed_view = QCheckBox(translate("MainWindow", "Use detailed view by default"))
        self.detailed_view.setToolTip(translate("MainWindow", 
            "Show file details (size, date modified, etc.) by default"))
        
        self.confirm_overwrites = QCheckBox(translate("MainWindow", "Confirm file overwrites"))
        self.confirm_overwrites.setToolTip(translate("MainWindow", 
            "Ask for confirmation before overwriting existing files"))
        
        features_layout.addWidget(self.remember_last_path)
        features_layout.addWidget(self.show_hidden_files)
        features_layout.addWidget(self.detailed_view)
        features_layout.addWidget(self.confirm_overwrites)
        
        layout.addWidget(features_group)
        
        # Performance Group
        performance_group = QGroupBox(translate("MainWindow", "Performance"))
        performance_layout = QVBoxLayout(performance_group)
        
        self.enable_previews = QCheckBox(translate("MainWindow", "Enable file previews and thumbnails"))
        self.enable_previews.setToolTip(translate("MainWindow", 
            "Show preview pane and thumbnails (may slow down navigation in large folders)"))
        
        self.enable_network_places = QCheckBox(translate("MainWindow", "Enable network places"))
        self.enable_network_places.setToolTip(translate("MainWindow", 
            "Allow access to network drives and locations"))
        
        performance_layout.addWidget(self.enable_previews)
        performance_layout.addWidget(self.enable_network_places)
        
        layout.addWidget(performance_group)
        
        # Information
        info_label = QLabel(translate("MainWindow", 
            "Note: Native Windows dialogs provide the best user experience with features like:\n"
            "• Drag and drop support\n"
            "• Quick navigation shortcuts (Ctrl+D for Desktop, etc.)\n"
            "• Integration with Windows Search\n"
            "• Shell extensions and custom context menus"))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { color: #666; font-style: italic; padding: 10px; }")
        
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton(translate("MainWindow", "OK"))
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton(translate("MainWindow", "Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        
        self.apply_button = QPushButton(translate("MainWindow", "Apply"))
        self.apply_button.clicked.connect(self.applySettings)
        
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def loadCurrentSettings(self):
        '''Load current settings from config'''
        from src.globals import data
        
        # Dialog type
        use_native = data.config.get('SETTINGS', 'usenativedialog', '1') == '1'
        force_qt = data.config.get('SETTINGS', 'forceqtdialog', '0') == '1'
        
        if force_qt:
            self.qt_radio.setChecked(True)
        elif use_native:
            self.native_radio.setChecked(True)
        else:
            self.auto_radio.setChecked(True)
        
        # Additional features
        self.remember_last_path.setChecked(
            data.config.get('SETTINGS', 'remember_last_path', '1') == '1')
        self.show_hidden_files.setChecked(
            data.config.get('SETTINGS', 'show_hidden_files', '0') == '1')
        self.detailed_view.setChecked(
            data.config.get('SETTINGS', 'detailed_view', '1') == '1')
        self.confirm_overwrites.setChecked(
            data.config.get('SETTINGS', 'confirm_overwrites', '1') == '1')
        
        # Performance
        self.enable_previews.setChecked(
            data.config.get('SETTINGS', 'enable_previews', '1') == '1')
        self.enable_network_places.setChecked(
            data.config.get('SETTINGS', 'enable_network_places', '1') == '1')
    
    def applySettings(self):
        '''Apply current settings to config'''
        from src.globals import data
        
        # Dialog type
        if self.native_radio.isChecked():
            data.config.set('SETTINGS', 'usenativedialog', '1')
            data.config.set('SETTINGS', 'forceqtdialog', '0')
        elif self.qt_radio.isChecked():
            data.config.set('SETTINGS', 'usenativedialog', '0')
            data.config.set('SETTINGS', 'forceqtdialog', '1')
        else:  # auto
            data.config.set('SETTINGS', 'usenativedialog', '1')
            data.config.set('SETTINGS', 'forceqtdialog', '0')
        
        # Additional features
        data.config.set('SETTINGS', 'remember_last_path', 
                       '1' if self.remember_last_path.isChecked() else '0')
        data.config.set('SETTINGS', 'show_hidden_files', 
                       '1' if self.show_hidden_files.isChecked() else '0')
        data.config.set('SETTINGS', 'detailed_view', 
                       '1' if self.detailed_view.isChecked() else '0')
        data.config.set('SETTINGS', 'confirm_overwrites', 
                       '1' if self.confirm_overwrites.isChecked() else '0')
        
        # Performance
        data.config.set('SETTINGS', 'enable_previews', 
                       '1' if self.enable_previews.isChecked() else '0')
        data.config.set('SETTINGS', 'enable_network_places', 
                       '1' if self.enable_network_places.isChecked() else '0')
        
        print("Dialog preferences applied successfully")
    
    def accept(self):
        '''Accept and apply settings'''
        self.applySettings()
        super().accept()


def showDialogPreferences(parent=None):
    '''Show dialog preferences window'''
    dialog = DialogPreferencesDialog(parent)
    return dialog.exec()