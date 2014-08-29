from Tkinter import *
import operator
from vehicleTag import vehicleTag
class interface:
	
	def __init__(self,screen_width=800,screen_height=600,slice_width_ms = 100, border = 20, point_rad=4):
		
		
		# Class Variable Init
		time_controls = False;
		self.slice_width_ms = slice_width_ms
				
		self.start_time = self.stop_time = self.meters_per_square = None
		
		self.vehicle_ids = dict()
		self.slices = dict()
		
		self.slices_sorted = True
		
		self.cur_slice = 0
		
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.half_width = screen_width/2
		self.half_height = screen_height/2

		self.border = border
		self.point_rad = point_rad

		self.track_id= ''
		
		# Create master Tk object (main window)
		self.master = Tk()
		self.master.title("GPS Visualizer")
		self.canvas = Canvas(self.master, width=screen_width, height=screen_height)
		
		# variable text  
		self.pos_text = StringVar() # gps location of center/tracked
		

		# Time Constants
		# time in microseconds (since 00:00:00 UTC 1, JANUARY, 2004)
		# 1 second == 1000000 microseconds
		self.second = 1000000
		self.milisecond = 1000
		self.slice_width_micro_seconds = self.slice_width_ms * self.milisecond
		
		# initial grid size
		self.init_pixels_per_grid_square = 25
		self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 1000.0
		print "ppm" + str(self.scale_pixelsPerMeter)

	# draw the center crosshair
	def center_crosshair(self, crosshair_radius):	
		#draw cross-hairs
		self.canvas.create_line(	\
			self.half_width - crosshair_radius,\
			self.half_height,	\
			self.half_width + crosshair_radius,\
			self.half_height, \
			width=1)	#horisontal
			
		self.canvas.create_line(	\
			self.half_width, 
			self.half_height - crosshair_radius,	\
			self.half_width,	\
			self.half_height + crosshair_radius, \
			width=1)	#vertical
			
	# draw the grid according to the current config
	def draw_grid(self):
		
		if self.meters_per_square == None:
			meters_per_square = self.init_pixels_per_grid_square / self.scale_pixelsPerMeter
			meters_per_square = int(meters_per_square)
		else:
			meters_per_square = self.meters_per_square
			
		self.pixels_per_grid_square = meters_per_square * self.scale_pixelsPerMeter
		

		
		if self.pixels_per_grid_square <= 1:
			return;
		
		delta = 0 
		while delta < max(self.half_height, self.half_width):
			
			#vertical lines 
			self.canvas.create_line(int(self.half_width + delta), 0, int(self.half_width + delta), self.screen_height)
			self.canvas.create_line(int(self.half_width - delta), 0, int(self.half_width - delta), self.screen_height)
			
			#horisontal lines 
			self.canvas.create_line(0,int(self.half_height + delta), self.screen_width, int(self.half_height + delta))
			self.canvas.create_line(0,int(self.half_height - delta), self.screen_width, int(self.half_height - delta))
			
			delta += self.pixels_per_grid_square
		
		
	# draw the concentric circle overlay
	def relative_center_overlay(self):

		#draw circles
		largest_radius = min (self.half_width, self.half_height) -  self.border
		
		scale = 1
		radius = largest_radius * scale
		self.canvas.create_oval (self.half_width - radius, self.half_height - radius, self.half_width + radius, self.half_height + radius, width=2, fill = '')
		
		scale = .75
		radius = largest_radius * scale
		self.canvas.create_oval (self.half_width - radius, self.half_height - radius, self.half_width + radius, self.half_height + radius, width=2, dash=(3,12))
		
		scale = .5
		radius = largest_radius * scale
		self.canvas.create_oval (self.half_width - radius, self.half_height - radius, self.half_width + radius, self.half_height + radius, width=2)
		
		scale = 0.25
		radius = largest_radius * scale
		self.canvas.create_oval (self.half_width - radius, self.half_height - radius, self.half_width + radius, self.half_height + radius, width=2,  dash=(3,12))
		
		self.center_crosshair(largest_radius)


	# draw all of the tags in the list
	def draw_all(self,tags):
		x_min = x_max = y_min = y_max = None
		
		# determine the bounds of our data
		for tag in tags:
			x, y = tag.meters_position
			
			if x_min == None or x_min > x:
				x_min = x;
			if x_max == None or x_max < x:
				x_max = x;	
				
			if y_min == None or y_min > y:
				y_min = y
			if y_max == None or y_max < y:
				y_max = y

		# set the centerpoint of the data
		rel_x = x_min + ((x_max - x_min) / 2.0)
		rel_y = y_min + ((y_max - y_min) / 2.0)

		for tag in tags:
			x, y = tag.meters_position
			
			# offset for the screen width after finding the delta from relative and scaling
			x = self.half_width + (( x - rel_x ) * self.scale_pixelsPerMeter)
			y = self.half_height + (( y - rel_y ) * self.scale_pixelsPerMeter)
			
			# draw the mark
			self.canvas.create_oval (x - self.point_rad, y - self.point_rad, x + self.point_rad, y + self.point_rad,fill = vehicleTag.tag_id_colour[tag.temp_id])


	def draw_relative(self,tags,rel_tag):

		# draw the overlay
		self.relative_center_overlay()
		
		# set the centerpoint of the data
		rel_x, rel_y = rel_tag.meters_position
		
		# find the delta from the centerpoint, apply scaling then adjust for screen center
		for tag in tags:
			x, y = tag.meters_position
	
			x = self.half_width + (( x - rel_x ) * self.scale_pixelsPerMeter)
			y = self.half_height + (( y - rel_y ) * self.scale_pixelsPerMeter)
			
			# draw the mark
			self.canvas.create_oval (x - self.point_rad, y - self.point_rad, x + self.point_rad, y + self.point_rad,fill = vehicleTag.tag_id_colour[tag.temp_id])

	# redraw a given slice (or all data if in absolute)
	def redraw(self,desired_slice=0):
		
		# overwrite the previous drawing
		self.canvas.create_rectangle(0,0,self.screen_width,self.screen_height,outline="white", fill="white")

		#drawing with time_slices
		if self.time_controls:
			desired_slice = int(desired_slice)
			self.desired_slice = desired_slice
			
			# find the first(earliest) time-stamp
			if self.start_time == None:
				for temp_id in self.vehicle_ids.keys():
					vehicle_id = self.vehicle_ids[temp_id]
					min_t,max_t = vehicle_id.get_time_bounds()
					
					if not min_t == None and (self.start_time == None or self.start_time > min_t):
						self.start_time = min_t
						
					if not max_t == None and (self.stop_time == None or self.stop_time > max_t):
						self.stop_time = max_t
						
				# with valid input this shouldn't happen
				if self.start_time == None:
					print "no start time"
					return
				else: # set the range on the slider
					self.set_range((self.stop_time - self.start_time)/self.slice_width_micro_seconds)
				
			# if we haven't already pulled the tags for this slice out of the IDs
			if not desired_slice in self.slices.keys():
					start = self.start_time + (self.slice_width_micro_seconds * ( 1 + desired_slice))
					current_slice = []
					
					# for each id, request the tags in the desired time-range
					for vehicle_id in self.vehicle_ids.keys():
						current_slice += self.vehicle_ids[vehicle_id].get_tags_in_slice(start, self.slice_width_micro_seconds)
					
					#add the slice to the cache	
					self.add_slice(desired_slice,self.start_time, self.start_time + self.slice_width_micro_seconds,current_slice)	
			
			# extract the current slice
			start_time,end_time,tags = self.slices[desired_slice]
			
			
			self.canvas.create_rectangle(0,0,self.screen_width,self.screen_height,outline="white", fill="white")	
			
			self.center_crosshair(100)			
			
			self.relative_center_overlay()
			
			#find the relative (tracked) tag
			for tag in tags:
				if tag.temp_id == self.track_id: 
					self.pos_text.set("(lat,lon) = (" + str(tag.gps_position[0]) + ", " + str(tag.gps_position[1]) + ")")
					
					# draw other tags relative to this one
					self.draw_relative(tags,tag)
					break;
					
		else:	# drawing without time 
			
			self.draw_grid()
			
			all_tags = []
			
			# enumerate all tags 
			for temp_id in self.vehicle_ids.keys():
				for time, tag in (self.vehicle_ids[temp_id].tags):
					all_tags.append(tag)  # get the tag, not time 
				
			# draw enumerated tags
			self.draw_all(all_tags)
		
		# have the canvas update
		self.canvas.update_idletasks
	
	# set the current zoom level
	def set_zoom(self,text,tags = None):
		print text

		if text == '5 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 5.0
		elif text == '10 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 10.0
		elif text == '25 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 25.0
		elif text == '50 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 50.0
		elif text == '100 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 100.0
		elif text == '300 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 300.0
		elif text == '500 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border)/ 500.0
		elif text == '1000 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border) / 1000.0
		elif text == '2000 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border) / 2000.0
		elif text == '5000 m':
			self.scale_pixelsPerMeter = ( min (self.half_height , self.half_width  ) - self.border) / 5000.0	
		elif text == '5 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 5.0
		elif text == '10 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 10.0
		elif text == '25 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 25.0
		elif text == '100 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 100.0
		elif text == '300 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 300.0
		elif text == '500 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 500.0
		elif text == '1000 m^2':
			self.scale_pixelsPerMeter = self.init_pixels_per_grid_square / 1000.0
		elif text == '-FIT-':	
			if tags == None and not self.time_controls:
				tags = []
				for temp_id in self.vehicle_ids.keys():
					for time, tag in (self.vehicle_ids[temp_id].tags):
						tags.append(tag)  # get the tag, not time 
			elif tags == None and self.time_controls:
				start_time, end_time,tags = self.slices[self.slider_control.get()]
					
			# get the range of the data and make it fit!
			x_min = x_max = y_min = y_max = None
			for tag in tags:
				x, y = tag.meters_position
				
				if x_min == None or x_min > x:
					x_min = x;
				if x_max == None or x_max < x:
					x_max = x;	
					
				if y_min == None or y_min > y:
					y_min = y
				if y_max == None or y_max < y:
					y_max = y
		
			rel_x = x_min + ((x_max - x_min) / 2.0)
			rel_y = y_min + ((y_max - y_min) / 2.0)	
			
			
			largest_distance = float(max ( x_max - x_min, y_max - y_min))
			self.scale_pixelsPerMeter = min (self.screen_height - (2 * self.border) / largest_distance , self.screen_width - (2 * self.border) / largest_distance )  
		
		# redraw at the new scale
		self.redraw(0)

	# defines which ID is tracked for the relative view
	def set_track_id(self,track_id,redraw=True):
		if redraw and self.track_id != track_id:
			self.track_id = track_id
			self.redraw(self.desired_slice)
		else:
			self.track_id = track_id

	# sets up the interface for a specific mode, most iface init is done here
	def prepare_interface(self,time_controls = True):
		self.time_controls = time_controls
		if time_controls:			
			frame = Frame(height=40,width=self.screen_width)
						
			next_frame_btn = Button(frame, text="Next", command=lambda: self.slider_control.set(self.slider_control.get()+1))
			prev_frame_btn = Button(frame, text="Prev", command=lambda: self.slider_control.set(self.slider_control.get()-1))
			self.slider_control = Scale(frame, from_=0,label="Time Slice",orient="horizontal",command=lambda x: self.redraw(x))
			
			prev_frame_btn.pack(side="left")
			self.slider_control.pack(side="left")
			next_frame_btn.pack(side="left")
			frame.pack(anchor='n')
			
		stats_frame = Frame(height=self.screen_height)		
		
		self.pos_label = Label(stats_frame,  textvariable=self.pos_text)
		
		self.zoom_type = StringVar(stats_frame)
		self.zoom_type.set("1000 m") # default value

		zoom_label = Label(stats_frame,  text='Outer Ring Distance: ')
		

		if time_controls:
			zoom_label = Label(stats_frame,  text='Outer Ring Distance: ')
			self.zoom_menu = OptionMenu(stats_frame, self.zoom_type, "5 m","10 m","25 m", "50 m", "100 m","300 m","500 m","1000 m", "2000 m", "5000 m","-FIT-", command=lambda x:self.set_zoom(x))
		else:
			zoom_label = Label(stats_frame,  text='Grid Square: ')
			self.zoom_menu = OptionMenu(stats_frame, self.zoom_type, "5 m^2","10 m^2","25 m^2","100 m^2","300 m^2", "500 m^2", "1000 m^2", command=lambda x:self.set_zoom(x))
		
		zoom_label.pack(side='left')
		self.zoom_menu.pack(side="left")
		
		if time_controls:
			track_label = Label(stats_frame,  text='Track ID: ')
			track_label.pack(side='left')


			self.track_id_item = StringVar(stats_frame)
			self.track_id_item.set("center") # default value


			options = sorted(self.vehicle_ids.keys())
			options.append('center')
			
			self.track_id_item.set(options[0]) # default value
			self.set_track_id(options[0],redraw=False)
			
			self.track_id_menu = OptionMenu(stats_frame, self.track_id_item, *(options),command=lambda x:self.set_track_id(x))
			self.track_id_menu.pack(side="left")
		
		self.pos_label.pack(side="right")
		
		
		stats_frame.pack(fill='y',anchor='w')
			
		
		self.canvas.create_rectangle(0,0,self.screen_width,self.screen_height,outline="white", fill="white")
		self.canvas.pack(anchor='se',fill='both')

			
	def clear_slices(self):
		self.slices = dict()
		slices_sorted = True;
		
	def add_vehicleID(self,vid):
		self.vehicle_ids[vid.temp_ids[0]] = vid
		
	def add_slice(self,slice_id,start_time, end_time, single_slice):
		self.slices[slice_id] = (start_time, end_time,single_slice)
		slices_sorted = False

			
	def start(self):
		mainloop()
		
	def set_range(self,x):
		self.slider_control.config(to=x)
