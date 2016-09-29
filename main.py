from Data import *
import Analysis, Parser
from matplotlib import pyplot
import Mapper
import time

#TODOS: finish doing save/load so you don't have to do analysis a bunch of times
#just to try new features

#2 different date conversions for the different files we are working on
#might have to make more since everyone inputs there stuff different
def convertDateCSV(date):
	try:
		new_date = time.mktime(time.strptime(date, "%d-%b-%y %H:%M:%S"))
	except ValueError:
		new_date = time.mktime(time.strptime(date, "%d%b%Y %H:%M:%S"))
	return new_date

def convertDateTXT(date):
	try:
		new_date = time.mktime(time.strptime(date, "%m-%d-%Y %H:%M"))
	except ValueError:
		new_date = time.mktime(time.strptime(date, "%m/%d/%Y %H:%M"))
	return new_date

def getStations(filedir, attr=None, depth = None, bottom_only=False):
	if attr == None:
		return Points(filename = filedir)

	#tries to parse it with csv, if its a txt it will fail this and go to the except block
	try: 
		dicts    = Parser.multiReadCSV(filedir)
		stations = Points([])

		for data in dicts:
			date = convertDateCSV(data['DateUTC'] + " " + data['TimeUTC'])
			stations.append(Point(float(data['Longitude']), float(data['Latitude']), float(data[attr]), date))

	except:
		dicts = Parser.multiReadTXT(filedir, bottom_only)
		stations = Points([])

		for data in dicts:
			if (float(data['Depth']) == depth or bottom_only) and (float(data[attr]) != -99.99):
				date = convertDateTXT(data['TimeUTC'])
				stations.append(Point(float(data['Longitude']), float(data['Latitude']), float(data[attr]), date))

	return stations

def krigAnalysis(dn, model, stations, bw=10, title="", cbar_label="", save_name=""):
	#parse files into stations
	if stations == None:
		stations = getStations(filedir, attr, depth, bottom_only)

	#uses this to mark where stations are on the map
	lons, lats   = stations.lonArray(), stations.latArray()
	station_locs = [lons, lats]

	#calculate the time range the data was collected in
	min_time   = time.strftime("%d-%b-%y %H:%M",time.localtime(np.amin(stations.timeArray())))
	max_time   = time.strftime("%d-%b-%y %H:%M",time.localtime(np.amax(stations.timeArray())))
	time_range = min_time + " to " + max_time

	#calculates the bounds for the basemap
	bounds = [int(max(lons)), int(min(lons)-1),
			  int(max(lats)+1), int(min(lats))] 

	#creates grid-values based on bounds and resolution
	yg, xg = Analysis.createGrid(bounds, dn)
	shape  = (len(yg)-1, len(yg[0])-1)

	#creates an array of blank points with locations at the center of the gridpoints
	points = Points([])
	for j in range(shape[0]):
		for i in range(shape[1]):
			x_mid = (xg[j][i] + xg[j][i+1])/2.
			y_mid = (yg[j][i] + yg[j+1][i])/2.
			points.append(Point(x_mid, y_mid))

	print points.size()

	(lags, ys, optf, alpha) = Analysis.semivariogram(stations, model, bw)

	points = Analysis.krigInterp(points, stations, model, alpha)

	Mapper.objectiveMap(bounds, xg, yg, points.valueMatrix(shape), station_locs,
						title = title + " From " + time_range, cbar_label = cbar_label, save_name=save_name, show=False)

	return points

def test():
	filedir  = "TXTs\\MS06\\"

	settings = [ ("Salinity", "PSS78"), ("Temperature", "deg C"), ("Fluorescence", "mg/m^3"), ("Turbidity", "NTU")]

	dn    = .005
	depth = 2.0
	model = Analysis.pentaspherical

	for setting in settings:
		for bottom_only in [True, False]:

			print "running interp on %s with bottom = %s" % (setting[0], bottom_only)

			if bottom_only: save_dir = "Saves\\Bottom " + setting[0] + "\\"
			else: save_dir = "Saves\\" + setting[0] + "\\"

			title = setting[0] + " Interpolation"
			if bottom_only: title = "Bottom " + title

			cbar_label = setting[1]

			save_name = save_dir + title + ".png"
			pt_save   = save_dir + title + "points.csv"
			stat_save = save_dir + title + "stations.csv"

			stations = getStations(filedir, setting[0], depth, bottom_only)
			points   = krigAnalysis(dn, model, stations, 5, title, cbar_label, save_name)

			stations.save(stat_save)
			points.save(pt_save)

if __name__ == "__main__":
	test()
 
