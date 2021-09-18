"""
Lightweight QT application for converting RGB to HEX and vice versa.
You can do this more quickly, and with more options, using Google,
so I wouldn't consider this any kind of production module.

Uses the HEXABIN API- which was the main motivation for this- I needed
practice with the requests module.

You can find this API at https://hexabin.herokuapp.com/api

Made by Joseph Hansen for learning purposes,
do whatever the heck you want with it.

(Just don't steal it!)

Contact me at josephclaytonhansen@gmail.com
with any questions.

If you want to see something actually
interesting, check out my other projects
on GitHub or elsewhere: specifically
Turnroot. 

rgb_to_hex takes either an array or three elements.
hex_to_rgb takes a string.
Both have validation built in.
"""

#imports/app creation
from PyQt5.QtWidgets import QApplication
app = QApplication([])
from PyQt5.QtWidgets import *
import qtmodern.styles
import qtmodern.windows
import sys, json, os
from PyQt5.QtGui import *
from PyQt5.QtCore import *
class ProxyStyle(QProxyStyle): pass
app.setStyle(ProxyStyle('Fusion'))
import requests

#copied and pasted from my massive collection of helper subclasses
#for PyQT I've built for Turnroot
class ColorBlock(QLabel):
    def __init__(self, color, w, h, parent=None):
        super().__init__(parent)
        self.color = color
        self.pixmap = QPixmap(w,h)
        self.pixmap.fill(QColor(self.color))
        self.setPixmap(self.pixmap)

#functionality
def rgb_to_hex(r,g=None,b=None):
    if g == None and b == None:
        g = r[1]
        b = r[2]
        r = r[0]
    try:
        rgb = [r,g,b]
        hex_str = ""
        hex_arr = []
        for color in rgb:
            response = requests.get("https://hexabin.herokuapp.com/api/decimal/"+str(color)+"/convert/hex")
            h = response.json()["result"]
            if response.status_code != 200:
                h = "00"
            if len(h) == 1:
                h = "0" + h
            hex_arr.append(h)
        hex_str = "".join(hex_arr)
        return "#" + hex_str
    except Exception as e:
        return e
  
def hex_to_rgb(h):
    try:
        if h.startswith("#"):
            h = h[1:]
        h_arr = [h[0:2],h[2:4], h[4:6]]
        rgb_arr = []
        for color in h_arr:
            if color.startswith("0"):
                color = color[1]
            response = requests.get("https://hexabin.herokuapp.com/api/hex/"+str(color)+"/convert/decimal")
            h = response.json()["result"]
            if response.status_code != 200:
                h = 0
            rgb_arr.append(h)
        return rgb_arr
    except Exception as e:
        return e

#packing functionality into QMainWindow
class main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RGB/HEX")
        self.setWindowFlags(Qt.FramelessWindowHint| Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground);
        self.initUI()
    
    def initUI(self):
        self.setStyleSheet("background:rgba(130,130,130,.5);")
        #add color block, RGB fields with button, and HEX field with button
        self.content = QWidget()
        self.setStyleSheet("background:rgba(130,130,130,.5);")
        self.setCentralWidget(self.content)
        self.content_layout = QGridLayout()
        self.content.setLayout(self.content_layout)
        #I'm not typing that again if I can help it
        c = self.content_layout
        self.c_block = ColorBlock("#000000", 70, 70, self)
        c.addWidget(self.c_block,1,1,2,2)
        self.r_entry, self.g_entry, self.b_entry, self.rgb_go = QSpinBox(), QSpinBox(), QSpinBox(), QPushButton("Convert RGB")
        self.r_entry.setRange(0,255)
        self.g_entry.setRange(0,255)
        self.b_entry.setRange(0,255)
        c.addWidget(self.r_entry, 1,3,1,1)
        c.addWidget(self.g_entry, 1,4,1,1)
        c.addWidget(self.b_entry, 1,5,1,1)
        c.addWidget(self.rgb_go, 1,6,1,1)
        self.hex_entry = QLineEdit()
        c.addWidget(self.hex_entry, 2,3,1,4)
        #update colorblock color with HEX value (or RGB if convert is clicked)
        self.hex_entry.returnPressed.connect(self.colorChangeHex)
        self.hex_entry.setPlaceholderText("Hex color (press Return to convert)")
        self.rgb_go.clicked.connect(self.colorChangeRgb)
    
    def colorChangeHex(self):
        self.c_block_pixmap = QPixmap(70,70)
        #update colorblock color with HEX value
        self.update_value = self.sender().text()
        self.rgb = hex_to_rgb(self.update_value.strip())
        if len(self.rgb) == 3:
            self.r_entry.setValue(self.rgb[0])
            self.g_entry.setValue(self.rgb[1])
            self.b_entry.setValue(self.rgb[2]) 
        try:
            self.c_block_pixmap.fill(QColor(self.update_value))
        except:
            self.c_block_pixmap.fill(QColor("black"))
        self.c_block.setPixmap(self.c_block_pixmap)
    
    def colorChangeRgb(self):
        #if Convert clicked, do that
        self.rgb = [self.r_entry.value(), self.g_entry.value(), self.b_entry.value()]
        self.hex = rgb_to_hex(self.rgb)
        self.c_block_pixmap = QPixmap(70,70)
        try:
            self.c_block_pixmap.fill(QColor(self.hex))
            self.hex_entry.setText(self.hex)
        except:
            self.c_block_pixmap.fill(QColor("black"))
        self.c_block.setPixmap(self.c_block_pixmap)
        
    def center(self):
        self.setGeometry(
    QStyle.alignedRect(
        Qt.LeftToRight,
        Qt.AlignCenter,
        self.size(),
        app.desktop().availableGeometry()
        ))
        
    def keyPressEvent(self, e):
        modifiers = QApplication.keyboardModifiers()
        if e.key() == Qt.Key_Escape:
            self.close()
        if modifiers == Qt.ControlModifier:
            if e.key() == Qt.Key_Q:
                self.close()
                sys.exit()
    #thanks to https://stackoverflow.com/questions/37718329/pyqt5-draggable-frameless-window/#answer-37718648
    #for helping me get this right!
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

def Go(go):
    if go:
        window = main()
        window.show()
        window.center()
        a = app.exec_()
        
Go(1)