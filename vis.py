#!/usr/bin/python

from Tkinter import *
import tkFileDialog
import sys, time

import random


from vehicleID import vehicleID
from interface import interface

#upstream change 

#########################
## BEGIN CONFIGURATION


## DISPLAY
screen_width = 800
screen_height = 600

point_rad = 5	# marker radius
border =  20	# width of whitespace while auto-scaling

thin_factor = 1	# every one in X points will be drawn


## FILE INPUT
# These are the expected fields, not all are used and column order does not matter
fields = ("time, temp_id, speed, latitude, longitude, altitude, heading").split(", ")
field_count = len(fields)

# to note which fields are textual
non_numeric_fields = ('temp_id').split(", ")


## TIMING
slice_width_ms = 100

# time in microseconds (since 00:00:00 UTC 1, JANUARY, 2004)
# 1 second == 1000000 microseconds
second = 1000000
milisecond = 1000
	
## END CONFIGURATION
#########################


# == GENERATED CONFIG VALUES  == 

half_width = screen_width/2
half_height = screen_height/2

# == END GENERATED  == 

random.seed()

iface = interface(screen_width=screen_width, screen_height=screen_height, border=border, point_rad=point_rad)
slider_control = None

# utility function
def is_number(s):
    try:
        float(s)
        return True or s.isdigit()
    except ValueError:
        return False

# help dialogue
def help_dia():
	#	+ "\n\t-w <file>\toutput file (used with -s) (NYI)"	\
	#	+ "\n\t-p \tread from input pipe (NYI)"	\
	#	+ "\n\t-s \tspoof other vehicles on this same path (NYI)"	\


	print "Usage:\n\t./vis.py [OPTIONS]"	\
	+ "\n\t--help (-h)\tthis help dialog"	\
	+ "\n\t-f <file>\tinput csv \n\t\tformat:\n\t\t\t" + ", ".join(fields) \
	+ "\n\t-r <file>\trelative positioning with time-slicing"	\
	+ "\n\t-t <num>\tonly print one in 'num' packets"	\
	+ "\n\t-d \topen file dialog"\
	+ "\n\t-o \toverlay test"
	
	exit()


def from_file(file_arg, time_slice=False,spoof=False,target=None):
	
	
	vehicle_ids = dict()
	line_no = 0
	
	field_list = fields
	
	# iterate over lines in the file
	for line in open(file_arg):
		line_no += 1
		
		# split the csv
		line_parts = line.split(", ")

		# check that this line has the correct number of items
		if  len(line_parts) != field_count:
			print 'invalid line (err1)\n\t('+ str(line_no) +') ' + line
			print str(line_parts)
			exit()
			
		
		# check if this is a header row
		if line_parts[0] in field_list:
			field_list = line_parts
			continue
		
		# check to make sure all fields validate
		for i in range (0,field_count):
			if not is_number(line_parts[i]) and  field_list[i] not in non_numeric_fields: 
				print 'invalid line (err2)\n\t('+ str(line_no) +') ' + line
				print "\t\tField: " + line_parts[i]
				exit()
		
		# extract the values
		temp_id = line_parts[fields.index("temp_id")]
		time = int(line_parts[fields.index("time")])
		lat = float(line_parts[fields.index("latitude")])
		lon = float(line_parts[fields.index("longitude")])
		pos = (lon,lat)
		
		# if this is the first time seeing the vehicle_id
		# we need to create a new vehicleID object for it
		if temp_id not in vehicle_ids.keys():
			vehicle_ids[temp_id] =  vehicleID(temp_id)
			iface.add_vehicleID(vehicle_ids[temp_id])
		
		#finally we add the tag information to the ID
		vehicle_ids[temp_id].add_tag(time,gps_position=pos)	
	
	# end of reading lines
	
	# if we are thinning the data 
	if thin_factor > 1:
		for temp_id in vehicle_ids.keys():
			vehicle_ids[temp_id].thin(thin_factor)
			
	# let the interface initialize 
	iface.prepare_interface(time_slice)
	
	# draw the first slice/the whole picture
	iface.redraw()	
	
	# hand the thread to TkInter
	iface.start()
	
# Open a file dialog
def file_dialog():
	dir_opt = options = {}
	options['initialdir'] = '~'
	options['filetypes'] = [('csv files', '.csv'),('all files', '.*')]
	options['parent'] = w
	options['title'] = 'Open a file'

	return tkFileDialog.askopenfilename(**options)


# if being run as a script rather than imported
if __name__ == "__main__":

	# CLI Arguments
	
	pipe_in = False
	time_slicing = False
	overlay_test = False
	spoof_points = False
	
	target = None
	read_file = None
	write_file = None
	
	# parse input arguments and call methods accordingly
	cur_arg_id = 1
	while cur_arg_id < len(sys.argv):
		cur_arg = sys.argv[cur_arg_id];
		
		# HELP
		if  cur_arg== '-h' or cur_arg == '--help':
			help_dia()
			
		# FROM FILE, all trails
		elif  cur_arg== '-f' :
			read_file = sys.argv[cur_arg_id + 1]
			cur_arg_id += 2
			
		# FROM FILE, Time Sliced
		elif  cur_arg== '-r' :
			read_file = sys.argv[cur_arg_id + 1]
			time_slicing = True
			cur_arg_id += 2	
			
		# FROM PIPE
		elif  cur_arg== '-p' :
			print 'Not yet implemented'
			exit()
		# set target
		elif  cur_arg== '-i' :
			target = sys.argv[cur_arg_id + 1]
			cur_arg_id += 2		
		# FILE DIALOG
		elif cur_arg == '-d':
			read_file =  file_dialog()
			cur_arg_id += 1
			
		# SPOOF POINTS
		elif cur_arg == '-s':
			spoof_points = True
			cur_arg_id += 1	
	
		# THINNING FACTOR
		elif cur_arg == '-t':
			try:
				thin_factor = int(sys.argv[cur_arg_id + 1],)
			except ValueError:
				thin_factor = 1
				print "invalid thinning factor (-t)"
			cur_arg_id += 2	
			
		# UNKNOWN ARGUMENT
		else:
			print 'Error: uknown argument "' + cur_arg + '"'
			help_dia() # calls exit() afterward
			
		from_file(read_file,time_slice = time_slicing, spoof = spoof_points,target = target)
	




