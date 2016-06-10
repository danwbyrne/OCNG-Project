import math
import numpy as np

#runs a Barnes Analysis on a given grid; alpha controls radius of influence
#that a station has, gamma controls smoothness of the interpolation.
#attr specifies which attribute of the points we are analyzing.
#setting station_view = True replaces the calculated values for stations with their original values
def Barnes(grid, attr, alpha, gamma, station_view=False):
	stations = grid.getStations()
	points   = grid.getPoints()
	shape    = grid.getShape()
	alpha    = 5.052*(((2*alpha)/math.pi)**2) #falloff rate

	print len(stations), len(points[0]), len(points)

	#initalizing arrays for storing the calculations
	www      = np.zeros((shape[0], shape[1],len(stations)), dtype = np.float) #stores the point-station weights
	g_init   = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the first pass of analysis.
	g_final  = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the second pass of analysis.

	#calculating the point-station weight values for each station.
	print "Generating weight values\n"
	for k in range(len(stations)):
		for j in range(shape[0]):
			for i in range(shape[1]):
				ddd          = points[j][i].distance(stations[k]) #distance from point at i,j to station k.
				www[j][i][k] = math.exp(-(ddd**2)/alpha)

	#running the first pass of interpolation.
	print "Running first pass of interpolation\n"
	for j in range(shape[0]):
		for i in range(shape[1]):
			w_sum = 0.0
			for k in range(len(stations)):
				g_init[j][i] += www[j][i][k]*stations[k].getAttr(attr)
				w_sum        += www[j][i][k]
			g_init[j][i] /= w_sum #for some reason I get some divide by 0 errors here, look into it.	


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

	return points