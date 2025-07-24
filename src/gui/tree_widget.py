'''Tree Widget'''
# pylint: disable=invalid-name

import sys
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtCore import Qt


class CustomTreeWidgetItem(QTreeWidgetItem):
    '''Tree Widget Item for proper ordering'''

    def __init__(self, parent=None):
        super().__init__(parent)

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if (not self.text(column) and not otherItem.text(column)):
            try:
                left_check = self.checkState(column)
                right_check = otherItem.checkState(column)
                left_value = 0 if left_check == Qt.Unchecked else (1 if left_check == Qt.PartiallyChecked else 2)
                right_value = 0 if right_check == Qt.Unchecked else (1 if right_check == Qt.PartiallyChecked else 2)
                
                return left_value < right_value
            except Exception:
                return str(self.text(column)).lower() < str(otherItem.text(column)).lower()
        
        try:
            left = int(self.text(column)) if self.text(column) != "-" else sys.maxsize
            right = int(otherItem.text(column)) if otherItem.text(column) != "-" else sys.maxsize
            return left < right
        except ValueError:
            return self.text(column).lower() < otherItem.text(column).lower()