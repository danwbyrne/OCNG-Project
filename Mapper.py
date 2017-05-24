#Daniel Byrne, danwbyrne@gmail.com
#TAMU Glider Map Project

import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap, shiftgrid, cm
import numpy as np
import analysis

plot_dir = "Plots\\"

def objectiveMap(bounds, x, y, values, colormap, station_locs=[], title='', cbar_label='', show=True, save_name=None):
	'''input: at least (location bounds, x-locations, y-locations, values and a colormap)
	output: plots the data to a Basemap image and displays it.
    additional display settings can be set, also providing station_locs
    displays a marker at every location we used to generate our values'''

	cmap     = colormap
	cmap.set_bad(color = 'white', alpha=1.) #set up our cmap to hide masked values

	values   = np.ma.array(values, mask=np.isnan(values)) #mask our bad data

	fig = pyplot.figure(figsize=(12,12)) #setup our figure
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


def plotSemivar(stations, model, max_range, bw, linear=False, show=True, title=None, mlabel=""):
	'''input: at least (stations, chosen model, max_range, lag bandwidth)
	output: given input station data and a model we want to try this function
	calculates our datas semivariance, finds an optimized model, displays it 
	and returns the optimized model as a function of distance'''

	xs, ys, alpha = analysis.semivariogram(stations, model, bw)
	print 'model alpha chosen: %s' % alpha 
	if linear:
		funct = analysis.makeLinear(xs, ys) #see documentation
	else:
		funct = analysis.reduceModel(model, alpha, ys[-1]) #reduce our 3-input model to a 1-input

	#calculate what our model looks like
	optxs = range(int(max_range)+1)
	optys = [funct(x) for x in optxs]

	if show:
		fig = pyplot.figure(figsize=(8,8))
		pyplot.plot(xs, ys, '.', label="Raw Semivariance")
		pyplot.plot(optxs, optys, '-',linewidth=3, label=mlabel)

		pyplot.xlabel("Distance (km)")
		pyplot.ylabel("Semivariance(h)")
		if title: pyplot.title(title)
		pyplot.grid(True)
		pyplot.legend(loc=4)

		pyplot.show()

	#Parser.saveData(xs, ys)  #see documentation for when this is useful

	return funct   

def plotHistogram(stations, num_bins, xlabel=None, title=None):
	'''input: at least (stations, num_bins)
	output: this function simple plots a histogram of given data'''
	
	n, bins, patches = pyplot.hist(stations.valueArray(), num_bins, normed=True)
	pyplot.ylabel("# Of Data In Bin")
	if xlabel: pyplot.xlabel(xlabel)
	if title: pyplot.title(title)
	pyplot.grid(True)
	pyplot.show()
