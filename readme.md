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

	Barnes(attr, alpha, gamma):
	The most important function, this runs a Barnes analysis on the Grid.
	When it is finished sets the attribute value of Points in the Grid to be the value calculated by the Barnes analysis.

