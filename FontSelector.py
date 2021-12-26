import sys

import cv2
import numpy as np
import json
import re

from PIL import Image 

from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, \
    QDialog, QScrollArea, QCheckBox, QHBoxLayout, QFrame, QTabWidget, QPushButton, QToolButton, \
    QSizePolicy, QLineEdit, QStyle
from PyQt5.QtGui import QFontDatabase, QFont, QColor, QPalette, QPainter, QPen
from PyQt5.QtCore import QRect, Qt, QEvent, QSettings

class SearchBox(QFrame):
    def __init__(self, app):
        QWidget.__init__(self)
       
        layout = QHBoxLayout()

        self.setStyleSheet('background-color: rgb(250,250,250)')  

        self.b = QPushButton()
        self.b.setParent(self)
        self.b.clicked.connect(lambda x: app.setShowSearch(False))

        pixmapi = getattr(QStyle, 'SP_TitleBarCloseButton')
        icon = self.style().standardIcon(pixmapi)
        self.b.setIcon(icon)

        self.l = QLabel()
        self.l.setFont(QFont("Arial Black", pointSize=14))
        self.l.setText("Search: ")
        self.l.setParent(self)

        self.editBox = QLineEdit()
        self.editBox.setFont(QFont("Arial Black", pointSize=12))

        self.setLayout(layout)
        layout.addWidget(self.b)
        layout.addWidget(self.l)
        layout.addWidget(self.editBox)

        self.setFrameStyle(QFrame.Panel)
        self.editBox.textChanged.connect(app.applySearch)

    def grabFocus(self):
        self.editBox.setFocusPolicy(Qt.StrongFocus)
        self.editBox.setFocus(Qt.OtherFocusReason)

    def clear(self):
        self.editBox.setText("")


