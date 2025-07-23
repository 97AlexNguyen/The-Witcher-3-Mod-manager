'''Updated Description Widget for displaying mod descriptions with API support'''

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from src.globals.constants import translate
from src.util.mod_description_fetcher import ModDescriptionFetcher


class DescriptionFetchThread(QThread):
    '''Thread to fetch description without blocking UI'''
    
    description_fetched = Signal(str)
    output_message = Signal(str)
    
    def __init__(self, mod_id, output_callback=None):
        super().__init__()
        self.mod_id = mod_id
        self.fetcher = ModDescriptionFetcher()
        self.output_callback = output_callback
    
    def run(self):
        if self.mod_id:
            # Create callback to emit messages
            def emit_output(message):
                self.output_message.emit(message)
            
            description = self.fetcher.get_description(
                self.mod_id, 
                output_callback=emit_output if self.output_callback else None
            )
            self.description_fetched.emit(description)
        else:
            self.description_fetched.emit("No mod ID available")


class DescriptionWidget(QWidget):
    '''Widget to display mod description with enhanced API support'''
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_thread = None
        self.output_callback = None
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # Title label
        self.title_label = QLabel(translate("MainWindow", "Mod Description"))
        self.title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.title_label)
        
        # Text edit to display description
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setPlaceholderText(
            translate("MainWindow", "Select a mod to view its description...")
        )
        # Set word wrap and formatting
        self.description_text.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.description_text)
        
        self.setLayout(layout)
    
    def set_output_callback(self, callback):
        '''Set callback function for output messages'''
        self.output_callback = callback
    
    def clear_description(self):
        '''Clear description display'''
        self.description_text.clear()
        self.description_text.setPlaceholderText(
            translate("MainWindow", "Select a mod to view its description...")
        )
    
    def show_loading(self, mod_name: str):
        '''Show loading message'''
        self.description_text.setPlainText(
            translate("MainWindow", f"Loading description for {mod_name}...")
        )
    
    def display_description(self, mod, fetch_if_needed=True):
        '''Display description for the given mod'''
        if not mod:
            self.clear_description()
            return
        
        # If description already exists, display immediately
        if mod.description:
            self.description_text.setPlainText(mod.description)
            return
        
        # If mod_id exists but no description yet
        if mod.mod_id and fetch_if_needed:
            self.show_loading(mod.name)
            
            # Clean up old thread if exists
            if self.current_thread:
                self.current_thread.quit()
                self.current_thread.wait()
            
            # Create new thread to fetch description
            self.current_thread = DescriptionFetchThread(
                mod.mod_id, 
                output_callback=self.output_callback
            )
            
            # Connect signals
            self.current_thread.description_fetched.connect(
                lambda desc: self.on_description_fetched(mod, desc)
            )
            
            if self.output_callback:
                self.current_thread.output_message.connect(self.output_callback)
            
            self.current_thread.start()
        else:
            # No mod_id or do not want to fetch
            if mod.mod_id:
                self.description_text.setPlainText(
                    translate("MainWindow", "No description available. Click 'Fetch Description' to load from Nexus Mods.")
                )
            else:
                self.description_text.setPlainText(
                    translate("MainWindow", "No mod ID detected. Cannot fetch description from Nexus Mods.")
                )
    
    def on_description_fetched(self, mod, description):
        '''Handle when description is fetched'''
        mod.description = description
        self.description_text.setPlainText(description)
        
        # Signal parent to save mod data
        if hasattr(self.parent(), 'model'):
            self.parent().model.write()
    
    def force_fetch_description(self, mod):
        '''Force fetch description even if already exists'''
        if mod and mod.mod_id:
            self.show_loading(mod.name)
            
            # Output message about force refresh
            if self.output_callback:
                self.output_callback(f"Force refreshing description for mod {mod.name} (ID: {mod.mod_id})")
            
            # Clean up old thread if exists
            if self.current_thread:
                self.current_thread.quit()
                self.current_thread.wait()
            
            # Remove old description to force fetch
            mod.description = None
            
            # Create new thread to fetch description
            self.current_thread = DescriptionFetchThread(
                mod.mod_id,
                output_callback=self.output_callback
            )
            
            # Connect signals
            self.current_thread.description_fetched.connect(
                lambda desc: self.on_description_fetched(mod, desc)
            )
            
            if self.output_callback:
                self.current_thread.output_message.connect(self.output_callback)
            
            self.current_thread.start()
    
    def __del__(self):
        '''Clean up thread when widget is destroyed'''
        if self.current_thread:
            self.current_thread.quit()
            self.current_thread.wait()