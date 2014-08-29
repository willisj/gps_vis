
from vehicleTag import vehicleTag
import operator	

class vehicleID:
	


	# heading 	= 0	# degrees from North
	# velocity 	= (0,0,0)	#  abs(speed), x-velocity, y-velocity
	# acceleration 	= (0,0,0)	# abs(acceleration), x-acceleration, y-acceleration
	
	def __init__(self,temp_id):
		self.temp_ids = []
		self.temp_ids.insert(0,temp_id)	
		self.tags = [] # (time, tag)
		self.is_sorted = True;	

	def add_tag(self,tag_time,gps_position=None,meters_position=None):
			
		tag = None;
		
		if not gps_position == None:
			tag = vehicleTag(self.temp_ids[0],tag_time,gps_position=gps_position)
		elif not meters_position == None:
			tag = vehicleTag(self.temp_ids[0],tag_time, meters_position=meters_position)

		self.tags.insert(0,(tag_time,tag))
		self.is_sorted = False;

	def sort_tags(self):
		self.tags.sort(key=operator.itemgetter(0))
		self.is_sorted = True
		
	def get_tags_in_slice(self,start,duration):
		if( not self.is_sorted):
			self.sort_tags()

		selected_slice = []
		for time,tag in self.tags:
			if time > start + duration: 
				break
			if time > start:
				selected_slice.append(tag)
				
		return selected_slice
		
	def get_time_bounds(self):
		if len(self.tags) == 0:
			return None
		
		if not self.is_sorted:
			self.sort_tags()
			
		return (self.tags[0][0],self.tags[len(self.tags)-1][0])

	def thin(self,thin_factor):
			
		for i in reversed(range (0,len(self.tags))):
			if not i % thin_factor == 0:
				self.tags.pop(i)

	def getStr(self):
		return  "{vehicleID -" 	\
			+ "temp_ids: "+str(self.temp_ids) \
			+ ", tags:"+str(self.tags)
			#+ ", tags:"+str(len(self.tags))

	def __str__(self):
		return self.getStr()
			
	
	def __repr__(self):
		return self.getStr()
