import math
import Data
import numpy as np
from numpy.linalg import inv
import Mapper

def createGrid(bounds, dn):
	ys,xs = np.mgrid[slice(bounds[3], bounds[2]+dn, dn),
					 slice(bounds[1], bounds[0]+dn, dn)]
	return ys, xs

#####MODELS#####
def cubic(dist, alpha, c0):
	if dist == 0: return 0.
	if dist > alpha: return c0
	return c0*(7*((dist/alpha)**2) - 8.75*((dist/alpha)**3) + 3.5*((dist/alpha)**5) - .75*((dist/alpha)**7))

def spherical(dist, alpha, c0):
	if dist == 0: return 0.
	if dist > alpha: return c0
	return c0*(1.5*(dist/alpha) - .5*((dist/alpha)**3))

def pentaspherical(dist, alpha, c0):
	if dist == 0: return 0.
	if dist > alpha: return c0
	return c0*(1.875*(dist/alpha) - 1.25*(dist/alpha)**3 + .375*(dist/alpha)**5)

def gaussian(dist, alpha, c0):
	if dist == 0: return 0.
	return c0*(1. - math.exp(-(dist/alpha)**2))

def sinusoidal(dist, alpha, c0):
	if dist == 0: return 0.
	return c0*(1 - math.sin((math.pi*dist)/alpha)/((math.pi*dist)/alpha))
################

def semivar(points, lag, bw):
	sum_list = []
	dist_mat = points.distMatrix()

	for j in range(points.size()):
		for i in range(j, points.size()):

			if (lag-bw <= dist_mat[j][i] <= lag+bw):
				sum_list.append(points[j].squareDiff(points[i]))

	try: return sum(sum_list) / (2. * len(sum_list))
	except: return None

#finds the alpha value between a range that best satisfies the fit for a model
def opt(model, xs, ys, c0, paramRange=[1,1000], precision=10000):
	errors = np.zeros(precision)
	alphas = np.linspace(paramRange[0], paramRange[1], precision)

	for i in range(precision):
		calcs = []
		for (x,y) in zip(xs,ys):
			calc = model(x, float(alphas[i]), c0)
			if str(y) != 'nan':
				calcs.append((y - calc)**2)

		errors[i] = sum(calcs)/len(calcs)
	alpha = alphas[errors.argmin()]

	#Mapper.semiMap(model, xs, ys, c0, alpha)

	return alphas[errors.argmin()]

def semivariogram(points, model, bw=5):
	values   = points.valueArray()
	c0       = points.var()
	lags     = np.arange(0, 700, bw)
	ys       = np.zeros(np.shape(lags), dtype = np.float)

	for i in range(len(lags)):
		sv = semivar(points, lags[i], bw)

		if sv == None: ys[i] = None
		elif (str(sv) != "nan"): ys[i] = sv

	alpha = opt(model, lags, ys, c0)
	optf  = [model(lags[i], alpha, c0) for i in range(len(lags))]



	return (lags, ys, np.asarray(optf), alpha)

#interpolates a list of points based on a list of stations and a model
#using a kriging analysis
def krigInterp(points, stations, model, alpha):
	#mmm = stations.mean()

	for point in points:
		close_stats = stations #stations.nClosest(point, 20) STILL NOT SURE IF THIS WORKS RIGHT
		values      = close_stats.residArray()
		point_covs  = close_stats.covVector(point, model, alpha)
		stat_covs   = close_stats.covMatrix(model, alpha)

		try:
			weights     = np.dot(inv(stat_covs), point_covs)
			point.value = np.dot(weights, values) + stations.mean() #+mmm

		except:
			print "got fucked"

	return points