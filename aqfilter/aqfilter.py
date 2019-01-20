import sys
import time 

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDockWidget

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QDesktopWidget

from PyQt5 import Qt

from PyQt5.QtCore import QItemSelection
from PyQt5.QtCore import QEvent

from PyQt5.QtCore import QRect
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QAbstractItemView

# ##################
#
# AkoFilter 
#
# ##################
class AQFilter(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(0)
        self.setLayout(self_layout)

        self.parent = parent
        self.main_window = self.get_main_window()
        
        self.value = ""
        self.index = None
        
        self.list = []
        
        # Input field Widget
        self.input_widget = FieldWidget(self)
        self.input_widget.setText(self.value)
        self_layout.addWidget(self.input_widget)
        
        # List Widget
        self.list_widget = ListWidget(self)
        self.list_widget.setHidden(True)

        QApplication.instance().installEventFilter(self)
        
        self.input_widget.textChanged.connect(self.show_list)
      
    def setSelectedValueIndex(self, value, index):
        """Set the value-index by the selected element from the list"""
        self.setTypedValueIndex(value, index)
        self.input_widget.setText(value)
        
    def setTypedValueIndex(self, value, index=None):
        """Set the value-index by the typed key"""
        self.value = value
        self.index = index
      
    def addItemToList(self, value, index):
        """Add value-index pair to the  list"""
        self.list.append((value,index))

    def hide_list(self):
        """Hide the list"""
        self.list_widget.setHidden(True)      
      
    def show_list(self):
        """
        When Key Pressed then this method is called.
        -The typed value is saved in the in the widget
        -Show the dropdown list
        -Show only the elements which fit to the typed value
        """   
        
        self.setTypedValueIndex(self.input_widget.text())
       
        self.reposition_list()
        self.list_widget.setHidden(False)
        self.list_widget.clear()
        for i in self.list:
            if self.input_widget.text().lower() in i[0].lower():            
                item=QListWidgetItem()            
                item.setText(i[0])
                item.setData(Qt.UserRole, i[1])
                self.list_widget.addItem(item)                        

        self.setWindowState(Qt.WindowActive)
        self.activateWindow()

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

    def reposition_list(self):
        """Re-position the list to the Input Widget"""
        def get(widget, x=0, y=0):
            x = x + widget.geometry().x()
            y = y + widget.geometry().y()
            parent = widget.parentWidget()        
            if parent:
                (x,y) = get(parent, x, y)
            return (x, y)      
        
        pos = get(self.input_widget)
        self.list_widget.move(pos[0], pos[1] + self.input_widget.geometry().height())

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Escape:
#            self.list_widget.setHidden(True)
#        event.ignore()
        
    def resizeEvent(self, event):
        self.reposition_list()
        event.ignore()
  
    def eventFilter(self, obj, event):
        
        # Close window
        if event.type() == QEvent.Close and obj is self.main_window: # type(self).__name__ == 
            self.list_widget.setHidden(True)
            self.list_widget.close()

            event.accept()
            return True
        
        # Focus-in Input Widget
        elif event.type() == QEvent.FocusIn and obj is self.input_widget:
            FocusWatchDog.getInstance().stop()
            #print('focus-in-input')
        
        # Focus-out Input Widget
        elif event.type() == QEvent.FocusOut and obj is self.input_widget: 
            wd = FocusWatchDog.getInstance()
            if not wd.isRunning():
                wd.timeOver.connect(self.hide_list)
                wd.start()
            #print('focus-out-input')

        # Focus-in List Widget
        elif event.type() == QEvent.FocusIn and obj is self.list_widget: 
            #print('focus-in-list')
            FocusWatchDog.getInstance().stop()

        ## Focus-out List Widget
        #elif event.type() == QEvent.FocusOut and obj is self.list_widget: 
        #    #print('focus-out-list')
        #    pass

        # Main Window moved
        elif event.type() == QEvent.Move and obj is self.main_window:
            self.reposition_list()

        # Escape Key Pressed
        elif event.type() == QEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.hide_list()

#        # Key Pressed on Input Widget
#        elif event.type() == QEvent.KeyPress and obj is self.input_widget:            
#            self.show_list()
            
        #print('event', obj, self.parent, event.type())

        return super(AQFilter, self).eventFilter(obj, event)

  
# ##################
#
# Input Field Widget
#
# #################
class FieldWidget(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

#    def focusInEvent(self, event):
#        super(FieldWidget, self).focusInEvent(event)
#        FocusWatchDog.getInstance().stop()
#        
#    def focusOutEvent(self, event):
#        super(FieldWidget, self).focusOutEvent(event)
#        wd = FocusWatchDog.getInstance()
#        if not wd.isRunning():
#            wd.timeOver.connect(self.parent.hide_list)
#            wd.start()


# ######################
#
# List
#
# ######################
class ListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__(None)
        self.parent = parent
        
        self.setWindowFlags( Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint )        
        self.setObjectName("listWidget")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:    
            #self.setSelectionMode(QAbstractItemView.SingleSelection)
            index = self.indexAt(event.pos())
            if not index.isValid():
                return
            
            ci = self.currentIndex()
            sm = self.selectionModel()
            sm.setCurrentIndex(index, sm.NoUpdate | sm.ClearAndSelect)
            
#            if not ci.isValid():
#                return
#            if not sm.hasSelection():
#                sm.select(index, sm.ClearAndSelect)
#                return
#            cr = ci.row()
#            tgt = index.row()
#            top = self.model().index(min(cr, tgt), 0)
#            bottom = self.model().index(max(cr, tgt), 0)
#            sm.select(QItemSelection(top, bottom), sm.Select)        
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            i = self.currentItem()
            if i is not None:
                self.parent.setSelectedValueIndex(i.text(), i.data(Qt.UserRole))
                self.setHidden(True)
           

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.setHidden(True)
            
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            i = self.currentItem()
            if i is not None:
                print(i.data(Qt.UserRole))

        event.ignore()

# =========================
#
# Watch Dog
#
# =========================
class FocusWatchDog(QThread):
    
    timeOver = pyqtSignal()
    __instance = None
    __run = False
    __stopped = False
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        cls.__stopped = False
        return cls.__instance    
    
    @classmethod
    def getInstance(cls):
        if not cls.__run:
            inst = cls.__new__(cls)
            cls.__init__(cls.__instance) 
            return inst
        else:
            return cls.__instance
    
    def __init__(self):
        QThread.__init__(self)
            
    def __del__(self):
        self.wait()
    
    def isRunning(self):
        return FocusWatchDog.__run
        
    def stop(self):
        if FocusWatchDog.__run:
            FocusWatchDog.__stopped = True
    
    def run(self): 
        
        # blocks to call again
        FocusWatchDog.__run = True
        for i in range(10):
            time.sleep(0.005)
            if FocusWatchDog.__stopped:
                break
        else:
            self.timeOver.emit()
        
        # release blocking
        FocusWatchDog.__run = False


        
        
    


class Test(QWidget):
    
    def __init__(self):
        QWidget.__init__(self)
                
        self_layout = QVBoxLayout(self)
        self_layout.setContentsMargins(10, 10, 10, 10)
        self_layout.setSpacing(0)
        self.setLayout(self_layout)
    
        previous_button = QPushButton("previous button")
        self_layout.addWidget(previous_button)
        
        tmp_widget = QWidget(self)
        self_layout.addWidget(tmp_widget)
        tmp_layout = QVBoxLayout(tmp_widget)
        
        
        ako_filter = AQFilter(tmp_widget)
        tmp_layout.addWidget(ako_filter)
        ako_filter.addItemToList("First element - plus extra text",1)
        ako_filter.addItemToList("Second element",2)
        ako_filter.addItemToList("Third element",3)
        ako_filter.addItemToList("Fourth element",4)
        ako_filter.addItemToList("Fifth element",5)
        ako_filter.addItemToList("Sixth element",6)
        ako_filter.addItemToList("Seventh element",7)
        
        next_button = QPushButton("next button")
        self_layout.addWidget(next_button)
      
      
        # --- Window ---
        self.setWindowTitle("Test AQFilter")    
        self.resize(500,300)
        self.center()
        self.show()    
        
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
    