class FontHoverCard(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.l = QLabel()
        self.l.setFont(QFont("Arial Black", pointSize=14))
        self.l.setParent(self)

    def setFontName(self, n):
        self.l.setText(n)
        self.l.adjustSize()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setOpacity(0.4)
        painter.setBrush(Qt.blue)
        painter.setPen(QPen(QColor(134, 173, 255)))
        painter.drawRect(self.rect())

class SetPhraseDialog(QDialog):
    def __init__(self, app):
        super(SetPhraseDialog, self).__init__()

        uic.loadUi('Dialog-SetPhrase.ui', self)
        self.app = app

        self.phrase.setText(self.app.getPhrase())

    def accept(self):
        self.app.setPhrase(self.phrase.text())
        self.close()

class AddCategoryDialog(QDialog):
    def __init__(self, app):
        super(AddCategoryDialog, self).__init__()

        uic.loadUi('Dialog-AddCategory.ui', self)
        self.app = app

    def accept(self):
        if self.category.text() != "":
            self.app.addCategory(self.category.text())

        self.close()

class RemoveCategoryDialog(QDialog):
    def __init__(self, app):
        super(RemoveCategoryDialog, self).__init__()

        uic.loadUi('Dialog-RemoveCurrentCategory.ui', self)
        self.app = app

    def accept(self):
        self.app.removeCurrentCategory()
        self.close()


class FontItem(QFrame):
    def __init__(self, family, app):
        super(FontItem, self).__init__()

        self.family = family
        self.app = app
        self._build()

    def _build(self):
        self.l = QLabel()
        self.l.setText(self.family)
        self.l.setFont(QFont(self.family, pointSize=40))
        self.l.setToolTip(self.family)
        self.l.installEventFilter(self)

        self.isSelected = False

        layout = QHBoxLayout()
        layout.addWidget(self.l,99)

        self.setFrameStyle(QFrame.Panel)

        self.setLayout(layout)

    def setText(self, text):
        self.l.setText(text)

    def eventFilter(self, o, event):
        if event.type() == QEvent.Enter:
            self.app.hoverCard.setFontName(self.family)
            return True
        elif event.type() == QEvent.Leave:
            self.app.hoverCard.setFontName("")
            return True
        return False

    def mousePressEvent(self, e):
        print (f"Mouse event: {e}")
        self.setSelected(not self.isSelected)
        print (f"Done calling setSelected")
        e.accept()

    def setColor(self, color):
        pal = self.palette()
        pal.setColor(QPalette.WindowText, color)
        self.setPalette(pal)

    def setSelected(self, isSelected):
        self.isSelected = isSelected
        if self.isSelected:
            self.setLineWidth(3)
            self.setFrameStyle(QFrame.Panel | QFrame.Raised)
            self.setColor(color=QColor("green"))
        else:
            self.setLineWidth(1)
            self.setFrameStyle(QFrame.Panel | QFrame.Plain)
            self.setColor(color=QColor("black"))

class FontListWidget(QScrollArea):
    def __init__(self, fontItems, evalVisible):
        super(FontListWidget, self).__init__()

        self.fontItems = fontItems
        self.evalVisible = evalVisible

        self.vbox = QVBoxLayout()       # The Vertical Box that contains the Font Items 
        self.widget = QWidget()
        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.setWidget(self.widget)
        self.subList = []

    def count(self):
        return self.vbox.count()

    def refresh(self):
        # Remove all the existing items
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        # Add in just the ones that were given to me
        for t in self.fontItems:
            if self.evalVisible(t):
                self.vbox.addWidget(t)
    
    def setFontListItems(self, f):
        self.fontItems = f
        self.refresh()


class FontTabClassified(QWidget):
    def __init__(self, app, fontItems, name, spec):
        super(FontTabClassified, self).__init__()

        self.fontItems = fontItems
        self.name = name
        self.spec = spec
        self.app = app
        self.unclassifiedFontListWidget = None

        self.layout = QVBoxLayout(self)
        
        # Initialize three tabs for the 3 different classes for this classification
        self.tabs = QTabWidget()
        self.tabs.resize(300,200)

        # Create Unclassified Tab, but only if there are some fonts not yet classified
        unclassified = list(filter(lambda x: x.family not in self.spec, fontItems))
        if len(unclassified):
            self.tabUnclassified = QWidget()
            self.tabs.addTab(self.tabUnclassified,"Unclassified")
            self.tabUnclassified.layout = QVBoxLayout()

            self.unclassifiedFontItems = []
            for x in unclassified:
                self.unclassifiedFontItems.append(FontItem(x.family, self.app))

            self.unclassifiedFontListWidget = FontListWidget(self.unclassifiedFontItems, lambda x: x.family not in self.spec)
            self.tabUnclassified.layout.addWidget(self.unclassifiedFontListWidget)

            self.addClassificationsButton = QPushButton()
            self.addClassificationsButton.setText("Add only selected Classifications")
            self.addClassificationsButton.clicked.connect(self.updateClassifications)
            self.tabUnclassified.layout.addWidget(self.addClassificationsButton)
            self.tabUnclassified.setLayout(self.tabUnclassified.layout)

        # Create In tab
        self.tabIn = QWidget()
        self.tabs.addTab(self.tabIn,"In")
        self.tabIn.layout = QVBoxLayout()
        self.fontListWidget = FontListWidget(fontItems, lambda x: self.isIn(x))
        self.tabIn.layout.addWidget(self.fontListWidget)
        self.removeSelectedClassifications = QPushButton()
        self.removeSelectedClassifications.setText("Remove selected Classifications")
        self.removeSelectedClassifications.clicked.connect(self.removeSelected)
        self.tabIn.layout.addWidget(self.removeSelectedClassifications)
        self.tabIn.setLayout(self.tabIn.layout)

        # Create Out tab
        self.tabOut = QWidget()
        self.tabs.addTab(self.tabOut,"Out")
        self.tabOut.layout = QVBoxLayout()
        self.removedFontListWidget = FontListWidget(fontItems, lambda x: not self.isIn(x))
        self.tabOut.layout.addWidget(self.removedFontListWidget)
        self.addBackInClassificationsButton = QPushButton()
        self.addBackInClassificationsButton.setText("Add Selected Classifications")
        self.addBackInClassificationsButton.clicked.connect(self.addBackIn)
        self.tabOut.layout.addWidget(self.addBackInClassificationsButton)
        self.tabOut.setLayout(self.tabOut.layout)


        # Add tabs to myself
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.refresh()


    def addBackIn(self):
        for x in self.fontItems:
            if x.isSelected:
                self.spec[x.family] = "True"

        self.app.classifications[self.name] = self.spec
        self.app._save()
        self.refresh()


    def removeSelected(self):
        for x in self.fontItems:
            if x.isSelected:
                self.spec[x.family] = "False"

        self.app.classifications[self.name] = self.spec
        self.app._save()
        self.refresh()


    def updateClassifications(self):
        for x in self.unclassifiedFontItems:
            if x.isSelected:
                self.spec[x.family] = "True"
            else:
                self.spec[x.family] = "False"

        self.unclassifiedFontListWidget.setParent(None)
        self.addClassificationsButton.setParent(None)
        self.app.classifications[self.name] = self.spec
        self.app._save()

        self.refresh()

    def isIn(self, item):
        if item.family in self.spec:
            v = self.spec[item.family]
            if v == "True":
                return True
        return False

    def refresh(self):
        if self.unclassifiedFontListWidget:
            self.unclassifiedFontListWidget.refresh()

        self.fontListWidget.refresh()
        self.removedFontListWidget.refresh()


class FontTabWidget(QWidget):
    def __init__(self, app, fontItems):
        super(FontTabWidget, self).__init__()

        self.fontItems = fontItems
        self.app = app

        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabAll = QWidget()
        self.tabSelected = QWidget()
        self.tabs.resize(300,200)

        # Add tabs
        self.tabs.addTab(self.tabAll,"All")
        self.tabs.addTab(self.tabSelected,"Selected")
        
        # Create first tab
        self.tabAll.layout = QVBoxLayout()
        self.tabAllFontListWidget = FontListWidget(fontItems, lambda x: True)
        self.tabAll.layout.addWidget(self.tabAllFontListWidget)
        self.tabAll.setLayout(self.tabAll.layout)

        # Create second tab
        self.tabSelected.layout = QVBoxLayout()
        self.tabSelectedFontListWidget = FontListWidget(fontItems, lambda x: x.isSelected)
        self.tabSelected.layout.addWidget(self.tabSelectedFontListWidget)
        self.tabSelected.setLayout(self.tabSelected.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.tabAllFontListWidget.refresh()
        self.tabSelectedFontListWidget.refresh()

        self.tabs.currentChanged.connect(self.tabItemSelected)

        self.classified = []

    def createNewClassifierTab(self, classificationName, classes):
        newClassification = FontTabClassified(self.app, self.fontItems, classificationName, classes)

        self.classified.append(newClassification)
        self.tabs.addTab(newClassification, classificationName)

    def removeCurrentCategory(self):
        which = self.tabs.currentIndex()

        if which == 0 or which == 1:
            print ("You cannot remove one of the standard categories")
            return

        print(f"Going to remove {which} tab out of {self.tabs.count()}")

        c = self.classified[which-2]

        self.app.removeCategory(c.name)
        self.classified.remove(c)
        c.setParent(None)

    def showOnlyTheseFontListItemsInAllFontList(self, l):
        self.tabAllFontListWidget.setFontListItems(l)
        
    def tabItemSelected(self, which):
        # Anytime someone switches the topmost tabs the search box will be hidden
        if which == 0:
            self.tabAllFontListWidget.refresh()
        else:
            self.app.setShowSearch(False)
            if which == 1:
                self.tabSelectedFontListWidget.refresh()
            else:
                self.classified[which-2].refresh()
    
    def showSelected(self):
        self.tabs.setCurrentIndex(1)

    def showAll(self):
        self.tabs.setCurrentIndex(0)

    def showLast(self):
        self.tabs.setCurrentIndex(self.tabs.count()-1)


class FontSelectorApp(QMainWindow):
    def __init__(self):
        super(FontSelectorApp, self).__init__()
        uic.loadUi('FontSelector.ui', self)

        self.actionSetPhrase.triggered.connect(self.setPhraseClicked)
        self.actionAddCategory.triggered.connect(self.addCategoryClicked)
        self.actionRemoveCurrentCategory.triggered.connect(self.removeCategoryClicked)
        self.actionExit.triggered.connect(self.close)
        self.actionSearch.triggered.connect(lambda x: self.setShowSearch(True))
        self.setWindowTitle("Font Selector")

        self.fontItems = []

        self._loadSettings()
        self._load()
        self._buildSearchBox()
        self._buildDisplay()
        self._buildHovercard()

        self.searchBox.raise_()
        self.setPhrase("This is a test")

        # Initial size and position
        self.resize(self.settings.value("size", QtCore.QSize(1024, 800)))
        self.move(self.settings.value("pos", QtCore.QPoint(50, 50)))

    def _loadSettings(self):
        self.settings = QSettings(QSettings.IniFormat, QSettings.SystemScope, 
                'FontSelector', '__settings')
        self.settings.setFallbacksEnabled(False)

    def closeEvent(self, event):
        print("Received close event")
        self.hoverCard.close()

        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())

    def _buildHovercard(self):
        g = self.geometry()
        self.hoverCard = FontHoverCard()
        self.hoverCard.setParent(self)
        self.hoverCard.setGeometry(QRect(g.width()-400,22,350,27))
        self.hoverCard.show()

    def _buildSearchBox(self):
        self.showSearch = False
        g = self.geometry()
        self.searchBox = SearchBox(self)
        self.searchBox.setParent(self)
        self.searchBox.setGeometry(QRect(g.width()-600,53,555,65))
        self.searchBox.setHidden(not self.showSearch)
    
    def addCategoryClicked(self):
        dlg = AddCategoryDialog(self)
        dlg.exec()

    def removeCategoryClicked(self):
        dlg = RemoveCategoryDialog(self)
        dlg.exec()

    def setPhraseClicked(self):
        dlg = SetPhraseDialog(self)
        dlg.exec()

    def getPhrase(self):
        return self.phraseText

    def setPhrase(self, text):
        self.phraseText = text
        for t in self.fontItems:
            t.setText(text)

    def applySearch(self, text):
        # Find the subset of the font items
        fontItemsToDisplay = []
        for t in self.fontItems:
            if re.search(text, t.family, re.IGNORECASE):
                fontItemsToDisplay.append(t)
        self.fontTabWidget.showOnlyTheseFontListItemsInAllFontList(fontItemsToDisplay)
        

    def addCategory(self, name):
        self.classifications[name] = dict()
        self.fontTabWidget.createNewClassifierTab(name, self.classifications[name])
        self.fontTabWidget.showLast()

    def keyPressEvent(self, event):
        k = event.key()
        if k == QtCore.Qt.Key_Q:
            self.close()
        elif k == QtCore.Qt.Key_Escape:
            self.setShowSearch(False)
        elif k == QtCore.Qt.Key_A:
            self.addCategoryClicked()
        elif k == QtCore.Qt.Key_R:
            self.removeCategoryClicked()
        elif k == QtCore.Qt.Key_S:
            self.setShowSearch(not self.showSearch)

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super().resizeEvent(a0)
        g = self.geometry()
        self.hoverCard.setGeometry(QRect(g.width()-400,22,350,27))
        self.searchBox.setGeometry(QRect(g.width()-600,53,555,65))

    def setShowSearch(self, show):
        print(f"setShowSearch - onEnter; current showSearch: {self.showSearch}, newValue: {show}")
        self.showSearch = show 
        self.searchBox.setHidden(not self.showSearch)
        if self.showSearch:
            self.searchBox.grabFocus()
            self.fontTabWidget.showOnlyTheseFontListItemsInAllFontList(self.fontItems)
        else:
            self.searchBox.clear()
            self.fontTabWidget.showOnlyTheseFontListItemsInAllFontList(self.fontItems)

    def removeCurrentCategory(self):
        self.fontTabWidget.removeCurrentCategory()

    def removeCategory(self, name):
        del self.classifications[name]
        self._save()

    def _buildDisplay(self):
        self.fontItems = []

        numberCreated = 0

        database = QFontDatabase()
        for family in database.families():
            fontItem = FontItem(family, self)

            self.fontItems.append(fontItem)
            numberCreated += 1

        print(f"Created {numberCreated} options.")

        self.fontTabWidget = FontTabWidget(self, self.fontItems)
        self.setCentralWidget(self.fontTabWidget)

        for x in self.classifications.keys():
            self.fontTabWidget.createNewClassifierTab(x, self.classifications[x])

        # It shouldn't be necessary to call showSelected then showAll here.  The default
        # behavior should be to show the first tab but PyQT has a bug where if you have 
        # a tab that itself contains any tabs (even if it isn't the tab being shown) then
        # the first tab will not draw anything.
        self.fontTabWidget.showSelected()
        self.fontTabWidget.showAll()
        
    def _load(self):
        try:
            with open('classifications.json', 'r') as f:
                print ("Loading up classifications.json")
                self.classifications = json.load(f)
        except Exception:
            print ("Failure in loading the classifications.json")
            self.classifications = dict()

    def _save(self):
        with open('classifications.json', 'w') as f:
            data = json.dump(self.classifications, f)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    fontSelectorApp = FontSelectorApp()
    fontSelectorApp.show()

    sys.exit(app.exec_())
