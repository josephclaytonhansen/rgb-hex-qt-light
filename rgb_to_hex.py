"""
Lightweight QT application for converting RGB to HEX and vice versa.
You can do this more quickly, and with more options, using Google,
so I wouldn't consider this any kind of production module.

This was using the HEXABIN API, which stopped working on 9/25/21, so
I've switched over fully to The Color API.

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
        p = ",".join([str(r), str(g), str(b)])
        response = requests.get("https://www.thecolorapi.com/id?", params = {"rgb":p})
        h = response.json()
        return h["hex"]["value"]
    except Exception as e:
        print(e)
  
def hex_to_rgb(h):
    try:
        if h.startswith("#"):
            h = h[1:]
        response = requests.get("https://www.thecolorapi.com/id?", params = {"hex":h})
        h = response.json()
        return [h["rgb"]["r"], h["rgb"]["g"],h["rgb"]["b"]]
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
        self.setStyleSheet("background:rgba(180,180,180,.4);")
        #add color block, RGB fields with button, and HEX field with button
        self.content = QWidget()
        self.setCentralWidget(self.content)
        self.content_layout = QGridLayout()
        self.content.setLayout(self.content_layout)
        #I'm not typing that again if I can help it
        c = self.content_layout
        self.c_block = ColorBlock("#000000", 80, 80, self)
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
        c.addWidget(self.hex_entry, 2,3,1,3)
        #update colorblock color with HEX value (or RGB if convert is clicked)
        self.hex_entry.returnPressed.connect(self.colorChangeHex)
        self.hex_entry.setPlaceholderText("Hex color")
        self.rgb_go.clicked.connect(self.colorChangeRgb)
        #color name, shades, and scheme
        self.color_name = QPushButton()
        self.color_name.clicked.connect(self.closestNamedHex)
        c.addWidget(self.color_name, 2,6,1,1)
    
    def colorChangeHex(self):
        self.c_block_pixmap = QPixmap(80,80)
        #update colorblock color with HEX value
        self.update_value = self.hex_entry.text()
        print("update value:"+self.update_value)
        self.rgb = hex_to_rgb(self.update_value.strip())
        if len(self.rgb) == 3:
            self.r_entry.setValue(self.rgb[0])
            self.g_entry.setValue(self.rgb[1])
            self.b_entry.setValue(self.rgb[2]) 
        try:
            if self.update_value.startswith("#") == False:
                self.update_value = "#" + self.update_value
            self.c_block_pixmap.fill(QColor(self.update_value))
            self.updateName()
        except:
            self.c_block_pixmap.fill(QColor("black"))
        self.c_block.setPixmap(self.c_block_pixmap)
        self.hex = self.update_value
        self.updateName()
    
    def colorChangeRgb(self):
        #if Convert clicked, do that
        self.rgb = [self.r_entry.value(), self.g_entry.value(), self.b_entry.value()]
        self.hex = rgb_to_hex(self.rgb)
        self.c_block_pixmap = QPixmap(80,80)
        try:
            self.c_block_pixmap.fill(QColor(self.hex))
            self.hex_entry.setText(self.hex)
            self.updateName()
        except Exception as e:
            print(e)
            self.c_block_pixmap.fill(QColor("black"))
        self.c_block.setPixmap(self.c_block_pixmap)
        self.updateName()
    
    def updateName(self):
        if hasattr(self, "hex"):
            response = requests.get("https://www.thecolorapi.com/id?", params = {"hex":self.hex}).json()
            self.relevant_values = {"name":response["name"]["value"],
                                    "cnh":response["name"]["closest_named_hex"],
                                    "distance":response["name"]["distance"],
                                    "contrast":response["contrast"]["value"]}
            self.color_name.setStyleSheet("background:"+self.hex+";"+"color:"+self.relevant_values["contrast"])
            self.color_name.setText(self.relevant_values["name"] + " ~"+str(self.relevant_values["distance"]))
    
    def closestNamedHex(self):
        self.hex_entry.setText(self.relevant_values["cnh"])
        
        self.colorChangeHex()
    
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
