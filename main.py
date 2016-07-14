from Grid import *
import Parser, analysis, Mapper
import numpy as np
import time
from matplotlib.backends.backend_pdf import PdfPages

#function for plotting CSV data from filedir to a generated map with interpolated data values.
#dn controls the distance between generated grid points, set it lower for more resolution
#be careful with how low you set it as it can eat A LOT of memory for values ~<.01
#see analysis.Barnes() function to see how alpha and gamma work
def BarnesMap(filedir, dn, attr, alpha, gamma, show=True, save_name=None):
	#reads in the all of the .csv files in a directory.
	dicts    = Parser.multiReadCSV(filedir)

	#organizing the data from the .csv data and making stations from them. points is just initialized.
	stations, lats, lons, dates, depths = [], [], [], [], []
	for data in dicts:
		lat, lon, value = float(data['Latitude']), float(data['Longitude']), float(data[attr])
		date            = data['DateUTC'] + " " + data['TimeUTC']
		lats.append(lat); lons.append(lon); dates.append(date);
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
	min_time   = time.strftime("%d-%b-%y %H:%M:%S",time.localtime(min(dates)))
	max_time   = time.strftime("%d-%b-%y %H:%M:%S",time.localtime(max(dates)))
	time_range = min_time + " to " + max_time
	
	#calculate boundary points, also applies some padding to get a nice int boundary.
	max_lon,min_lon = int(max(lons)),int(min(lons)-1)
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

	values    = np.asarray(analysis.Barnes(points, stations, attr, alpha, gamma, dev_view=True)) #run the analysis and convert the output to a numpy array.
	print "Mean of stations: ", analysis.mean(stations,attr)
	print "Mean of interped: ", np.mean(values)
	print "Residual: ", analysis.mean(stations,attr) - np.mean(values)

	#map the data
	Mapper.objectiveMap(bounds, x, y, values, station_locs,
						title="Bottom Oxygen Content From " + time_range,
						cbar_label="Oxygen mg/L", show=show, save_name=save_name)




#runs and saves multiple barnes analysis and saves them to a directory as pdfs
def multiBarnes(filedir, dn, attr, alpha, gamma_range, pdf_dir):
	for gamma in gamma_range:
		save_name = pdf_dir + ("OxMgL Analysis Gamma-%s" % (gamma*.1))+".pdf"
		BarnesMap(filedir, dn, attr, alpha, gamma*.1, show=False, save_name=save_name)




#because of differences in naming conventions this will do analysis on data from TXT files
#the new depth variable defines which depth data we are using for that station.
def BarnesMapTXT(filedir, dn, attr, depth, alpha, gamma, show=True, save_name=None, title="", cbar_label="", bottom_only=False):
	#reads in the all of the .csv files in a directory.
	dicts    = Parser.multiReadTXT(filedir, bottom_only=bottom_only)

	#organizing the data from the .csv data and making stations from them. points is just initialized.
	stations, lats, lons, dates, depths = [], [], [], [], []
	if bottom_only:
		for data in dicts:
			if not (float(data[attr]) == -99.99):
				lat, lon, value = float(data['Latitude']), float(data['Longitude']), float(data[attr])
				date            = data['TimeUTC']
				lats.append(lat); lons.append(lon); dates.append(date);
				stations.append(Point(lon, lat, attributes = {attr: value}))

	else:
		for data in dicts:
			if float(data['Depth']) == depth and not (float(data[attr]) == -99.99):
				lat, lon, value = float(data['Latitude']), float(data['Longitude']), float(data[attr])
				date            = data['TimeUTC']
				lats.append(lat); lons.append(lon); dates.append(date);
				stations.append(Point(lon, lat, attributes = {attr: value}))
	station_locs = [lons, lats] #so we can see where the stations are on our map

	#date conversion
	converted_dates = []
	for date in dates:
		try:
			new_date = time.mktime(time.strptime(date, "%m-%d-%Y %H:%M"))
		except ValueError:
			new_date = time.mktime(time.strptime(date, "%m/%d/%Y %H:%M"))
		converted_dates.append(new_date)
	dates = converted_dates

	#calculate the time range the data was collected in
	min_time   = time.strftime("%d-%b-%y %H:%M",time.localtime(min(dates)))
	max_time   = time.strftime("%d-%b-%y %H:%M",time.localtime(max(dates)))
	time_range = min_time + " to " + max_time
	
	#calculate boundary points, also applies some padding to get a nice int boundary.
	max_lon,min_lon = int(max(lons)),int(min(lons)-1)
	max_lat,min_lat = int(max(lats)+1),int(min(lats))
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

	values    = np.asarray(analysis.Barnes(points, stations, attr, alpha, gamma, dev_view=True)) #run the analysis and convert the output to a numpy array.

	print "Mean of Stations:", analysis.mean(stations, attr)
	print "Mean of Interped:", np.mean(values)
	print "Residual:", analysis.mean(stations, attr)-np.mean(values)
	#map the data
	#Mapper.objectiveMap(bounds, x, y, values, station_locs,
	#					title=title + time_range,
	#					cbar_label=cbar_label, show=show, save_name=save_name)

	Parser.writeCSV(x, y, values, "csvtest.csv")

if __name__ == "__main__":

	filedir = "TXTs\\MS04\\"
	BarnesMapTXT(filedir, .01, "Salinity", 2.0, 15, .6 ,show=False,
				save_name = "Plots\\MS04 Surface Salinity Interpolation.png",
				title    = "Surface Salinity From ", cbar_label = "PSS78")

	#BarnesMapTXT(filedir, .01, "Salinity", 2.0, 15, .6 ,show=False,
	#			save_name = "Plots\\MS04 Bottom Salinity Interpolation.png",
	#			title    = "Bottom Salinity From ", cbar_label = "PSS78", bottom_only = True)

	#BarnesMapTXT(filedir, .01, "Oxygen", 0.0, 15, .6 ,show=False,
	#			save_name = "Plots\\MS04 Bottom Oxygen Content Interpolation.png",
	#			title    = "Bottom Oxygen Content From ", cbar_label = "mL/L", bottom_only = True)

	#filedir = "TXTs\\MS06\\"
	#BarnesMapTXT(filedir, .01, "Salinity", 2.0, 15, .6 ,show=False,
	#			save_name = "Plots\\MS06 Surface Salinity Interpolation.png",
	#			title    = "Surface Salinity From ", cbar_label = "PSS78")

	#BarnesMapTXT(filedir, .01, "Salinity", 2.0, 15, .6 ,show=False,
	#			save_name = "Plots\\MS06 Bottom Salinity Interpolation.png",
	#			title    = "Bottom Salinity From ", cbar_label = "PSS78", bottom_only = True)

	#BarnesMapTXT(filedir, .01, "Oxygen", 0.0, 15, .6 ,show=False,
	#			save_name = "Plots\\MS06 Bottom Oxygen Content Interpolation.png",
	#			title    = "Bottom Oxygen Content From ", cbar_label = "mL/L", bottom_only = True) 	

	#filedir = "CSVs\\R2-0318\\"
	#BarnesMap(filedir, .005, "OxMgL", 20, .6, show = False, save_name = "Plots\\NOAA Bottom Oxygen Content Interpolation.png")
