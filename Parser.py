import csv
import os

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
		if fff.endswith(".csv"):
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
				key = key.strip(',')
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

def writeCSV(lon, lat, values, save_name):
	with open(save_name, 'w') as csvfile:
		writer = csv.writer(csvfile, delimiter=',',
							quotechar='|', quoting=csv.QUOTE_MINIMAL)

		writer.writerow(['longitude'] + ['latitude'] + ['Surface Salinity (PSS78)'])
		for j in range(len(lat)-1):
			for i in range(len(lat[0])-1):
				writer.writerow([str(lon[j][i])] + [str(lat[j][i])] + [str(values[j][i])])

