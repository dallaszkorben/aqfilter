import sys
import time 

#from PyQt5 import Qt

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLabel

from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QStyleOptionViewItem
from PyQt5.QtWidgets import QStyle

from PyQt5.QtCore import QItemSelection
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSortFilterProxyModel  
from PyQt5.QtCore import QStringListModel
from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import QRegExp

from PyQt5 import QtCore
from PyQt5 import QtGui

from PyQt5.QtGui import QFont
from PyQt5.QtGui import QStandardItemModel, QStandardItem


#from PyQt5.QtWidgets import QAbstractItemView

# ===================
#
# AkoFilter 
#
# ===================
class AQFilter(QWidget):
    DEFAULT_MAX_LINE = 10
    DEFAULT_MIN_CHARS = 0
    
    def __init__(self, parent):
        super().__init__(parent)

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(0)
        self.setLayout(self_layout)

        self.parent = parent
        self.main_window = self.get_main_window()
        
        self.max_line = AQFilter.DEFAULT_MAX_LINE
        self.min_chars_to_show_list = AQFilter.DEFAULT_MIN_CHARS
        
        self.value = ""
        self.index = -1
        
        self.list = []
        
        # Input field Widget
        self.input_widget = QLineEdit(self)
        self.input_widget.setText(self.value)
        self_layout.addWidget(self.input_widget)
        self.input_widget.textChanged.connect(self.input_changed)
        
#        # List Widget
#        self.list_widget = QListWidget(self)
#        self.list_widget.setHidden(True)
        
        self.custom_auto_completer = CustomCompleter()
        self.custom_auto_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.custom_auto_completer.setCaseSensitivity(0)
        self.input_widget.setCompleter(self.custom_auto_completer)
        self_layout.addWidget(self.input_widget)

        self.model = MyListModel(self.list)
        self.custom_auto_completer.setModel(self.model)

    def input_changed(self, value):
        self.value = value
        
    # #############
    # addItemToList
    # #############
    def addItemToList(self, value, index):
        """Add value-index pair to the  list"""
        self.list.append((value,index))
        self.custom_auto_completer.setModel(self.model)

    # #############
    # getValue
    # #############
    def getValue(self):
        return self.value
    
    def getIndexes(self):
        return [l[1] for l in self.list if self.value in l[0]]
    
    
#    # ############
#    # setMaxLine
#    # ############
#    def setMaxLine(self, max_line):
#        """Set the max number of lines of the list"""
#        self.max_line = max_line
#
#    # #####################
#    # setMinCharsToShowList
#    # #####################
#    def setMinCharsToShowList(self, min_chars):
#        self.min_chars_to_show_list = min_chars
#
#    def set_selected_value_index(self, value, index):
#        """Set the value-index by the selected element from the list"""
#        self.set_typed_value_index(value, index)
#        self.input_widget.setText(value)
#        
#    def set_typed_value_index(self, value, index=None):
#        """Set the value-index by the typed key"""
#        self.value = value
#        self.index = index
#      
#    def hide_list(self):
#        """Hide the list"""
#        self.list_widget.setHidden(True)      

    def get_main_window(self):
        """Search for the Main Window"""
        def get(widget, ret=None):
            parent = widget.parentWidget()
            if parent:
                ret = get(parent)
            else:
                ret = widget
            return ret
        
        main_window = get(self)
        return main_window


        
        
  
