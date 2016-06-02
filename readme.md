Mapper is a python file that contains 4 classes so far:

---------
| Frame |
---------
	
	Frame is a class that will essentially be a wrapper from the model snapshot I receive
	and callable functions to work with other classes. Once I have access to the data this class should:

		- have a callable function that can get surface/bottom salinity, surface/bottom oxygen levels, and maybe depth based on a lat/long position.

---------
| Point |
---------

	Point is a basic class that will hold a latitude/longitude as well as the attributes from the model associated with its position.
	It will be the most basic object used, and should implement the ability to:

		- get data from the Frame based on latitude & longitude
		- convert to and from a string for storage in a Line.


--------
| Line |
--------

	Line is a class which holds 2 points, and in turn can calculate "nice" points in between those 2 to be analyzed.
	It handles finding distance between points, conversion of distance to Km for iteration, and it will eventually be able to:

	    -reliably predict points in between (need to do some work on the calculations for latitude & longitude with Km distances)
	    -collect data about all of those points, and store them nicely as a string.

--------
| Trek |
--------

	Trek is a class which will store multiple lines, and handle storing and analyzing them in an order. This class will probably be the highest level
	class needed and will contain the bulk of the code for both running the simulation on points and for analyzing the data. It should:

		-create and hold multiple line classes based on "waypoint" Points (i.e points we determine, not calculated in the Line class).
		-convert to and from a text (cdf?) document for use in other code.


The basic structure I am aiming for is:
	1) Pick X many points in an order.
	2) Enter those points into a Trek class.
	3) Trek class calculates the Lines between the X points, and generates sub points between.
	4) Take all of the generated points and collect data about them from the Frame class.
	5) Output data nicely so that it is ready for objective analysis.
	6) Create maps of the data / statistical analysis of the data.
	7) etc