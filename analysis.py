import numpy as np
import time, operator, math
from numpy.linalg import inv
from pylab import *

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
		return_list.append(station[0])
		station = sorted_dists.pop()

	return return_list

#plugs a distance into the spherical formula and returns a covariance
def spherical(distance, alpha, sill=1.):
	if distance > alpha:
		return 0.
	return sill*(1.-1.5*(distance/alpha) + .5*((distance/alpha)**3))

#calculates the mean value of attribute in a list of points, or in a tuple style like returned by FindNClosest.
def mean(points):
	sss = 0.
	try: 
		for point in points: sss += point.value
	except: 
		for point in points: sss += point[0].value

	return sss / len(points)

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

#returns a covariance matrix of station -> station distances, M x M
def cov_mat(stations, funct, alpha):
	mat = np.zeros((len(stations), len(stations)), dtype = np.float)

	for j in range(len(stations)):
		for i in range(len(stations)):
			mat[j][i] = stations[j].distance(stations[i])
			mat[j][i] = funct(mat[j][i], alpha)

	return mat

#returns covariance vector of point -> station distances, 1 x N
def cov_vect(point, stations, funct, alpha):
	mat = np.zeros(len(stations), dtype = np.float)

	for ss in range(len(stations)):
		mat[ss] = funct(point.distance(stations[ss]), alpha)

	return mat



#SUPER DIRTY ATM
#TODOS: clean it up, getting findNClosest points working, optimization
#probably want to rewrite anything using a form for the full program function such
#that you can define the analysis type as an argument instead of having multiple functions
#that do basically the same thing
def kriging(points, stations, funct, alpha=500):
	shape = (len(points), len(points[0]))
	size = shape[0]*shape[1]
	count = 1.
	print "Number of points: ", size

	output = np.zeros(shape, dtype = np.float)

	for j in range(len(points)):
		for i in range(len(points[0])):

			close_stats = findNClosest(points[j][i], stations, 16, 1000)
			nnn = len(close_stats)
			mmm = mean(close_stats)
			values = np.zeros(nnn, dtype = np.float)
			for z in range(nnn):
				values[z] = close_stats[z].value - mmm

			point_covs  = cov_vect(points[j][i], close_stats, funct, alpha)
			stat_covs   = cov_mat(close_stats, funct, alpha)

			weights     = np.dot(inv(stat_covs),point_covs)

			value = np.dot(weights, values)

			output[j][i] = value + mmm
			print count/float(size)
			count += 1

	print "kriging complete"
	return output

