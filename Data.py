import cdf

class Data:
	#data attribute setup
	def __init__(self):

		self.attr = {"latitude":         None,
					 "longitude":        None,
					 "depth":            None,
					 "surface salinity": None,
					 "bottom salinity":  None,
					 "surface oxygen" :  None,
					 "bottom oxygen":    None}
		
	def toCDF(self, filename):
		#create a blank cdf file
		new_file = cdf.archive()
		for key in self.attr.keys():
			new_file[key] = self.attr[key]

		

