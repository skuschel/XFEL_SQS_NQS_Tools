#import sqs_nqs_tools.helper
import numpy as np
import pyqtgraph as pg

def plotImBuffer(buf, views):
	'''
	plot all the images in a buffer into a list of views
	'''
	for i in range(len(buf)):
		views[i].setImage(buf[i])		

def makeImageBufferPlots(length):
	'''
	creates a figure with subplots, ready to display a buffer full of images
	this does not give you the color bars. Good luck adding them
	remeber to keep the fig output in memory, or it closes
	Input:
		length of buffer
	Output:
		list of imageItems, the graphicsWindow
	'''
	fig = pg.GraphicsWindow()
	views = []
	fakeimgdata  = np.random.rand(100,100)
	for i in range(length):
		views.append(pg.ImageItem())
		v = fig.addViewBox(row = 0, col = i)
		v.addItem(views[-1])
		views[-1].setImage(fakeimgdata)
	return views, fig
