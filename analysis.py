import math
import Data
import numpy as np
from numpy.linalg import inv
import mapper
from scipy import stats
from scipy.interpolate import interp1d

def createGrid(bounds, dn):
	ys,xs = np.mgrid[slice(bounds[3], bounds[2]+dn, dn),
					 slice(bounds[1], bounds[0]+dn, dn)]
	return ys, xs
#####MODELS#####
def reduceModel(model, alpha, c0):

	def funct(dist):
		return model(dist, alpha, c0)
	return funct

def makeLinear(xs, ys):
	slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
	print r_value

	def linear(dist):
		return slope*dist + intercept

	return linear

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
	if dist > alpha: return c0
	return c0*(1. - math.exp(-(dist/alpha)**2))

def sinusoidal(dist, alpha, c0):
	if dist == 0: return 0.
	if dist > alpha: return c0
	return c0*(1 - math.sin((math.pi*dist)/alpha)/((math.pi*dist)/alpha))


def makePerfect(xs, ys, max_range):
	'''experimental, probably doesn't have any uses'''
	def perfect(dist):
		if dist > max_range:
			return ys[-1]

		return np.interp(dist, np.append([0.],xs[1:]), np.append([0.], ys[1:]))

	return perfect

################

def semivar(points, lag):
	sss      = 0.
	count    = 0
	for j in range(points.size()):
		for i in range(points.size()):
			if i == j: break		

			elif (points[j].distance(points[i]) <= lag):
				sss   += points[j].squareDiff(points[i])
				count += 1

	if count == 0:
		return None

	return sss / (2.*count)

def semivariogram(points, model, bw=5):
	mm = np.amax(points.distMatrix()) #max_range
	xs = [(i+1)*bw for i in range(int(math.ceil(mm/bw)))]
	ys = [None for _ in range(len(xs))]

	for i, x in enumerate(xs):
		ys[i] = semivar(points, x)

	c0 = ys[-1]
	

	alpha = opt(model, xs, ys, c0)
	return xs, ys, alpha

#finds the alpha value between a range that best satisfies the fit for a model
def opt(model, xs, ys, c0, paramRange=[1,2000], precision=10000):
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

	return alpha

def augmentMatrix(mat):
	column = np.ones(mat.shape[0]).T
	row    = np.append(np.ones(mat.shape[0]) ,0.)
	mat = np.column_stack((mat, column))
	return np.row_stack((mat, row))

#this is ordinary krieging, where we work with neighborhoods of data, MUCH more timely than simple krieging
def krigInterp(points, stations, model, max_range, n):
	mmm = stations.mean()

	for point in points:
		closest = stations.nClosest(point, int(n/2), max_range/2.)

		try:
			if closest.size() < int(n/3.) and (True not in [(point.distance(stat) < max_range/5.) for stat in closest] ):
				closest = None

			values  = np.append( closest.residArray(mmm), [0.] )
			cov_mat = augmentMatrix(closest.covMatrix(model))
			cov_vec = np.append(closest.covVector(point, model), [1.]).T

			weights = np.dot(inv(cov_mat),cov_vec)
			point.value = mmm + np.dot(weights, values)

		except:
			point.value = np.nan


	return points

def getKrieged(stations, dn, funct, max_range):
	#a nice function to make krieging less painful in our main function
	lons, lats = stations.lonArray(), stations.latArray()

	#calculates the bounds for the basemap
	bounds = [int(max(lons)+1), int(min(lons)-2),
			  int(max(lats))+2, int(min(lats)-1)] 

	#creates grid-values based on bounds and resolution
	yg, xg = createGrid(bounds, dn)
	shape  = (len(yg)-1, len(yg[0])-1)

	#creates an array of blank points with locations at the center of the gridpoints
	points = Data.Points([])
	for j in range(shape[0]):
		for i in range(shape[1]):
			x_mid = (xg[j][i] + xg[j][i+1])/2.
			y_mid = (yg[j][i] + yg[j+1][i])/2.
			points.append(Data.Point(x_mid, y_mid))

	points = krigInterp(points, stations, funct, max_range, 100)
	return bounds, xg, yg, points


