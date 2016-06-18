from Grid import *
import CSVtoPoints, analysis, Mapper
import numpy as np
import time
from matplotlib.backends.backend_pdf import PdfPages

def test1():
	grid = Grid()
	grid.createPoints(100, 100)
	grid.createStations(100, "surface salinity", 500)

	analyzed_grid = Grid(analysis.Barnes(grid, "surface salinity", 5, 1, True))
	Mapper.map(analyzed_grid.getAttrList("surface salinity"))

def test2():
	grid = Grid()
	grid.createPoints(100, 100)
	grid.createStations(75, "surface salinity", 500)

	#creates 7 files (.4 <= gamma <= 1.0) each with 10 plots (1 <= alpha <= 10)
	for gamma in range(4,11):
		data_list = []
		titles    = []
		for alpha in range(1,11):
			analyzed_grid = Grid(analysis.Barnes(grid, "surface salinity", alpha, gamma*0.1, True))
			data_list.append((analyzed_grid.getAttrList("surface salinity")))
			titles.append("Interpolation with alpha = %s" % (alpha))
		Mapper.multiPlot(data_list, titles, "Gamma-%s.pdf" % (gamma))

#function for plotting CSV data from filedir to a generated map with interpolated data values.
#dn controls the distance between generated grid points, set it lower for more resolution
#be careful with how low you set it as it can eat A LOT of memory for values ~<.01
#see analysis.Barnes() function to see how alpha and gamma work
def BarnesMap(filedir, dn, attr, alpha, gamma, show=True, pdf_name=None):
	#reads in the all of the .csv files in a directory.
	dicts    = CSVtoPoints.multiRead(filedir)

	#organizing the data from the .csv data and making stations from them. points is just initialized.
	stations, lats, lons, dates = [], [], [], []
	for data in dicts:
		lat, lon, value = float(data['Latitude']), float(data['Longitude']), float(data[attr])
		date            = data['DateUTC'] + " " + data['TimeUTC']
		lats.append(lat); lons.append(lon); dates.append(date)
		stations.append(Point(lon, lat, attributes = {attr: value}))

	station_locs = [lons, lats] #so we can see where the stations are on our map

	#date conversion since NOAA decided to switch their format up halfway through
	converted_dates = []
	for date in dates:
		try:
			new_date = time.mktime(time.strptime(date, "%d-%b-%y %H:%M:%S"))
		except ValueError:
			new_date = time.mktime(time.strptime(date, "%d%b%Y %H:%M:%S"))
		converted_dates.append(new_date)
	dates = converted_dates

	#calculate the time range the data was collected in
	min_time   = time.strftime("%d-%B-%y %H:%M:%S",time.localtime(min(dates)))
	max_time   = time.strftime("%d-%B-%y %H:%M:%S",time.localtime(max(dates)))
	time_range = min_time + " to " + max_time
	
	#calculate boundary points, also applies some padding to get a nice int boundary.
	max_lon,min_lon = int(max(lons)+1),int(min(lons)-1)
	max_lat,min_lat = int(max(lats)+1),int(min(lats)-1)
	bounds          = [max_lon, min_lon, max_lat, min_lat]

	#creates a mesh grid over the boundaries size dn apart.
	y,x = np.mgrid[slice(min_lat, max_lat+dn, dn),
				   slice(min_lon, max_lon+dn, dn)]

	#create a grid of points from the created mesh for analysis. 	
	points = []
	for j in range(len(y)-1):
		row = []
		for i in range(len(y[0])-1):
			x_mid = (x[j][i] + x[j][i+1])/2.
			y_mid = (y[j][i] + y[j+1][i])/2.
			new_point = Point(x_mid, y_mid, attributes = {attr: 0.0})
			row.append(new_point)
		points.append(row)

	grid      = Grid(points, stations) #initialize the grid with points and stations.
	values    = np.asarray(analysis.Barnes(grid, attr, alpha, gamma)) #run the analysis and convert the output to a numpy array.

	#map the data
	Mapper.objectiveMap(bounds, x, y, values,
						station_locs, title="Bottom Oxygen Content From " + time_range,
						cbar_label="Oxygen mg/L", show=show, pdf_name=pdf_name)

#runs and saves multiple barnes analysis and saves them to a directory as pdfs
def multiBarnes(filedir, dn, attr, alpha, gamma_range, pdf_dir):
	for gamma in gamma_range:
		pdf_name = pdf_dir + ("OxMgL Analysis Gamma-%s" % (gamma*.1))+".pdf"
		BarnesMap(filedir, dn, attr, alpha, gamma*.1, show=False, pdf_name=pdf_name)
	

if __name__ == "__main__":
	filedir = "C:\\Users\\Daniel Byrne\\Desktop\\OCNG-Project\\CSVs\\R2-0318\\"
	BarnesMap(filedir, .01, "OxMgL", 7, .5, show=True, pdf_name="Plots\\Objective Analysis of Oxygen Content.pdf")