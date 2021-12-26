import sys

import cv2
import numpy as np
import json
import copy

from PIL import Image 

from PyQt5 import uic, QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, \
    QDialog, QScrollArea, QCheckBox, QHBoxLayout, QFrame, QTabWidget, QPushButton, QToolButton, \
    QSizePolicy 
from PyQt5.QtGui import QFontDatabase, QFont, QColor, QPalette, QPainter, QPen, QImage
from PyQt5.QtCore import QRect, Qt, QEvent, QSettings

class MyImageLabel():
    def __init__(self, family, text):
        super(MyImageLabel, self).__init__()

        self.width = 60
        self.height = 60

        self.family = family
        self.text = text
        self.font = QFont(self.family, pointSize=40)

        self._generateImage()

    def _generateImage(self):

        self.image = QImage(self.width, self.height, QImage.Format_RGB888)
        rect = QRect(0,0, self.width, self.height)

        paint = QtGui.QPainter(self.image)
        paint.begin(self.image)
        paint.fillRect(0, 0, self.width, self.height, 0)
        paint.setFont(self.font)
        paint.drawText(rect, Qt.AlignCenter, self.text)
        paint.setPen(QtGui.QPen(Qt.blue, 2, join = Qt.MiterJoin)) 
        paint.end()

    def asPyQtImage(self):
        return self.image

    def asNpArray(self):
        width = self.image.width()
        height = self.image.height()

        ptr = self.image.bits()
        ptr.setsize(self.image.byteCount())
        arr = np.asarray(ptr).reshape(height, width, 3)

        return arr


class FontTestApp(QMainWindow):
    def __init__(self):
        super(FontTestApp, self).__init__()
        uic.loadUi('FontTest.ui', self)

        self.f1.currentTextChanged.connect(lambda x: self._generateImage())
        self.f2.currentTextChanged.connect(lambda x: self._generateImage())

        self._generateImage()

    def _modifyNpImage(self, npArray):
        return cv2.blur(npArray, (10,10))

    def _setNpImage(self, l, npArray):
        image = QtGui.QImage(
                npArray.data, 
                npArray.shape[1], 
                npArray.shape[0], 
                npArray.strides[0],
                QtGui.QImage.Format_RGB888)
        l.setPixmap(QtGui.QPixmap.fromImage(image))

    def _generateImage(self):

        font1 = self.f1.currentText()
        font2 = self.f2.currentText()

        self.l1 = MyImageLabel(font1, "T")
        self.l2 = MyImageLabel(font2, "T")

        n1 = self.l1.asNpArray()
        n2 = self.l2.asNpArray()

        # result = cv2.subtract(n2,n1)
        result = cv2.absdiff(n1,n2)

        similarPixels = np.sum(result==0x000000)
        percentage = (similarPixels / (result.shape[1] * result.shape[0] * 3 )) * 100

        self._setNpImage(self.c1, n1)
        self._setNpImage(self.c2, n2)
        self._setNpImage(self.d, result)

        self.p.setText(f"{percentage:2.2f} %")
        print (f"Number of similar pixels: {similarPixels}, percentage: {percentage}")

    def closeEvent(self, event):
        print("Received close event")

    def keyPressEvent(self, event):
        k = event.key()
        if k == QtCore.Qt.Key_Q or k == QtCore.Qt.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    FontTestApp = FontTestApp()
    FontTestApp.show()

    sys.exit(app.exec_())
