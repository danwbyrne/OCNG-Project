import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap, shiftgrid, cm
import numpy as np
import sys
import Grid, analysis

file_dir = "C:\\Users\\User\\Desktop\\OCNG Project\\Plots\\"

def map(data):

	array = np.asarray(data)
	gradient = ['black','blue','green','yellow','red','purple','white']
	cmap = mpl.colors.LinearSegmentedColormap.from_list('my_colormap', gradient, 256)
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

def map_test(dicts, grid_points, attr):
	gradient = ['black','blue','green','yellow','red','purple','white']
	cmap     = mpl.colors.LinearSegmentedColormap.from_list('my_colormap', gradient, 256)

	#read in the data
	dx, dy = .01, .01
	stations = []
	lats,lons,values = [],[],[]
	for data in dicts:
		lats.append(float(data['Latitude']))
		lons.append(float(data['Longitude']))
		values.append(float(data[attr]))
		new_station = Grid.Point(float(data['Longitude']),float(data['Latitude']))
		new_station.setAttr('surface salinity',float(data[attr]))
		stations.append(new_station)

	#calculate min/max of lat/lon for boundary points.
	max_lat,min_lat = max(lats),min(lats)
	max_lon,min_lon = max(lons),min(lons)

	fig = pyplot.figure(figsize=(10,10))

	#create the basemap using max-min lat/lon data from input data.
	m = Basemap(llcrnrlon=int(min_lon), llcrnrlat=int(min_lat)+.5,
				urcrnrlon=int(max_lon)+.5, urcrnrlat=int(max_lat)+.5,
				resolution = 'l')

	print "Corners: ",m.xmax, m.xmin, m.ymax, m.ymin, '\n'
	
	#create a mesh grid over the map.
	y,x = np.mgrid[slice(m.ymin, m.ymax+dy, dy),
				   slice(m.xmin, m.xmax+dx, dx)]

	#create points with this grid to do Barnes Interpolation.
	points = []
	for j in range(int((m.ymax-m.ymin)/dy)+1):
		row = []
		for i in range(int((m.xmax-m.xmin)/dx)+1):
			x_mid = (x[j][i] + x[j][i+1])/2.
			y_mid = (y[j][i] + y[j+1][i])/2.
			new_point = Grid.Point(x_mid, y_mid)
			row.append(new_point)
		points.append(row)

	grid = Grid.Grid(points, stations)
	print len(grid.getStations())
	z = analysis.Barnes(grid, 'surface salinity', 5, .6)
	z = np.asarray(z)
	z_min, z_max = np.abs(z).min(), np.abs(z).max()
	print z_min, z_max
	
	
	m.pcolormesh(x, y, z, latlon=True, cmap=cmap)
	#pyplot.imshow(z, cmap=cmap, vmin=z_min, vmax=z_max,
    #       extent=[x.min(), x.max(), y.min(), y.max()],
    #       interpolation='nearest', origin='upper')

	pyplot.colorbar(cmap=cmap)
	
	x_stat, y_stat = m(lons, lats)
	m.scatter(x_stat,y_stat,3,marker='o', color='k', latlon=True)
	#draw the coastline and fill it in with a color.
	m.drawcoastlines()
	m.fillcontinents(color='0.8')

	#draw the parallel and meridian lines.
	parallels = np.arange(int(min_lat - 1),int(max_lat + 1) ,1)
	meridians = np.arange(int(min_lon - 1),int(max_lon + 1) ,1)
	m.drawparallels(parallels, labels=[True, False, False, False])
	m.drawmeridians(meridians, labels=[False, False, True, False])


	pyplot.show()