import csv
import os
import numpy as np
import Data


###DBD Parser###

var_dict = {'m_present_time': 584,
			'm_gps_lat': 513,
			'm_gps_lon': 514,
			'm_depth': 449}

def printDBD(filename):
	'''returns a nicer looking version of the DBD file for testing/working with'''

	fff      = open(filename, 'rb')

	for i, line in enumerate(fff):
		if i == 14:
			var_list = line.split(' ') #this puts all of the variable names in a list
			var_list.pop()             #some endline characters at the back of this list

		if i == 15:
			type_list = line.split(' ') #this is the value-type for each variable
			type_list.pop()             #same as before, pop endline characters
			var_list = [[var_list[j], type_list[j]] for j in range(len(var_list))]

		if i == 17:
			val_list = line.split(' ') #this is the actual value for each variable
			val_list.pop()
			return_list = [var_list[j].append(val_list[j]) for j in range(len(var_list))]

	return var_list

def DBDparseLine(line):
	val_list = line.split(' ')
	val_list.pop()

	return_dict = {}
	#gets a dictionary of the values we want
	for key in var_dict.keys(): return_dict[key] = val_list[var_dict[key]]

	return return_dict

def saveData(xs, ys, save_name='test.csv'):
	with open(save_name, 'wb') as myfile:
		wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
		for z in zip(xs, ys):
			wr.writerow(z)



def parseDBD(filename):

	fff    = open(filename, 'rb')
	points = []
	for i, line in enumerate(fff):
		if i > 16:
			point = DBDparseLine(line)
			flag = True
			for value in point.values():
				if value in ["NaN", "69696969"]:
					flag = False
			if flag:
				point['m_gps_lat'] = float(point['m_gps_lat'])/100.
				point['m_gps_lon'] = float(point['m_gps_lon'])/100.
				point['m_depth']   = float(point['m_depth'])
				points.append(point)

	return points

###END DBD Parser###

#formatting stuff, its kind of nasty and preliminary set up of the 
#csv files can be neccessary to get rid of unneccesary titles etc.
def readCSV(filedir):
	return_dicts = []
	with open(filedir, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

		keys = reader.next()[0].split(',') #the first row determines the keys

		while True:
			try:
				row = reader.next()
				if any(field.strip(',') for field in row): #checks if its a blank row
					row_dict = {}                          #creates a blank dictionary
					split_row = row[0].split(',')          #breaks the values from 1 long string to a list of values
					for i in range(len(split_row)):
						row_dict[keys[i]] = split_row[i]   #matches the keys to there values and puts it in this dict.
					return_dicts.append(row_dict)          #adds the new dict to this list of dicts.
			except:
				break #breaks when the endline error is called

	return return_dicts

#reads in all CSV files in this directory
def multiReadCSV(filedir):
	return_dicts = []
	for fff in os.listdir(filedir):
			return_dicts.extend(readCSV(filedir + fff))

	return return_dicts


#parser for dealing with these really really ugly .txt files Tyler sent me.
#if bottom_only is true it only returns the 1 dict that has maximum depth for this set.
def readTXT(filedir, bottom_only=False):
	return_dicts = []
	keys         = []

	if bottom_only: bottom_dict = []; bottom = 0.0
	#since lat,lon,time are the same across all of this data I set those up here for putting them in later.
	lat          = None
	lon          = None
	time         = None

	#here is where the constant lat,lon,time variables are grabbed.
	#since im searching for specific lines the way I am, there is no need for elifs.
	txtfile = open(filedir, 'rb')
	for line in txtfile:
		#the -2 is to get rid of the \n char.
		if line[:21] == "* CAST LATITUDE (N): ":  lat = line[21:-2]
		if line[:22] == "* CAST LONGITUDE (W): ": lon = line[22:-2]
		if line[:41] == "* CAST DATE-TIME (MM/DD/YYYY HH:MM UTC): ": time = line[41:-2]	

		#this line gets the value keys from the txt file, bottom line is it is a very ugly
		#block of code, but the formatting of these files is also very ugly so
		if line[:6] == "* name":
			line = line.strip("\n")
			key  = line.strip("*").split(": ")[2]
			key  = key.split(" ")

			for i in range(len(key)):
				if (key[i].count("{") >= 1) or (key[i].count("[") >= 1):
					key = key[:i]
					break

			if key[0][-1]==",":
				keys.append(key[0][:-1])

			else:
				try: 
					key = key[0] + " " + key[1]
				except:
					key = key[0]
				key = key.strip(',').strip('\r')
				keys.append(key)

		#now to actually get the data and assign it, this part is simpler.	
		elif line[0] == " ":
			data_dict = {}
			values    = line.split() #a list of all the output data

			for i in range(len(values)):
				data_dict[keys[i]] = values[i]

			#now put the constant data in
			data_dict['Latitude']  = lat
			data_dict['Longitude'] = lon
			data_dict['TimeUTC']   = time

			return_dicts.append(data_dict)

	if len(return_dicts[-1]) <= 3:
		return_dicts.pop()
		
	if bottom_only:
		for data in return_dicts:
			ddd = float(data["Depth"])
			if ddd > bottom: 
				bottom = ddd
				bottom_dict = [data]

		return bottom_dict

	return return_dicts

#reads in all TXT files in this directory
def multiReadTXT(filedir, bottom_only=False):
	return_dicts = []
	for fff in os.listdir(filedir):
		if fff.endswith(".txt"):
			return_dicts.extend(readTXT(filedir + fff, bottom_only))

	return return_dicts

#pointstoCSV and loadPoints are different from above in that they are used
#after analysis is run and do not require complex parsing to load
def pointsToCSV(filename, points):
	'''takes Point objects and converts them to lat/lon/value lines of a csv and saves'''
	title = ['Longitude','Latitude','Value','TimeUTC']
	if points[0].timeUTC == None: title = ['Longitude','Latitude','Value']


	with open(filename, 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=" ", quotechar = ' ')
		writer.writerow(title)
		for point in points:
			writer.writerow([str(point)])


def loadPoints(filename):
	'''reads in lat/lon/value from a csvfile and converts them to Point objects'''
	return_points = []

	with open(filename, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=" ", quotechar='|')
		line  = reader.next()
		while True:
			try:
				line = reader.next()
				point = Data.Point(float(line[1]), float(line[3]), float(line[5]))
				return_points.append(point)
			except:
				break

	return return_points
