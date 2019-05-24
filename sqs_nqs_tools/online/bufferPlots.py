#import sqs_nqs_tools.helper
import numpy as np
import pyqtgraph as pg

class ImBufferPlotter():
    def __init__(self, length):
        '''
        creates a figure with subplots, ready to display a buffer full of images
        this does not give you the color bars. Good luck adding them
        
        remember to keep the fig output in memory, or it closes
        
        Input:
            length of buffer
        Output:
            list of imageItems, the graphicsWindow
        '''
        self.fig = pg.GraphicsWindow()
        self.views = []
        for i in range(length):
            fakeimgdata  = np.random.rand(100,100)
            self.views.append(pg.ImageItem())
            v = self.fig.addViewBox(row = 0, col = i)
            v.addItem(self.views[-1])
            self.views[-1].setImage(fakeimgdata)

    def plotImBuffer(self, buf):
        '''
        plot all the images in a buffer into this figure
        '''
        for v,b in zip(self.views, buf):
            v.setImage(b)		

