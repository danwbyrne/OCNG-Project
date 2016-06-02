import math

class Frame:

	def __init__(self):
		#TODO this will be the wrapper class from the model snapshot to callable functions.
		pass

class Point:

	def __init__(self, latitude = 0.0,longitude = 0.0, ss = None, bs = None, so = None, bo = None, depth = 0.0):

		self.latitude  = latitude
		self.longitude = longitude
		self.ss        = ss
		self.bs        = bs
		self.so        = so
		self.bo        = bo
		self.depth     = depth

		self.fromPos()

		def setPos(self,latitude,longitude):
			self.latitude = latitude
			self.longitude = longitude


		def fromPos(self):
			#TODO When you get the tool this function will extract ss,bs,so,bo based on lat/long.
			pass


class Line:

	def __init__(self, point1, point2):
		#two predetermined points
		self.p1 = point1 
		self.p2 = point2

		self.distance = None #distance stored as latitude degrees, longitude degrees
		self.getDistance()

		self.lineData = []

	def getDistance(self):
		#calculates the degrees of lat/long between 2 points.
		lat_dist  = self.p2.latitude - self.p1.latitude
		long_dist = self.p2.longitude - self.p1.longitude

		self.distance = (lat_dist, long_dist)

	def distanceToKM(self):
		lat_km  = self.distance[0] * 110.574 #1 degree of latitude ~= 110.574 km
		long_km = 111.32 * self.distance[1] * math.cos((self.p1.latitude)*360/(math.pi)) #1 degree of longitude ~= 111.32*cos(latitude) km

		return (lat_km, long_km)

	def getData(self):
		#TODO: This probably needs a different approach for finding sub points on the line, range() might not be the way to do it.
		#Decide how to properly move along a line where you can still get data inbetween, this will be easier once you can actually work with the data.
		lineData = []
		km_distance = self.distancetoKM()
		start    = self.p1
		lineData.append(start)

		interval = int(km_distance[1])
		if km_distance[0] >= km_distance[1]: #look at how you are doing spacing for this later
			interval = int(km_distance[0])

		for i in range(interval):
			new_lat  = start.latitude + (self.distance[0]/float(interval))  
			new_long = start.longitude + (self.distance[1]/float(interval))

			new_point = Point()
			new_point.setPos(new_lat, new_long)

			#get data about this point from the Frame
			new_point.fromPos()
			lineData.append(new_point)

		lineData.append(self.p2)

		self.lineData = lineData


class Trek:

	def __init__(self, points):
		pass

	def getLines(self):
		size = len(self.points)
		if size < 2:
			print "Insufficient amount of points: %s", size
		else:
			for i in range(1,size):
			lines.append((self.points[i-1],self.points[i]))

