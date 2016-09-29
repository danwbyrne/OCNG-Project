import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap, shiftgrid, cm
import numpy as np
import sys

plot_dir = "Plots\\"

def semiMap(model, xs, ys, c0, alpha):
	pyplot.plot(xs,ys, '.')
	aa = [alpha for i in range(len(xs))]
	cs = [c0 for i in range(len(xs))]
	zs = map(model, xs, aa, cs)
	pyplot.plot(xs, zs, '-')
	pyplot.show()

def multiPlot(data_list, titles, pdf_name):
	pp       = PdfPages(plot_dir + pdf_name)
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

#used in tangent with the BarnesMap function in main, station_locs need only be specified if
#you want a marker placed where the interpolated data is calculated from.
def objectiveMap(bounds, x, y, values, station_locs=[], title='', cbar_label='', show=True, save_name=None):
	gradient = ['red','yellow','green']
	cmap     = mpl.colors.LinearSegmentedColormap.from_list('my_colormap', gradient, 256)

	fig = pyplot.figure(figsize=(8,8))
	title = pyplot.title(title)
	title.set(y = title.get_position()[1] + .05)
	title.set(x = title.get_position()[0] - .01)

	#create the basemap using max-min lat/lon data from input data.
	m = Basemap(llcrnrlon=bounds[1], llcrnrlat=bounds[3],
				urcrnrlon=bounds[0], urcrnrlat=bounds[2],
				resolution = 'f')
	
	#apply the colormesh to the figure
	m.pcolormesh(x, y, values, latlon=True, cmap=cmap)

	#apply our color bar, cmap, to the figure
	pyplot.colorbar(cmap=cmap, label=cbar_label, pad=.05, orientation='horizontal')
	
	#place a marker at station locations if given.
	if len(station_locs) == 2:
		x_stat, y_stat = m(station_locs[0], station_locs[1])
		m.scatter(x_stat,y_stat, 15 ,marker="x", color='k', latlon=True)


	#draw the coastline and fill it in with a color.
	m.drawcoastlines()
	m.fillcontinents(color='#AD6B55')
	m.drawrivers()

	#draw the parallel and meridian lines.
	meridians = np.arange(bounds[1], bounds[0]+1 ,1)
	parallels = np.arange(bounds[3], bounds[2]+1 ,1)
	m.drawmeridians(meridians, labels=[False, False, False, True])
	m.drawparallels(parallels, labels=[True, False, False, False])

	#this way we can see the ones we want but don't have to show them if we are just saving them to a page.
	if show: pyplot.show(fig)

	#saving protocol.
	if save_name:
		pyplot.savefig(save_name, format='png')
		print "saved to:", save_name
		pyplot.clf()

def histogram(values, bins=10):
	pyplot.hist(values, bins, range=None, normed=True)
	pyplot.show()
