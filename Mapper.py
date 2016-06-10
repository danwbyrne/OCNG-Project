import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys

file_dir = "C:\\Users\\User\\Desktop\\OCNG Project\\Plots\\"

def map(data):

	array = np.asarray(data)

	cmap = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',
														['white','pink','red','purple','blue'],
														256)
	bounds = [0,3,6,9]
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
	img = pyplot.imshow(array, interpolation='nearest',
						 cmap = cmap, origin='lower')

	pyplot.colorbar(img, cmap=cmap)
	pyplot.show()

def multiPlot(data_list, titles, pdf_name):
	pp       = PdfPages(file_dir + pdf_name)
	gradient = ['black','blue','green','yellow','red','purple','white']
	cmap     = mpl.colors.LinearSegmentedColormap.from_list('my_colormap', gradient, 256)
	bounds = [0,3,6,9]
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

	for i in range(len(data_list)):
		array = np.asarray(data_list[i])

		img = pyplot.imshow(array, interpolation='nearest',
							 cmap = cmap, origin='lower')

		pyplot.colorbar(img, cmap=cmap)
		colorbar = True

		pyplot.title((titles[i]))
			
		pyplot.savefig(pp, format='pdf')
		pyplot.clf()

	pp.close()