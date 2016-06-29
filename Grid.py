import math, sys, random

class Point:

	def __init__(self, lon, lat, attributes={}):
		self.x       = lon       #x-coordinate in the GRID
		self.y       = lat       #y-coordinate in the GRID

		self.weights = {}

		self.attributes = attributes #dictionary of attributes

	#get and set commands for the attributes of this point
	def setAttr(self, attr, value): self.attributes[attr] = value
	def getAttr(self, attr): return self.attributes[attr]

	#calculates the distance between this point and another
	#uses the haversine formula to calculate this
	def distance(self, point):
		rrr      = 6371. #mean distance of earths radius, in km
		lat1     = math.radians(point.y)
		lat2     = math.radians(self.y)
		lat_dif  = math.radians(self.y - point.y)
		lon_dif  = math.radians(self.x - point.x)

		aaa      = (math.sin(lat_dif/2))**2 + math.cos(lat1)*math.cos(lat2) * (math.sin(lon_dif/2))**2
		ccc      = 2 * math.atan2(math.sqrt(aaa), math.sqrt(1.-aaa))

		return rrr*ccc


	#calculates the residual between the attributes of this point and another.
	def residual(self, point, attr): return (point.getAttr(attr) - self.getAttr(attr))

class Grid:

	def __init__(self, points=[[]], stations = []):

		self.points   = points
		self.stations = stations

	#returns the number of points in the grids array.
	def getSize(self): return len(self.points)*len(self.points[0])

	#returns the dimensions of this grid.
	def getShape(self): return (len(self.points),len(self.points[0]))

	#returns the list of points in the grid.
	def getPoints(self): return self.points

	#returns a list of stations in this grid.
	def getStations(self): return self.stations


	#creates a grid of dummy points.
	#this is really just a testing function, no other uses.
	def createPoints(self, x_amount, y_amount):
		points = []
		for y in range(y_amount):
			row = []
			for x in range(x_amount):
				row.append(Point(x,y))
			points.append(row)
		self.points = points

	#creates a number of random stations with a random attr-value < max_value
	#this is really just a testing function, no other uses.
	def createStations(self, num, attr, max_value):
		for i in range(num):
			y = random.randint(0, len(self.points)-1)
			x = random.randint(0, len(self.points[y])-1)
			self.points[y][x].station = True
			self.points[y][x].setAttr(attr, random.randint(0, max_value))



	#returns a list of attribute values, as opposed to a list of point objects, useful when graphing.
	def getAttrList(self, attr):
		attr_list = []
		for j in range(len(self.points)):
			row = []
			for point in (self.points[j]):
				row.append(point.getAttr(attr))
			attr_list.append(row)
		return attr_list

	#returns a list of the residual values between this grid and another.
	def getResidualList(self, grid, attr):
		resid_list = []

		if self.getShape() != grid.getShape():
			print "dimension error: grids are of different shapes"

		else:
			shape = self.getShape()
			for y in shape[0]:
				for x in shape[1]:
					resid = self.points[y][x].residual(grid.points[y][x], attr)
					resid_list.append(resid)

		return resid_list