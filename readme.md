The BarnesMap function in the main.py file is probably the most important function I am using right now, it handles the full process from CSV-data -> Analysis -> Plotting, although it invokes multiple functions from Mapper.py (objectiveMap() in particular) as well as from analysis.py

More updates to come on the full process.

-------------
|CSVtoPoints|
-------------

CSVtoPoints is a package that handles the parsing of input CSV files to dictionaries that can be easily read and converted to stations for further calculations. The package has only two functions at the moment, but may be expanded on further to handle more of the bulk of CSV->station conversions.

-readCSV(filedir):
	this function takes an input .csv file and returns a a list of dictionaries of its data. It takes the first non-whitespace line of the file as the keys for the dictionaries.

-multiRead(filedir):
	this function takes an input file directory where multiple .csv files are located and runs the readCSV function on each .csv file in that directory, returning a large list of dictionaries.

#TODO: Perhaps handle the string->type conversion within this module so it doesn't have to be done in other packages.

-----------
|  Grid   |
-----------

Grid is a package that contains two classes, Point and Grid. Grid is an almost obsolete class that will be removed in later versions however for now it is still used in the Barnes function of the analysis function. Point is an important class that does the following:

	-stores latitude/longitude of a point
	-stores attributes about a point in a dictionary
	-has a distance(point) function that calculates the distance, in Km, from this point to another.

#TODO: need to get rid of the Grid class ideally as it is just unnecessary wrapping that the analysis function doesn't need anymore, although it still has its uses for testing new analysis functions in some of its functions.

----------
|analysis|
----------

The analysis package is where the bulk of the calculations is maintained, although as of right now it only contains the Barnes() function, in the future it will also contain functions for running a Gauss-Markov Optimal Interpolation. The Barnes function does the following:

	-takes in a grid, attribute name we are running the analysis on, alpha value which influences weight falloff rate,and a gamma value which influences second pass smoothing of the grid.

	1)unwraps the grid to a list of points and stations and adjusts alpha

	2)for every station given, a weight value will be assigned from it to every non-station gridpoint given. This value is given by:
		weight = exp(-(distance^2)/alpha)

	3)Go through every grid point and calculate an initial value given by:
		g0(i,j) = sum for all k of (weight(i,j,k)*station-value(k))
		this value is also divided by the sum of all its weight values

	4)Finally a second-pass smoothing is applied and gFinal is returned.

#TODO: implement Gauss-Markov Interpolation.
#TODO: move away from using the grid class, just take direct inputs.
#TODO: maybe try implementing the ClosestN method as well seen in OI.

--------
|Mapper|
--------

The Mapper package is the package that handles all of the mapping of the csv data as well as the analysis grid data. It has a few functions, however the map() and multiPlot() function are both somewhat obsolete and are no longer used (they were used primarily in early stage testing). However the important function, ObjectiveMap() does the following:

	-takes lat/long boundary data, analyzed grid values, station locations, and some formatting data as inputs.
	-Uses the Basemap package to create an geographical plot area from bounds
	-plots the analyzed data as a color map on the grid.
	-plots the location of all the input stations.
	-plots a high resolution coastline, meridians, and parallels.
	-can show the plot, save the plot, or do both

#TODO: some more formatting with the colorbar, as well as some multi-mapping tools.

