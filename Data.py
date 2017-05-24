import math, operator
import numpy as np
from numpy.linalg import inv
import analysis, Parser
import time



#our most primitive class, stores an x,y position and a arbitrary point value.
class Point:

	def __init__(self, lon, lat, value=0., timeUTC = None):
		self.lon     = lon     #x-coordinate
		self.lat     = lat     #y-coordinate
		self.value   = value   #an attribute value for this Point
		self.timeUTC = timeUTC #timestamp for this stations data

	def __str__(self):
		string = "%.8f %.8f %.5f" % (self.lon, self.lat, self.value)
		if self.timeUTC: string = string + " %s" % (time.strftime("%d\%b\%y-%H:%M:%S",time.localtime(self.timeUTC)))
		return string

	#uses the haversine formula to calculate the distance between two points in km
	def distance(self, point):
		rrr      = 6371. #mean distance of earths radius, in km
		lat1     = math.radians(point.lat)
		lat2     = math.radians(self.lat)
		lat_dif  = math.radians(self.lat - point.lat)
		lon_dif  = math.radians(self.lon - point.lon)

		aaa      = (math.sin(lat_dif/2.))**2 + math.cos(lat1)*math.cos(lat2) * (math.sin(lon_dif/2.))**2
		dist     = 2. * rrr * math.atan2(math.sqrt(aaa), math.sqrt(1.-aaa)) #the calculate distance, in km

		return abs(dist) 

	def squareDiff(self, point): return (self.value - point.value)**2

#a collection of points and useful functions
class Points:

	def __init__(self, points=[], filename=None):

		self.points = points #our array of points
		if filename != None: self.load(filename) #if given a file, loads it

	def __getitem__(self, i): return self.points[i]

	def save(self, filename): Parser.pointsToCSV(filename, self.points)

	def load(self, filename): self.points = Parser.loadPoints(filename)

	#wrapper list functions
	def append(self, point):      self.points.append(point)
	def extend(self, new_points): self.points.extend(new_points.points)

	#multiple functions to allow easy conversion to other formats as needed
	def timeArray(self):   return np.asarray([point.timeUTC for point in self.points])
	def valueArray(self):  return np.asarray([point.value for point in self.points])
	def lonArray(self):    return np.asarray([point.lon for point in self.points])
	def latArray(self):    return np.asarray([point.lat for point in self.points])
	def asArray(self):     return np.asarray(zip(self.lonArray(), self.latArray(), self.valueArray()))
	def nanFiltered(self): return Points([point for point in self.points if point.value != np.nan])

	def residArray(self, mmm=None):
		if mmm == None: return np.asarray([point.value - self.mean() for point in self.points])
		return np.asarray([point.value - mmm for point in self.points])

	def normalize(self):
		mmm = self.mean()
		var = self.var()
		for point in self.points:
			point.value = (point.value - mmm)/math.sqrt(var)

	def unNormalize(self, mmm, vvv):
		for point in self.points:
			point.value = (point.value*math.sqrt(vvv) + mmm)

		
	#some statistical functions for calculating value information
	def size(self):    return len(self.points)
	def mean(self):    return np.mean(self.valueArray())
	def var(self):     return np.var(self.valueArray())

	#returns the total sum of squares
	def sst(self):
		mmm = self.mean()
		return sum([(point.value - mmm)**2 for point in self.points])

	#returns the n-closest stations to this point.
	def nClosest(self, point, n, max_range):
		return_points, dist_dict = Points([]), {}
		for p1 in self.points:
			if point.distance(p1) <= max_range:
				dist_dict[p1] = point.distance(p1)
		try:

			dist_dict = sorted(dist_dict.items(), key=operator.itemgetter(1))[::-1]
			closest   = dist_dict.pop()

		
			while (return_points.size() < n) and (0 < len(dist_dict)):
				return_points.append(closest[0])
				closest = dist_dict.pop()

			return return_points

		except:
			return None

	#returns a matrix of point values in a given shape.
	def valueMatrix(self, shape):
		return np.reshape(self.valueArray(), shape)

	#returns a covariance matrix of these points based on a given model
	def covMatrix(self, model):
		#c0  = self.var()
		mat = [model(p1.distance(p2)) for p1 in self.points for p2 in self.points]
		return np.asarray(mat).reshape((self.size(), self.size()))

	#returns a matrix that represents the distance between all points
	def distMatrix(self):
		mat = [p1.distance(p2) for p1 in self.points for p2 in self.points]
		return np.asarray(mat).reshape((self.size(), self.size()))

	#returns a covariance vector of a point given a model
	def covVector(self, point, model):
		#c0  = self.var()
		return np.asarray([model(point.distance(p1)) for p1 in self.points])

	def getNonNan(self):
		good_points = [point for point in self.points if (str(point.value) != 'nan')]
		return Points(good_points)

