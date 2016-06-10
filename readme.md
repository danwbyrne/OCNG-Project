-----------------
|The Point Class|
-----------------

The Point class is an object that is incorporated into the Grid class, it stores:
	-xy-coordinates of where the point is on the Grid
	-A boolean value that designates whether or not this Point is a station
	-A list of attributes (surface salinity, bottom salinity, surface oxygen, bottom oxygen)

It contains functions to:
	-get/set attributes of the Point
	-reset the point (useful for running multiple tests)

----------------
|The Grid Class|
----------------

The Grid class stores a list of stations and a list of Points.

It has the following functions:
	getStations() :
	finds a list of stations in its list of points and sets it.

	createPoints(x_amount, y_amount) :
	creates a 2x2 matrix of x*y blank points.

	resetPoints() :
	resets all of the points stored in grid.

	setPoint(x, y, station, ss, bs, so, bo) :
	sets the attributes of a point in the Grid. 
	#TODO probably don't need this function, or need a better one

	printGrid(attr) :
	prints a semi-nice list of the attribute-value for every point in the Grid. 
	#TODO make this formatted better

	createStations(num_stations, attr, attr_max) :
	creates a number of stations, randomly assigning their xy-coord and attribute up to a maximum.

-------------------
|The Analysis File|
-------------------

This file only holds the Barnes analysis function for the moment, but more
analysis related functions will be stored here.

		Barnes(grid, attr, alpha, gamma, station_view=False):
		The most important function, this runs a Barnes analysis on a Grid.
		When it is finished it returns a list of the attribute values of Points in the Grid as calculated by its interpolation.

		grid  = The Grid object we are analzing
		attr  = The attribute we want to analyze
		alpha = Controls the radius of influence each station has
		gamma = Controls how much smoothing the second pass does

		setting station_view to True plots the stations original values so you can more easily see their influence on the graph.

		This function does the following:
			-For every point we know information about (called a station) create a weight (www) from that station to every other point.

			-Next the first pass of interpolation is run, for every point a g_init(i,j) value is calculated as:
			the sum of [weight(i,j)*station[k].value] for all k stations divided by the sum of [weight(i,j)] for all k stations

			-Finally the last pass of interpolation (the smoothing path) is run. Here a weighted difference between stations and points is added to g_init. This pass is less intuitive, but it essentially smooths the edges and stations out.