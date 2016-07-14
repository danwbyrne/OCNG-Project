import numpy as np
import time, operator, math
from numpy.linalg import inv

#returns a list of AT MOST N stations within the range of max_range, if
#it cannot find 20 points it returns as many as it can.
def findNClosest(point, stations, N, max_range):
	return_list, dist_dict = [], {}
	for station in stations:
		dist_dict[station] = point.distance(station)

	#returns a sorted list of station-dist keys in an order that we can pop from.
	sorted_dists = sorted(dist_dict.items(), key=operator.itemgetter(1))[::-1]
	station = sorted_dists.pop()

	#keep building return_dict until one of the conditions is not met.
	while (len(return_list) < N) and (station[1] <= max_range):
		return_list.append(station)
		station = sorted_dists.pop()

	return return_list

#calculates the mean value of attribute in a list of points, or in a tuple style like returned by FindNClosest.
def mean(points, attr):
	sss = 0.
	try: 
		for point in points: sss += point.getAttr(attr)
	except: 
		for point in points: sss += point[0].getAttr(attr)

	return sss / len(points)

def exponential(distance, alpha):
	return math.exp(-(distance**2)/alpha)

#runs a Barnes Analysis on a given grid; alpha controls radius of influence
#that a station has, gamma controls smoothness of the interpolation.
#attr specifies which attribute of the points we are analyzing.
#setting station_view = True replaces the calculated values for stations with their original values
#setting dev_view = True lets you see running time values for the analysis.
def Barnes(points, stations, attr, alpha, gamma, N=20, dev_view=False):
	if dev_view: start_time = time.time()
	shape    = (len(points),len(points[0]))
	alpha    = 5.052*(((2*alpha)/math.pi)**2) #falloff rate

	print "Running Barnes Analysis on:"
	print len(stations),"Stations and", len(points[0])*len(points), "Points"

	#initalizing arrays for storing the calculations
	#www      = np.zeros((shape[0], shape[1],len(stations)), dtype = np.float) #stores the point-station weights
	g_init   = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the first pass of analysis.
	g_final  = np.zeros((shape[0], shape[1]), dtype = np.float) #stores the data from the second pass of analysis.

	if dev_view: weight_time = time.time()
	#calculating the point-station weight values for each station.
	print "Generating weight values\n"
	for j in range(shape[0]):
		for i in range(shape[1]):
			weights = {}
			for station in (findNClosest(points[j][i], stations, N, alpha)):
				ddd = station[1] #distance
				w1  = math.exp(-(ddd**2)/alpha)         #weight function for first pass
				w2  = math.exp(-(ddd**2)/(alpha*gamma)) #weight function for second pass
				weights[station[0]] = [w1,w2]
			points[j][i].weights = weights

	if dev_view: first_time = time.time()
	#running the first pass of interpolation.
	print "Running first pass of interpolation\n"
	for j in range(shape[0]):
		for i in range(shape[1]):
			w_sum = 0.0
			weights = points[j][i].weights
			for station in weights.keys():
				g_init[j][i] += weights[station][0]*station.getAttr(attr)
				w_sum        += weights[station][0]
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
			weights = points[j][i].weights
			for station in weights.keys():
				dif_sum  += (station.getAttr(attr) - g_init[j][i])*weights[station][1]
			g_final[j][i] = g_init[j][i] + dif_sum

	if dev_view:
		end_time = time.time()
		print "Weight Generating took:",(first_time - weight_time)
		print "First pass of interpolation took:",(second_time - first_time)
		print "Second pass of interpolation took:",(end_time - second_time)
		print "In total the analysis took:",(end_time - start_time)

	return g_final


def Kriging(points, stations, attr, weight_func, alpha, N=20):
	print "Starting Kriging Interpolation"
	shape = len(points), len(points[0])
	alpha = 5.052*(((2*alpha)/math.pi)**2)
	runs  = 0.

	final = np.zeros(shape, dtype = np.float)

	#go through all the points
	for j in range(shape[0]):
		for i in range(shape[1]):
			#at each point we'll have N estimators, so an NxN covariance matrix and
			#a 1xN weight matrix for obtaining or final weight matrix
			estimators = findNClosest(points[j][i], stations, N, alpha)
			mmm        = mean(estimators, attr)
			cov_mat    = np.zeros((len(estimators),len(estimators)), dtype = np.float)
			weights    = np.zeros(len(estimators), dtype = np.float)
			values     = np.zeros(len(estimators), dtype = np.float)

			#set up our covariance matrix and our weight matrix at the same time
			for ii in range(len(estimators)):
				weights[ii] = weight_func(estimators[ii][1], alpha)
				values[ii]  = estimators[ii][0].getAttr(attr)
				for jj in range(len(estimators)):
					cov_mat[jj][ii] = weight_func(estimators[ii][0].distance(estimators[jj][0]), alpha)

			cov_inv = inv(cov_mat)
			weights = np.dot(cov_inv, weights)

			final[j][i] = mmm + np.dot(weights, values)

			runs += 1.
			print str(runs/(shape[0]*shape[1])*100.),"percent complete"



	return final

