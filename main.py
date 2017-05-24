import scipy.io
import time
from Data import *
import analysis, mapper
import numpy as np
import cmocean
import math
import datetime

#the mission .MAT files we will be working on
calib  = scipy.io.loadmat('m26_mission_calib.mat')
scimat = scipy.io.loadmat('m26_science_calib.mat')

#.MAT files are really ugly so we do some formatting and get it in list form.
mdate  = calib['mdate'][0]
mdepth = calib['m_depth'][0]
sdate  = scimat['sdate'][0]
olon   = scimat['olon'][0]
olat   = scimat['olat'][0]
temp   = scimat['s_tempR'][0]
salt   = scimat['s_sal'][0]
cdom   = scimat['s_cdom'][0]
pres   = scimat['s_press'][0]
turb   = scimat['s_turb'][0]
schl   = scimat['s_chl'][0]
rink   = scimat['sDO_rinko_R'][0]

#A quality of life function so you can view what data is in the .MAT files we can work with
def printKeys():
	print calib.keys()
	print scimat.keys()

#because a large majority of our science data is missing lat/lon/depth measurements
#we interpolated over the 'good' data we do have using time, its a bit of a mess because
#lining up 'good' data points to interp on is different in some cases
def getLocs():
	sci_size = len(sdate)
	g_sci = [i for i in range(sci_size)  if str(sdate[i]) != 'nan']  #gets indices of 'good' science points
	g_pos = [j for j in range(len(olon)) if str(olon[j])  != 'nan'] #gets indices of 'good' location data
	g_dep = [k for k in range(len(mdepth)) if (str(mdepth[k]) not in ['nan', '-1.0', '4.0']) and (str(sdate[i]) != 'nan')] #there is a lot of bad depth values to filter out here

	nlon, nlat, ndepth = np.zeros(sci_size), np.zeros(sci_size), np.zeros(sci_size) #arrays for our new, interped locations of 'good' science data

	g_dates    = [mdate[i] for i in g_pos]              #pulls the time data for our 'good' location data
	immm       = np.argsort(g_dates)                    #sorted indices of our 'good' dates
	mdate2     = np.sort(g_dates)                        #the actual sorted dates, for interping

	gd_dates   = [mdate[i] for i in g_dep]      #same as above but need a seperate one for depths, weird
	innn       = np.argsort(gd_dates)           
	mdate3     = np.sort(gd_dates)


	sdepth     = [ [ mdepth[i] for i in g_dep ][j] for j in innn] #get the good depths
	slon       = [ [ olon[i] for i in g_pos ][j] for j in immm ] #get the good longitudes and then sort them by immm
	slat       = [ [ olat[i] for i in g_pos ][j] for j in immm ] #get the good latitudes and then sort them by immm

	for i in g_sci:
		nlon[i]   = np.interp(sdate[i], mdate2, slon) #interp to get an estimate of location data at each 'good' science point
		nlat[i]   = np.interp(sdate[i], mdate2, slat)
		ndepth[i] = np.interp(sdate[i], mdate3, sdepth)

	return g_sci, nlon, nlat, ndepth

def getData(g_sci, nlon, nlat, ndepth):
	'''used by saveAllPoints and timeSeries to format our data into one dictionary'''
	return_dicts = []

	for i in g_sci:
		data = {'time' : sdate[i], 
				'lon'  : nlon[i],
				'lat'  : nlat[i],
				'press': pres[i],
				'temp' : temp[i],
				'cdom' : cdom[i],
				'salt' : salt[i],
				'turb' : turb[i],
				'chl'  : schl[i],
				'oxy'  : rink[i],
				'depth': ndepth[i]}
		return_dicts.append(data)

	return return_dicts

#just a condition function used in the timeSeries function below
def isGood(data):
	if data['time']-1000. < 0.: return False
	return True

#a quick, spaghetti-coded timeSeries function that shows the depths and locations of stations we choose to use
def timeSeries():
	data = getData()
	sci_time, alt_depth, sci_depth = [], [], []
	for sample in data:
		if isGood(sample):
			sci_time.append(sample['time'])
			alt_depth.append(sample['depth'])
			sci_depth.append(sample['press'])

	print 'samples: %s, %s, %s' % (len(sci_time), len(alt_depth), len(sci_depth))
	max_depth = max(max(alt_depth), max(sci_depth))
	sorted_indices     = np.argsort(sci_time)
	sorted_sci_time        = [datetime.datetime.fromtimestamp(sci_time[i]) for i in sorted_indices]

	sorted_alt_depth = [alt_depth[i] for i in sorted_indices]
	sorted_sci_depth = [sci_depth[i] for i in sorted_indices]

	#you need to adjust this bottom condition list to match the conditions for data you are choosing.
	#for example using surface data use sorted_sci_depth[i] < .5, or bottom data use the current one.
	bottom_cond = [i for i in range(len(sorted_sci_time)) if abs(sorted_alt_depth[i] - sorted_sci_depth[i]) < 5.] 

	print 'bottom_cond size: %s' % len(bottom_cond)

	red_ys  = [sorted_sci_depth[i] for i in range(len(sorted_sci_time)) if i not in bottom_cond]
	red_xs  = [sorted_sci_time[i] for i in range(len(sorted_sci_time)) if i not in bottom_cond]

	blue_ys = sorted_alt_depth
	blue_xs = sorted_sci_time

	cyan_ys = [sorted_sci_depth[i] for i in bottom_cond]
	cyan_xs = [sorted_sci_time[i] for i in bottom_cond]

	fig = pyplot.figure()
	pyplot.scatter(red_xs, red_ys, color='r', marker='.')
	pyplot.scatter(blue_xs, blue_ys, color='b', marker='.')
	pyplot.scatter(cyan_xs, cyan_ys, color='cyan', marker='.')
	pyplot.xlim((min(sorted_sci_time), max(sorted_sci_time)))
	pyplot.ylim((pyplot.ylim()[::-1][0],-10.))
	pyplot.xlabel(r'$Time$')
	pyplot.ylabel(r'$Pressure\ (hPa)$')
	pyplot.show()

