#!/usr/bin/env python3

#plotting
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

#else
import sys

#sqs
import sqs_nqs_tools.online as online
import sqs_nqs_tools as tools

class App(QWidget):
    
    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 500
        self.source='tcp://10.253.0.142:6666'
        # UI
        self.initUI()
        
    def initUI(self):
        self.setGeometry(self.left,self.top,self.width,self.height)
        
        # create Layout Elements
        self.data_Figure = plt.figure()
        self.data_Figure_Ax = self.data_Figure.add_subplot(111)
        self.data_Canvas = FigureCanvas(self.data_Figure)
        
        # create Layout
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # add elements to layout
        grid.addWidget(self.data_Canvas,1,0)
        
        # add layout to application
        self.setLayout(grid)
        self.show()
        
    def refreshPlot(self, data):
        self.data_Figure_Ax.cla()
        self.data_Figure_Ax.plot(data, '-')
        self.data_Canvas.draw()
        
## create app instance
app = QApplication([])
app.setStyle('Fusion')
ex = App()

sys.exit(app.exec_())   
