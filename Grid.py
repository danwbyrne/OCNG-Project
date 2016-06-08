import math
import Mapper
import sys
import random

def newList3(x, y, z):
	new_list = []
	for k in range(z):
		row1 = []
		for j in range(y):
			row2 = []
			for i in range(x):
				row2.append(0.0)
			row1.append(row2)
		new_list.append(row1)

	return new_list

def newList2(x,y):
	new_list = []
	for j in range(y):
		row = []
		for i in range(x):
			row.append(0.0)
		new_list.append(row)

	return new_list


class Point:

	def __init__(self, x, y, station=False, ss = 0.0, bs = 0.0, so = 0.0, bo = 0.0):
		self.x       = x       #x-coordinate in the GRID
		self.y       = y       #y-coordinate in the GRID

		self.station = station #true or false depending on if we already know information about this point.

		self.attributes = {"ss": ss, "bs": bs,
						   "so": so, "bo": bo}

	def isStation(self): return self.station

	#calculates the distance between points
	def distance(self, point): return math.sqrt((point.x - self.x)**2 + (point.y - self.y)**2)

	def setAttribute(self, attr, value): self.attributes[attr] = value
	def getAttribute(self, attr): return self.attributes[attr]

	#resets this data point, useful for doing an analysis multiple times.
	def reset(self):
		self.attributes = {"ss": 0.0, "bs": 0.0,
						   "so": 0.0, "bo": 0.0}

class Grid:

	def __init__(self, points=[[]]):

		self.points   = points
		self.stations = []

	def getStations(self):
		stations = []
		for points in self.points:
			for point in points:
				if point.isStation():
					stations.append(point)
		self.stations = stations

	#creates a grid of dummy points
	def createPoints(self, x_amount, y_amount):
		points = []
		for y in range(y_amount):
			row = []
			for x in range(x_amount):
				row.append(Point(x,y))
			points.append(row)
		self.points = points

	#resets all the points that are not stations.
	def resetPoints(self):
		for point in self.points:
			if not (point.isStation()):
				point.reset()

	#sets everything about a point.
	def setPoint(self, x, y, station, ss, bs, so, bo):
		self.points[y][x].station = station
		self.points[y][x].attributes["ss"] = ss
		self.points[y][x].attributes["bs"] = bs
		self.points[y][x].attributes["so"] = so
		self.points[y][x].attributes["bo"] = bo

	def printGrid(self, attr):
		lines = ""
		for j in range(len(self.points)):
			line = ""
			for i in range(len(self.points[j])):
				line += "%s  " % (self.points[j][i].getAttribute(attr))
			lines += line + "\n"

		print lines

	def getAttrList(self, attr):
		new_list = []
		for j in range(len(self.points)):
			row = []
			for i in range(len(self.points[j])):
				row.append(self.points[j][i].getAttribute(attr))
			new_list.append(row)
		return new_list

	#creates a bunch of random stations for testing
	def createStations(self, num_stations, attr, attr_max):
		for i in range(num_stations):
			y = random.randint(0,len(self.points)-1)
			x = random.randint(0,len(self.points[y])-1)
			self.points[y][x].station = True
			self.points[y][x].attributes[attr] = random.randint(0,attr_max)


	def Barnes(self, attr, alpha, gamma):
		print len(self.points[0]), len(self.points), len(self.stations), '\n\n\n'
		w = newList3(len(self.points[0]), len(self.points), len(self.stations))
		alpha = 5.052*((2*alpha)/math.pi)**2
		#self.printGrid(attr)
		print "calculating w-values\n\n"
		for k in range(len(self.stations)):
			for j in range(len(self.points)):
				for i in range(len(self.points[j])):
					#if not self.points[j][i].isStation():
					if True:
						d          = self.points[j][i].distance(self.stations[k])
						w[k][j][i] = math.exp(-(d**2)/alpha)

					else:
						w[k][j][i] = 0.0

		g_init = newList2(len(self.points[0]), len(self.points))
		print "running first pass\n\n"
		for j in range(len(self.points)):
			for i in range(len(self.points[j])):
				#if not self.points[j][i].isStation():
				if True:
					w_sum = 0.0
					g_init[j][i] = 0.0
					for k in range(len(self.stations)):
						g_init[j][i] += w[k][j][i]*self.stations[k].getAttribute(attr)
						w_sum += w[k][j][i]

					try:
						g_init[j][i] /= w_sum
					except:
						g_init[j][i] = 0.0

				else:
					g_init[j][i] = 0.0

		g_final = newList2(len(self.points[0]), len(self.points))
		print "running second pass\n\n"
		for j in range(len(self.points)):
			for i in range(len(self.points[j])):
				#if not self.points[j][i].isStation():
				if True:
					dif_sum = 0.0
					for k in range(len(self.stations)):
						d = self.points[j][i].distance(self.stations[k])
						dif_sum += (self.stations[k].getAttribute(attr) - g_init[j][i])*math.exp(-(d**2)/(gamma*alpha))

					g_final[j][i] = g_init[j][i] + dif_sum

				else:
					g_final[j][i] = self.points[j][i].getAttribute(attr)

		for j in range(len(self.points)):
			for i in range(len(self.points[j])):
				self.points[j][i].setAttribute(attr, g_final[j][i])


def main():
	#try:
	grid = Grid()
	grid.createPoints(100,100)
	grid.createStations(50, "ss", 50)
	grid.getStations()

	grid.Barnes("ss", 7, .8)

	#grid.printGrid("ss")

	Mapper.map(grid.getAttrList("ss"))

	#except:
	#	print("Unexpected error:", sys.exc_info()[0])
	#	raw_input()


if __name__ == "__main__":
	main()
	raw_input()