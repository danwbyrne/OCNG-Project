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
def multiRead(filedir):
	return_dicts = []
	for file in os.listdir(filedir):
		if file.endswith(".csv"):
			return_dicts.extend(readCSV(filedir + file))

	return return_dicts