def saveAllPoints():
	'''this function finishes cleaning up all of our data and saves it, while it may appear like we do an
	inefficient amount of cleaning and data-type conversions it actually makes it easier when we
	save our data to .csv files. This only really needs to be done once so that you don't re-GET
	the data every time you want to run an analysis on a specific characteristic'''
	filename = "Surface_M26\\"
	data = getData(getLocs()) #pretty inefficient stuff, but I'm only 1 man.

	#set up our Points objects to store our stations, convienent here because
	#Points has a built-in save function.
	salinity    = Points([])
	temperature = Points([])
	cdom_points = Points([])
	turbidity   = Points([])
	chlor       = Points([])
	oxy_rinko   = Points([])

	for sample in data:
		#the condition here needs to be changed depending on what data you wish to work with
		#sample['press'] <= .5 only uses stations within .5 meters of the surface.
		if sample['press'] <= .5 and (int(sample['lon']) != 0):
			salinity.append( Point(sample['lon'], sample['lat'], value=sample['salt']) )
			temperature.append( Point(sample['lon'], sample['lat'], value=sample['temp']) )
			cdom_points.append( Point(sample['lon'], sample['lat'], value=sample['cdom']) )
			turbidity.append( Point(sample['lon'], sample['lat'], value=sample['turb']) )
			chlor.append( Point(sample['lon'], sample['lat'], value=sample['cdom']) )
			oxy_rinko.append( Point(sample['lon'], sample['lat'], value=sample['oxy']) )

	#utilize our save feature and save all of our data as nice .csv's that can easily
	#be read and written using our Points object now. 
	salinity.save(filename + "salinity.csv")
	temperature.save(filename + "temperature.csv")
	cdom_points.save(filename + "cdom.csv")
	turbidity.save(filename + "turbidity.csv")
	oxy_rinko.save(filename + "oxygen.csv")
	chlor.save(filename + "chlorophyll.csv")

def main():
	#set up our variables before we start
	bw = 1
	dn = .005
	lin_bool   = False
	data_label = r'$\mathrm{Salinity}\ (PSS78)}$'
	data_type  = "Surface\ Salinity\ Content"
	map_title  = "Mission 26 Surface salinity"
	color_map  = cmocean.cm.haline
	model = analysis.pentaspherical

	#specifiy which data we want to run an interpolation on and get some information from it
	stations = Points(filename = "M26\\salinity.csv")
	lons, lats = stations.lonArray(), stations.latArray()
	mmm      = stations.mean()
	vvv      = stations.var()

	print stations.size() #just so I can see it


	#calculate our max inter-station range using our distance matrix.
	max_range = np.amax(stations.distMatrix())
	print stations.mean(), stations.var()

	#calculate seimvariance, plot it, and get our optimized model for use later.
	funct = mapper.plotSemivar(stations, model, max_range, bw, linear=lin_bool, title=r'$Semivariogram\ of\ %s$' % (data_type), mlabel="Model (Pentaspherical)") #plot the semivariance

	#plot the histogram of our data so we can see its distribution
	mapper.plotHistogram(stations, 50, xlabel=data_label,
				 title=r'$\mathrm{Distribution\ of\ %s:}\ \mu=%.6f,\ \sigma^2=%.6f$' % (data_type, stations.mean(), stations.var())) #plot the distribution of our station data

	bounds, xg, yg, points = analysis.getKrieged(stations, dn, funct, max_range) #get our interped points and our grid values
	shape = (len(yg)-1, len(yg[0])-1)

	#when a point is 'bad', i.e it is an outlier or doesn't have enough neighbors, we set it to np.NaN
	#so when plotting our final map we can mask the bad data out and only work with good data points.
	clean_points = points.getNonNan()
	print clean_points.mean(), clean_points.var()

	#plot the histogram of our interpolated data so we can see its distribution for comparison.
	mapper.plotHistogram(clean_points, 50, xlabel=data_label,
				 title=r'$\mathrm{Distribution\ of\ Interpolated\ %s:}\ \mu=%.6f,\ \sigma^2=%.6f$' % (data_type, clean_points.mean(), clean_points.var()))

	#plot our final interpolated map with the values returned by getKrieged
	mapper.objectiveMap(bounds, xg, yg, points.valueMatrix(shape), color_map, [lons, lats],
						title=map_title,
						cbar_label = data_label)

main()