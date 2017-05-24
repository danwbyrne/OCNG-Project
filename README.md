---Idea---
	The original goal of this project was to create a program that can use mission data collected by autonomous gliders and create an accurate interpolated map of specific ocean conditions. While legacy versions used simpler methods such as Barnes Analysis and Simple Krieging, this final version uses true neighborhood Krieging.

	How Krieging works:
	While I will gloss over the gritty details of assumptions we make about our field of data the basic idea is fairly straightforward. In order, Krieging is accomplished by doing the following:
		1) Calculate the semivariance of our observations.
		2) Fit a model to this semivariance.
		3) Set up and solve a system of linear equations to calculate an expected value of a given point.
		4) repeat this for every point we want to interpolate.

	Where the semivariance is a function which represents expected variance at a given distance. To see the actual system of equations we are solving consult the wiki.

	Since we are using neighborhood Krieging our general assumption is that a prospective point's value is determined by only its neighbors and not every observation we have available (this would be simple Krieging, which is not very good for data spread over a large area). While on the upside we will get a better estimate about points, the downside is we now have to invert a different semivariance matrix for each distinct point, which is VERY taxing. With running times of certain data to take several hours a plot.

	Running time is determined by several things, in order of importance they are:
		1. Number of stations: The single most important thing when considering run-time. The number of stations used in determining a 'neighborhood' will change running time significantly since matrix inversion is very taxing and each new station increases our matrix size.
		2. Resolution: the variable 'dn' in our kriegAnalysis function determines how spaced our gridpoints are. For a full analysis I will typically use a value of .005, while for testing lower values such as .1 or even .5 significantly speed it up. 
		3. Bounds: The more spread out your data is the longer it will take to generate the interpolated grid. Currently we calculate our grid bounds as the floor/ceiling of our min/max values from the station data.

---data---
	









---analysis---
	This module handles all of our number-crunching. For a full breakdown of how krieging itself works refer to the 'Idea' section or check the wiki. For functions we have:

	-createGrid(bounds, dn):
		given lat/lon boundaries and a resolution scale dn returns 2 grid arrays of partitioned lat/lon coordinates. Note: ys, xs returned are each NxN

	:MODELS:
	-reduceModel(model, alpha, c0):
		this function accepts a model, an alpha value, and a max-variance c0. Since (most) of our models accept 3 arguements, this gets rid of 2 of them and returns a new function which only needs distance as an input. QoL function.

	-makeLinear(xs, ys):
		returns a linear regression of the data.

	-cubic, spherical, pentaspherical, guassian, sinusoidal (dist, alpha, c0):
		these functions are all of our cookie-cutter models (though it isn't all of the possible models). Alpha and c0 are used when optimizing our model (see opt) but once we have use reduceModel so we don't have to bother with 3 inputs.

	:NUMBER CRUNCHING:
	Note: If you don't understand what each of these functions is doing see the 'Idea' section as I won't be discussing WHY these functions do what they do in this section, only WHAT they do.

	-semivar(points, lag):
		given input points (really should only be used on stations) and a lag distance this function calculates the semivariance of points within the distance of each other and returns it.

	-semivariogram(points, model, bw=5):
		given input points (again, should really only be used on stations), a model we want to try and use to explain the semivariance, and a bandwidth for our lag-distances. It calculates the semivar(points, lag) for each lag point in range(0, max_range, bw) and then uses analysis.opt to find an optimal alpha value for our model and returns it.

	-opt(model, xs, ys, c0):
		takes a model and calculates the sum of residuals between it and the raw data over a large range of possible alpha values and returns the alpha value which gave the lowest error. Not necessarily the best way to find an optimized model but it works for what we need.

	-krigInterp(points, stations, model, max_range, n):
		This is the backbone of everything. This function uses station observations to interpolate a grid of points through Krieging.
		:: input ::
		points   := an custom array of points whose values we will interpolate
		stations := an array of points whose values we have observed
		model    := the model we will use for our semivariogram. This should be a reduced model which only relies on an input distance.
		max_range := max inter-station distance, used for filtering 'good' points to interpolate.
		n  := n specifies the maximum number of stations to use when solving for our interpolated value. I actually only use half as many as input, and because of such I typically set n to be ~ |stations|.

		Note: since we are dealing with data that can be 100+ miles apart we do some hand-waving magic to:
			1) reduce the amount of calculations require
			3) throw away interpolations that are too far away from observations
		 	2) increase our confidence in the data
		 the result of doing this is actually pretty nice. Prospective points which are too far away and have few neighboring observations are filtered out, while points located near a lot of neighbors and points located really close to at least one neighbor are left in.

		 We do this by going point by point and checking how many stations it has close to it with max_range/2, if it has less than |stations|/3 neighbors and it doesn't have at least one station with max_range/5 it is filtered out (we just mask it).


---mapper---
	This module handles the bulk of plotting functions. It uses matplotlib's Basemap module which enables us to easily plot landmass, rivers and latitude/longitude lines. The Basemap module also provides us with easy mapping from lat/lon coordinates to array coordinates using the latlon=True command when applying our colormesh. We have 3 functions currently:
	
	-objectiveMap(bounds, x, y, values, colormap, *args):
		handles plotting our krieged data. An example of this function being used can be found in test.py. This is typically the last thing I run when doing an interpolation.

		:: inputs :: 
		bounds := (upper-right-lon, lower-left-lon, upper-right-lat, lower-left-lat)
		x, y, values := x,y, and values are all NxN grids created by analysis.krigInterp , generally you will be using them one right after the other so not much to worry about.
		colormap := I highly reccomend using the cm.ocean colormaps created [insert who made cm.ocean, I know it is TAMU], though any colormap can be used.
		station_locs := if you want to display a marker at every station we used to create our interpolation then supply a list of (lat, lon) station coordinates.
		title, cbar_label := just used to set the titles on our plot.
		show := if set to False, it won't show the plot, useful if you want to batch run multiple interpolations without having to monitor each plot.
		save_name := if provided, saves this plot to given filename.

	-plotSemivar(stations, model, max_range, bw, *args):
		handles calculating stations semivariance and then plots and returns an optimized model. This should be done before krieging to check how well we are fitting our data and to see if we should try another model.

		:: inputs ::
		stations := station data we are using to interpolate a map.
		model := the model we want to try and fit the data too, there are a number of different choices for this, I've provided several cookie-cutter options in the analysis module. My first gotos are pentaspherical/spherical/cubic.
		max_range := the max range between any 2 stations, important since that will be our cutoff of where we can no longer predict semivariance.
		bw := bandwidth, specifices how large your intervals are when checking raw semivariance, generally keep it between 1-5.
		linear := if set to True will use a linear regression in lieu of a model provided. 
		(This seems silly as opposed to making it its own model, however due to some legacy spaghetti-coding it is easier to implement this way)
		show := set to False if you don't need to see the plot again you just need the optimized model returned.

		notes:
		if your semivariance is especially ugly and you are savy in 3rd-party statistic software such as R or JMP you can uncomment the "Parser.saveData(xs, ys)" line and save the raw semivariance as a .csv to be analyzed further. Once you have a model you are comfortable with you can implement it yourself and continue.

	-plotHistogram(stations, num_bins, *args):
		plots a histogram of our data, useful when comparing the distribution of your station data to the distribution of your krieged data. I typically plot (and save) a histogram of the raw station values AND a histogram of the krieged points.