class HTMLDelegate(QStyledItemDelegate):
    """ From: https://stackoverflow.com/a/5443112/1504082 """
    def __init__(self, filter_model):
        super().__init__()
        self.filter_model = filter_model
        
    def paint(self, painter, option, index):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        if options.widget is None:
            style = QtGui.QApplication.style()
        else:
            style = options.widget.style()

        doc = QtGui.QTextDocument()

        pattern = self.filter_model.filterRegExp().pattern()
        if pattern.lower() in options.text.lower():
            start = options.text.lower().index(pattern.lower())
            end = len(pattern) + start
            part_1 = options.text[0:start]
            part_2 = options.text[start:end]
            part_3 = options.text[end:]                
            label = part_1 + '<b>' + part_2 + '</b>' + part_3
            doc.setHtml(label)            
        else:
            doc.setHtml(options.text)

        doc.setTextWidth(option.rect.width())
        options.text = ""
        style.drawControl(QStyle.CE_ItemViewItem, options, painter)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        textRect = style.subElementRect(QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = QStyleOptionViewItem(option)
#       self.initStyleOption(options, index)
        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
#       print(options.text)
#       doc.setTextWidth(options.rect.width())
        return QtCore.QSize(doc.size().width(), doc.size().height())

        
class CustomCompleter(QCompleter):

    def __init__(self):
        super(CustomCompleter, self).__init__()
        self.source_model = None
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.delegate = HTMLDelegate(self.filterProxyModel)

    def setModel(self, model):
        self.source_model = model
        self.filterProxyModel = QSortFilterProxyModel(self)
        self.filterProxyModel.setSourceModel(self.source_model)
        super(CustomCompleter, self).setModel(self.filterProxyModel)
        
        self.delegate.filter_model = self.filterProxyModel

    def updateModel(self, local_completion_prefix):
        self.filterProxyModel.setSourceModel(self.source_model)

        pattern = QRegExp(local_completion_prefix, Qt.CaseInsensitive, QRegExp.FixedString)

        self.filterProxyModel.setFilterRegExp(pattern)
                
        self.popup().setItemDelegate(self.delegate)

    def splitPath(self, path):
        self.updateModel(path)

        return []
        #if self.filterProxyModel.rowCount() == 0:
        #    self.usingOriginalModel = False
        #    self.filterProxyModel.setSourceModel(QStringListModel([path]))
        #    print(path)
        #    return [path]
        #else:
        #    return []
    

class MyListModel(QAbstractListModel):
    
    def __init__(self, mylist):
        super().__init__()
        self.mylist = mylist

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
                
        if row > len(self.mylist):
            return None
 
        if role == Qt.DisplayRole:
            return self.mylist[row][0]

        if role == Qt.EditRole:
#            self.value = self.mylist[row][0]
#            self.index = self.mylist[row][1]
            return self.mylist[row][0]
            
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self.mylist)

    def flags(self, index):
        flags = super().flags(index)
        #if index.isValid():
        #flags |= not Qt.ItemIsSelectable 
        #flags |= not Qt.ItemIsSelectable
        #   flags |= Qt.ItemIsDragEnabled
        #else:
        #    flags = Qt.ItemIsDropEnabled
        #print('flag', flags)
        flags = Qt.ItemIsEnabled
        return flags
            
#   def roleNames(self):
#       return {
#                    Qt.UserRole + 1: b'value',
#                    Qt.UserRole + 2: b'key'
#                }



class Test(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
                
        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(10, 10, 10, 10)
        self_layout.setSpacing(0)
        self.setLayout(self_layout)
    
        # Show value field - read only
        self.show_value_field = QLineEdit()
        self.show_value_field.setReadOnly(True)
        self_layout.addWidget(self.show_value_field)
        
        # Show index field - read only
        self.show_index_field = QLineEdit()
        self.show_index_field.setReadOnly(True)
        self_layout.addWidget(self.show_index_field)

        # Show value button
        show_value_button = QPushButton("Show value")
        show_value_button.clicked.connect(self.button_clicked)
        self_layout.addWidget(show_value_button)
        
        tmp_widget = QWidget(self)
        self_layout.addWidget(tmp_widget)
        tmp_layout = QVBoxLayout(tmp_widget)        
        
        # AQFilter field
        self.ako_filter = AQFilter(tmp_widget)
#        self.ako_filter.setMinCharsToShowList(0)
        tmp_layout.addWidget(self.ako_filter)
        self.ako_filter.addItemToList("First element - plus extra text",1)
        self.ako_filter.addItemToList("Second element",2)
        self.ako_filter.addItemToList("Third element",3)
        self.ako_filter.addItemToList("Fourth element",4)
        self.ako_filter.addItemToList("Fifth element",5)
        self.ako_filter.addItemToList("Sixth element",6)
        self.ako_filter.addItemToList("Seventh element",7)
        self.ako_filter.addItemToList("Eight element",8)
        self.ako_filter.addItemToList("Nineth element",9)
        self.ako_filter.addItemToList("Tenth element",10)
        self.ako_filter.addItemToList("Eleven element",11)
        self.ako_filter.addItemToList("Twelv element",12)
        self.ako_filter.addItemToList("Thirteen element",13)
        self.ako_filter.addItemToList("Fourteen element",14)
        self.ako_filter.addItemToList("Fifteen element",15)        
      
        # --- Window ---
        self.setWindowTitle("Test AQFilter")    
        self.resize(500,200)
        self.center()
        self.show()    
        
    def button_clicked(self):
        fd = self.ako_filter
        self.show_value_field.setText(fd.getValue())
        self.show_index_field.setText(str(fd.getIndexes()))
        
    def center(self):
        """Aligns the window to middle on the screen"""
        fg=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

def main():   
    
    app = QApplication(sys.argv)
    ex = Test()
    sys.exit(app.exec_())
    
