import math
import numpy as np
import time

#runs a Barnes Analysis on a given grid; alpha controls radius of influence
#that a station has, gamma controls smoothness of the interpolation.
#attr specifies which attribute of the points we are analyzing.
#setting station_view = True replaces the calculated values for stations with their original values
#setting dev_view = True lets you see running time values for the analysis.
def Barnes(grid, attr, alpha, gamma, dev_view=False):
	if dev_view: start_time = time.time()
	stations = grid.getStations()
	points   = grid.getPoints()
	shape    = grid.getShape()
	alpha    = 5.052*(((2*alpha)/math.pi)**2) #falloff rate

	print "Running Barnes Analysis on:"
	print len(stations),"Stations and", len(points[0])*len(points), "Points"

	#initalizing arrays for storing the calculations
	www      = np.zeros((shape[0], shape[1],len(stations)), dtype = np.float) #stores the point-station weights
	g_init   = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the first pass of analysis.
	g_final  = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the second pass of analysis.

	if dev_view: weight_time = time.time()
	#calculating the point-station weight values for each station.
	print "Generating weight values\n"
	for k in range(len(stations)):
		for j in range(shape[0]):
			for i in range(shape[1]):
				ddd          = points[j][i].distance(stations[k]) #distance from point at i,j to station k.
				www[j][i][k] = math.exp(-(ddd**2)/alpha)

	if dev_view: first_time = time.time()
	#running the first pass of interpolation.
	print "Running first pass of interpolation\n"
	for j in range(shape[0]):
		for i in range(shape[1]):
			w_sum = 0.0
			for k in range(len(stations)):
				g_init[j][i] += www[j][i][k]*stations[k].getAttr(attr)
				w_sum        += www[j][i][k]
			try:
				g_init[j][i] /= w_sum #for some reason I get some divide by 0 errors here, look into it.
			except:
				g_init[j][i] = 0.0	

	if dev_view: second_time = time.time()
	#running the second pass of interpolation.
	print "Running second pass of interpolation\n"
	for j in range(shape[0]):
		for i in range(shape[1]):
			dif_sum = 0.0 #stores the sum of the differences * slightly altered weight function.
			for k in range(len(stations)):
				ddd       = points[j][i].distance(stations[k])
				dif_sum  += (stations[k].getAttr(attr) - g_init[j][i])*math.exp(-(ddd**2)/(gamma*alpha))
			g_final[j][i] = g_init[j][i] + dif_sum

	for j in range(shape[0]):
		for i in range(shape[1]):
			if not points[j][i].isStation():
				points[j][i].setAttr(attr, g_final[j][i])

	if dev_view:
		end_time = time.time()
		print "Weight Generating took:",(first_time - weight_time)
		print "First pass of interpolation took:",(second_time - first_time)
		print "Second pass of interpolation took:",(end_time - second_time)
		print "In total the analysis took:",(end_time - start_time)

	return g_final