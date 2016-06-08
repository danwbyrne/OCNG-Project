import matplotlib as mpl
from matplotlib import pyplot
import numpy as np
import sys

def map(data):
	array = np.asarray(data)

	cmap = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',
														['blue','yellow','green'],
														256)
	bounds = [0,3,6,9]
	norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

	img = pyplot.imshow(array, interpolation='nearest',
						 cmap = cmap, origin='lower')

	pyplot.colorbar(img, cmap=cmap)

	pyplot.show()

