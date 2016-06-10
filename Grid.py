import math, sys, random
import numpy as np
import analysis
import Mapper

class Point:

	def __init__(self, x, y, station=False, ss = 0.0, bs = 0.0, so = 0.0, bo = 0.0):
		self.x       = x       #x-coordinate in the GRID
		self.y       = y       #y-coordinate in the GRID

		self.station = station #true or false depending on if we already know information about this point.

		self.attributes = {"surface salinity": ss,
						   "bottom salinity" : bs,
						   "surface oxygen"  : so,
						   "bottom oxygen"   : bo}

	#returns True or False if this point is a station
	def isStation(self): return self.station

	#get and set commands for the attributes of this point
	def setAttr(self, attr, value): self.attributes[attr] = value
	def getAttr(self, attr): return self.attributes[attr]

	#calculates the distance between this point and another
	def distance(self, point): return math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

	#calculates the residual between the attributes of this point and another.
	def residual(self, point, attr): return (point.getAttr(attr) - self.getAttr(attr))

	#resets the attributes of this point to 0, useful for doing more than one analysis.
	def reset(self):
		self.attributes = {"surface salinity": 0.0,
						   "bottom salinity" : 0.0,
						   "surface oxygen"  : 0.0,
						   "bottom oxygen"   : 0.0}

class Grid:

	def __init__(self, points=[[]]):

		self.points   = points
		#self.stations = [] might not need this with how stations are added.

	#returns the number of points in the grids array.
	def getSize(self): return len(self.points)*len(self.points[0])

	#returns the dimensions of this grid.
	def getShape(self): return (len(self.points),len(self.points[0]))

	#returns the list of points in the grid.
	def getPoints(self): return self.points

	#returns a list of stations in this grid.
	def getStations(self):
		stations = []
		for row in self.points:
			for point in row:
				if point.isStation(): stations.append(point)
		return stations


	#creates a grid of dummy points.
	def createPoints(self, x_amount, y_amount):
		points = []
		for y in range(y_amount):
			row = []
			for x in range(x_amount):
				row.append(Point(x,y))
			points.append(row)
		self.points = points

	#creates a number of random stations with a random attr-value < max_value
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