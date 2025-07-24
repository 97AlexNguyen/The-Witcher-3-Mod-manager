from PySide6 import QtCore
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLineEdit, QPushButton, QLabel, QMessageBox
)

from src.globals.constants import translate
from src.util.resource_utils import load_category_mapping


class CategoryDialog(QDialog):
    '''Dialog for setting mod category with resource-aware category loading'''

    def __init__(self, parent, current_category='General'):
        super().__init__(parent)
        
        self.setWindowTitle(translate("MainWindow", "Set Category"))
        self.setModal(True)
        self.resize(350, 150)
        
        layout = QVBoxLayout(self)
        
        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel(translate("MainWindow", "Category:")))
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        
        # UPDATED: Load categories using standardized method
        try:
            from src.util.resource_utils import get_predefined_categories_list
            categories = get_predefined_categories_list()
            self.category_combo.addItems(categories)
            print(f"[CategoryDialog] Loaded {len(categories)} categories")
        except Exception as e:
            print(f"[CategoryDialog] Failed to load categories: {e}")
            # Fallback categories
            self.category_combo.addItems(['General', 'Miscellaneous', 'Visuals and Graphics', 'Combat', 'Gameplay Changes'])
        
        self.category_combo.setCurrentText(current_category)
        category_layout.addWidget(self.category_combo)
        
        layout.addLayout(category_layout)
        
        # Custom category input
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel(translate("MainWindow", "Or enter custom:")))
        
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText(translate("MainWindow", "Enter custom category..."))
        custom_layout.addWidget(self.custom_input)
        
        layout.addLayout(custom_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton(translate("MainWindow", "OK"))
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton(translate("MainWindow", "Cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_category(self) -> str:
        if self.custom_input.text().strip():
            return self.custom_input.text().strip()
        return self.category_combo.currentText()