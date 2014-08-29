import pyproj 


wgs84=pyproj.Proj(proj='utm',ellps='WGS84') # LatLon with WGS84 datum used by GPS units and Google Earth

class vehicleTag:
	
	# heading 	= 0	# degrees from North
	# velocity 	= (0,0,0)	# speed, x-velocity, y-velocity
	tag_id_available_colours = ['red','green','blue','yellow','orange','gray25','purple','red','green','blue','yellow','orange','gray25','purple','red','green','blue','yellow','orange','gray25','purple']
	tag_id_colour = dict()
	
	def __init__(self,temp_id,tag_time,gps_position=None,meters_position=None):
		self.temp_id = None
		self.time = 0;		
		self.temp_id = temp_id
		self.time = tag_time
		
		if not temp_id in vehicleTag.tag_id_colour.keys():
			vehicleTag.tag_id_colour[temp_id] = vehicleTag.tag_id_available_colours.pop()
			
		if not gps_position == None:
			self.gps_position = gps_position
			self.meters_position = (wgs84(gps_position[0],gps_position[1]))
		elif not meters_position == None:
			self.meters_position = meters_position
			self.gps_position = (wgs84(meters_position[0],meters_position[1],inverse=True))
		else:
			print "Warning: tag created without positional value"
		#print str(self)
			
	def getStr(self):
		return "{VehicleTag -  " 	\
			+ "temp_id: "+str(self.temp_id) \
			+ ", time:"+str(self.time)	\
			+ ", gps_position: "+str(self.gps_position)	\
			+ ", meters_position: "+str(self.meters_position) + "}"

	def __str__(self):
		return self.getStr()
			
	
	def __repr__(self):
		return self.getStr()
