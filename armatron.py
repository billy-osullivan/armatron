# ARMATRON v1.0 Personal Augmentation Platform
# SHED TECH
# 12 Jan 2022
# Billy O Sullivan
#
#
######################
#
# ARMATRON DESCRIPTION
# The ARMATRON is a wearable computer or Personal Augmentation Platform
# The platform is based on a Raspberry Pi Zero 2. It allows the user
# to plug in i2c sensors and display the results on an OLED.
# It also has a USB C port which is planned to be used as a 'Rubber Ducky'
# USB HID interface in a future version.
#
#
# 
######################
#
# DEFAULT SCREENS DESCRIPTION
# 
# Main menu screen
# This screen by default will look for the GPS i2c device and the 4 in 1
# environmental i2c device.
# If present it will display the time and temperature on the screen. 
# It will also display the IP address of the Raspberry Pi on the local
# network.
#
#######################
#
# i2c devices and addresses
# 
# Use this command to see what is 
# plugged in and available in bash, 				sudo i2cdetect -y 1
# should show most devices
#
# BME688 4-in-1 environmental sensor				0x76 or 0x77
# PA1010D GPS receiver module 						0x10
# MLX90614-DCC Non-contact IR Temperature Sensor 	0x5a
# 11x7 LED Matrix Breakout							0x75/0x77 (cut trace)
# neokey 1*4 keypad									0x30
# Adafruit 2.23" Monochrome OLED Bonnet				0x32	
#
#########################
#
# libraries to install
#
# sudo pip3 install adafruit-blinka
# sudo pip3 install adafruit-circuitpython-seesaw
# sudo pip3 install pa1010d
# sudo pip3 install matrix11x7
# sudo pip3 install adafruit-circuitpython-mlx90614
# sudo pip3 install bme680
# sudo pip3 install netifaces
# sudo pip3 install adafruit-circuitpython-neokey

#########################
# Library Imports
#
import board
from board import SCL, SDA, D4
import busio as io
import time
import sys
import math
import csv
from math import radians, cos, sin, asin, sqrt
import digitalio
from PIL import Image, ImageDraw, ImageFont
# OLED library
import adafruit_ssd1305
# library for the infrared sensor MLX90614-DCC
import adafruit_mlx90614
# library to get IP address easily
import netifaces
# gps library
from pa1010d import PA1010D
# 4 in 1 air quality sensor
import bme680
# LED matrix i2c library
from matrix11x7 import Matrix11x7
# neo pixels library
from adafruit_neokey.neokey1x4 import NeoKey1x4


logfile = open("logfile.txt", "w")


##########################
# i2c sensors
#
# Try to initialize i2c sensors. Use try statements to handle
# sensors that are not plugged in
# add any additional sensors that you want to use in here
# in order to initialise them
#
# Make a boolean variable for each device to make the correct
# bitmaps appear
#

global ledchip
global locchip
global envirochip
global infrachip

#
# neo pixels keypad
i2c_bus = board.I2C()
neokey = NeoKey1x4(i2c_bus, addr=0x30)
#
# gps sensor setup

logfile.write("sensor search")

try:
	gps = PA1010D()
	
	result = gps.update()
	if result == True:
		locchip = True	
except:
	logfile.write("gps sensor not available on initial search")
	locchip = False
#
# air sensor setup 
try:	
	airsensor = bme680.BME680()
	airsensor.set_humidity_oversample(bme680.OS_2X)
	airsensor.set_pressure_oversample(bme680.OS_4X)
	airsensor.set_temperature_oversample(bme680.OS_8X)
	airsensor.set_filter(bme680.FILTER_SIZE_3)
	airsensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
	airsensor.set_gas_heater_temperature(320)
	airsensor.set_gas_heater_duration(150)
	airsensor.select_gas_heater_profile(0)
	# set an initial value for temp until sensor is initialised
	stattemp = 100.00
	envirochip = True
	logfile.write("environmental sensor available on initial search")
except:
	logfile.write("environmental sensor not available on initial search")
	print("")
	envirochip = False
#
# LED matrix chip setup code
try:
	matrix11x7 = Matrix11x7()
	matrix11x7.set_brightness(0.5)
	ledchip = True
	logfile.write("led matrix chip available on initial search")
except:
	logfile.write("led matrix chip not available on initial search")
	ledchip = False
#
# infrared sensor setup code
try:
	i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
	mlx = adafruit_mlx90614.MLX90614(i2c)
	infrachip = True
	logfile.write("infrared thermometer available on initial search")
except:
	logfile.write("infrared thermometer not available on initial search")
	infrachip = False

###############################
#
# this is the menu selection
# buttons for use
#

#######################
# display setup code

logfile.write("setting up display")

# peripheral params for display
# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(D4)
# Create the I2C interface.
i2c = io.I2C(SCL, SDA)
# Create the SSD1305 OLED class.
# The first two parameters are the pixel width and pixel height. Change these
# to the right size for your display!
disp = adafruit_ssd1305.SSD1305_I2C(128, 32, i2c, reset=oled_reset)
# Clear display.
disp.fill(0)
disp.show()
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)



# this will scan for button presses once buttons are ready
# in order to call code for specific sensors
#
# lines of text, lines need 15 pixels space (y value)
#

def home():

	# Draw a black filled box to clear the image.
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	# Draw some shapes.
	# First define some constants to allow easy resizing of shapes.
	padding = -2
	top = padding
	bottom = height-padding
	# Move left to right keeping track of the current x position for drawing shapes.
	x = 0
	# Load default font.
	font = ImageFont.load_default()
	
	logfile.write("home function")

	neokey.pixels[0] = 0x000000
	neokey.pixels[1] = 0x000000
	neokey.pixels[2] = 0x000000
	neokey.pixels[3] = 0x000000
		

	airButton = 'na'
	locButton = 'na'
	infraButton = 'na'
	lightButton = 'na'

	#
	# a better way to do this definitely exists!!!
	# it has to because this sucks!!!!
	# code wont allow both the light and the thermometer to work at the moment
	# this is because i like to use the far right socket for these devices 
	# due to their size.
	#  

	logfile.write("setting up buttons layout and bitmap order")

	if locchip == True and envirochip == False and ledchip == False and infrachip == False:
		locButton = 'keypos1'
		airButton = 'na'
		infraButton = 'na'
		lightButton = 'na'
	if locchip == False and envirochip == True and ledchip == False and infrachip == False:
		airButton = 'keypos1'
		locButton = 'na'
		infraButton = 'na'
		lightButton = 'na'
	if locchip == True and envirochip == True and ledchip == False and infrachip == False:
		locButton = 'keypos1'
		airButton = 'keypos2'
		infraButton = 'na'
		lightButton = 'na'
	#
	if locchip == False and envirochip == False and ledchip == True and infrachip == False:
		lightButton = 'keypos1'
		infraButton = 'na'
		locButton = 'na'
		airButton = 'na'
	if locchip == True and envirochip == False and ledchip == True and infrachip == False:
		lightButton = 'keypos2'
		locButton = 'keypos1'
		infraButton = 'na'
		airButton = 'na'
	if locchip == False and envirochip == True and ledchip == True and infrachip == False:
		lightButton = 'keypos2'
		airButton = 'keypos1'
		infraButton = 'na'
		locButton = 'na'
	if locchip == True and envirochip == True and ledchip == True and infrachip == False:
		lightButton = 'keypos3'
		airButton = 'keypos1'
		infraButton = 'na'
		locButton = 'keypos2'
	#
	if locchip == False and envirochip == False and ledchip == False and infrachip == True:
		infraButton = 'keypos1'
		lightButton = 'na'
		locButton = 'na'
		airButton = 'na'
	if locchip == True and envirochip == False and ledchip == False and infrachip == True:
		infraButton = 'keypos2'
		locButton = 'keypos1'
		lightButton = 'na'
		airButton = 'na'
	if locchip == False and envirochip == True and ledchip == False and infrachip == True:
		infraButton = 'keypos2'
		airButton = 'keypos1'
		lightButton = 'na'
		locButton = 'na'
	if locchip == False and envirochip == False and ledchip == True and infrachip == True:
		infraButton = 'keypos2'
		lightButton = 'keypos1'
		airButton = 'na'
		locButton = 'na'
	if locchip == True and envirochip == True and ledchip == False and infrachip == True:
		lightButton = 'na'
		airButton = 'keypos1'
		infraButton = 'keypos3'
		locButton = 'keypos2'
	if locchip == False and envirochip == True and ledchip == True and infrachip == True:
		lightButton = 'keypos2'
		airButton = 'keypos1'
		infraButton = 'keypos3'
		locButton = 'na'
	if locchip == True and envirochip == False and ledchip == True and infrachip == True:
		lightButton = 'keypos2'
		airButton = 'na'
		infraButton = 'keypos3'
		locButton = 'keypos1'
	if locchip == True and envirochip == True and ledchip == True and infrachip == True:
		locButton = 'keypos2'
		airButton = 'keypos3'
		infraButton = 'keypos4'
		lightButton = 'keypos1'


	gps = PA1010D()

	neokey.pixels[0] = 0x800080
	neokey.pixels[1] = 0xFFFFFF
	neokey.pixels[2] = 0xFFFF00
	neokey.pixels[3] = 0x008000

	while True:
		
		draw.rectangle((0, 0, width, height), outline=0, fill=0)

		logfile.write("get ip address")
		try:
			# get ip address
			addrs = netifaces.ifaddresses('wlan0')
			ipaddress = addrs[netifaces.AF_INET][0]['addr']
			
		except:
			ipaddress = 'not found'
		draw.text((x, top + 0), "IP: " + ipaddress, font=font, fill=255)

		# gps main screen data
		if locchip == True:
			try:
				result = gps.update()
				if result == True:
					gpstime = str(gps.timestamp)
					draw.text((x, top + 8), "Time: " + gpstime.split(".")[0], font=font, fill=255)
			except Exception as e:
				logfile.write(str(e))

		# air sensor main screen data
		if envirochip == True:
			try:
				if airsensor.get_sensor_data():
					temp = "{0:.2f}".format(airsensor.data.temperature)
					stattemp = "{0:.2f}".format(airsensor.data.temperature)
					draw.text((x, top + 16), str(temp) + " C", font=font, fill=255)
			except:
				logfile.write("environmental sensor problem")
			
		if neokey[0] and lightButton == 'keypos1':
			neokey.pixels[0] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[0] = 0x800080
			light()
		if neokey[0] and airButton == 'keypos1':
			neokey.pixels[0] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[0] = 0x800080
			enviro()
		if neokey[0] and locButton == 'keypos1':
			neokey.pixels[0] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[0] = 0x800080
			gpsfun()
		if neokey[0] and infraButton == 'keypos1':
			neokey.pixels[0] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[0] = 0x800080
			infra()
		# key 2
		if neokey[1] and lightButton == 'keypos2':
			neokey.pixels[1] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[1] = 0xFFFFFF
			light()
		if neokey[1] and airButton == 'keypos2':
			neokey.pixels[1] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[1] = 0xFFFFFF
			enviro()
		if neokey[1] and locButton == 'keypos2':
			neokey.pixels[1] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[1] = 0xFFFFFF
			gpsfun()
		if neokey[1] and infraButton == 'keypos2':
			neokey.pixels[1] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[1] = 0xFFFFFF
			infra()
		# key 3
		if neokey[2] and lightButton == 'keypos3':
			neokey.pixels[2] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[2] = 0xFFFF00
			light()
		if neokey[2] and airButton == 'keypos3':
			neokey.pixels[2] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[2] = 0xFFFF00
			enviro()
		if neokey[2] and locButton == 'keypos3':
			neokey.pixels[2] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[2] = 0xFFFF00
			gpsfun()
		if neokey[2] and infraButton == 'keypos3':
			neokey.pixels[2] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[2] = 0xFFFF00
			infra()
		# key 4
		if neokey[3] and lightButton == 'keypos4':
			neokey.pixels[3] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[3] = 0x008000
			light()
		if neokey[3] and airButton == 'keypos4':
			neokey.pixels[3] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[3] = 0x008000
			enviro()
		if neokey[3] and locButton == 'keypos4':
			neokey.pixels[3] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[3] = 0x008000
			gpsfun()
		if neokey[3] and infraButton == 'keypos4':
			neokey.pixels[3] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[3] = 0x008000
			infra()

		# Display image
		disp.image(image)
		disp.show()	
		time.sleep(0.1)
	


def enviro():
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()
	z = 0
	draw.text((0, top + 0 - z), "button1 & 2 - home", font=font, fill=255)
	draw.text((0, top + 8 - z), "button 1: all enviro" , font=font, fill=255)
	draw.text((0, top + 16 - z), "button 2: air quality ", font=font, fill=255)
	try:
		while True:			
			if neokey[0] and neokey[1]:
				neokey.pixels[0] = 0xFF0000
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				neokey.pixels[1] = 0xFFFFFF
				time.sleep(.5)
				home()
			if neokey[0]:
				neokey.pixels[0] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				time.sleep(.5)
				atmosall()
			if neokey[1]:
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[1] = 0xFFFFFF
				time.sleep(.5)
				airquality()
			disp.image(image)
			disp.show()
			time.sleep(0.1)
	except Exception as e:
		logfile.write(e)
		home()
	

def gpsfun():
	logfile.write("gpsfun function")
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()

	gps = PA1010D()
	
	z = 0
	while True:
		result = gps.update(wait_for="GGA", timeout=5)
		draw.rectangle((0, 0, width, height), outline=0, fill=0)
		if result:
			latcurrent = gps.latitude
			lngcurrent = gps.longitude
			closestcity, distance, country, population = cities(latcurrent, lngcurrent)
			draw.text((0, top + 0 - z), "button1 - home", font=font, fill=255)
			draw.text((0, top + 8 - z), "city: " + closestcity, font=font, fill=255)
			draw.text((0, top + 16 - z), "distance (km): " + str(distance), font=font, fill=255)
			draw.text((0, top + 25 - z), "country: " + country, font=font, fill=255)
			draw.text((0, top + 34 - z), "population: " + str(population), font=font, fill=255)
			draw.text((0, top + 43 - z), "latitude: " + str(latcurrent), font=font, fill=255)
			draw.text((0, top + 52 - z), "longitude: " + str(lngcurrent), font=font, fill=255)
			z = z + 9
			if z > 43:
				z = 0
		if neokey[0]:
			neokey.pixels[0] = 0xFF0000
			time.sleep(.5)
			neokey.pixels[0] = 0x800080
			home()
		disp.image(image)
		disp.show()
		time.sleep(1)

def infra():
	neokey.pixels[0] = 0x800080
	neokey.pixels[1] = 0xFFFFFF
	neokey.pixels[2] = 0xFFFF00
	neokey.pixels[3] = 0x008000
	logfile.write("infra-red thermometer function")
	#i2c = io.I2C(board.SCL, board.SDA, frequency=100000)
	mlx = adafruit_mlx90614.MLX90614(i2c)
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()
	z = 0
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	draw.text((0, top + 0 - z), "button1 and 2 - home", font=font, fill=255)
	draw.text((0, top + 8 - z), "Button 1 	   - temp", font=font, fill=255)
	try:
		while True:			
			if neokey[0] and neokey[1]:
				neokey.pixels[0] = 0xFF0000
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				neokey.pixels[1] = 0xFFFFFF
				time.sleep(.5)
				home()
			if neokey[0]:
				neokey.pixels[0] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				ambiantTemp = "{:.2f}".format(mlx.ambient_temperature)
				targetTemp = "{:.2f}".format(mlx.object_temperature)
				time.sleep(1)
				draw.rectangle((0, 0, width, height), outline=0, fill=0)
				draw.text((0, top + 0 - z), "button1 and 2 - home", font=font, fill=255)
				draw.text((0, top + 8 - z), "Button 1 	   - temp", font=font, fill=255)
				draw.text((0, top + 16 - z), "Ambiant Temp: " + str(ambiantTemp), font=font, fill=255)
				draw.text((0, top + 25 - z), "TarGet Temp: " + str(targetTemp), font=font, fill=255)
			disp.image(image)
			disp.show()
			time.sleep(1)
	except Exception as e:
		logfile.write(e)
		home()

def light():
	
	logfile.write("light function")
	neokey.pixels[0] = 0x800080
	neokey.pixels[1] = 0xFFFFFF
	neokey.pixels[2] = 0xFFFF00
	neokey.pixels[3] = 0x008000
	matrix11x7 = Matrix11x7()
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()
	
	z = 0
	try:
		while True:
			draw.rectangle((0, 0, width, height), outline=0, fill=0)
			draw.text((0, top + 0 - z), "button1 and 2 - home", font=font, fill=255)
			draw.text((0, top + 8 - z), "Button 1 	   - torch", font=font, fill=255)
			draw.text((0, top + 16 - z), "Button 2 	   - flash", font=font, fill=255)
			draw.text((0, top + 25 - z), "Button 3 	   - plasma", font=font, fill=255)
			draw.text((0, top + 34 - z), "Button 4 	   - hipno", font=font, fill=255)

			if neokey[0] and neokey[1]:
				neokey.pixels[0] = 0xFF0000
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				neokey.pixels[1] = 0xFFFFFF
				time.sleep(.5)
				home()
			if neokey[0]:
				neokey.pixels[0] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				while True:
					matrix11x7.fill(1, 0, 0, 11, 7)
					matrix11x7.show()
					if neokey[0]:
						matrix11x7.fill(0, 0, 0, 11, 7)
						matrix11x7.show()
						neokey.pixels[0] = 0xFF0000
						time.sleep(.5)
						neokey.pixels[0] = 0x800080
						light()
			if neokey[1]:
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[1] = 0xFFFFFF
				while True:
					matrix11x7.fill(0.8, 0, 0, 11, 7)
					matrix11x7.show()
					time.sleep(.1)
					matrix11x7.fill(0, 0, 0, 11, 7)
					matrix11x7.show()
					time.sleep(.1)
					if neokey[1]:
						matrix11x7.fill(0, 0, 0, 11, 7)
						matrix11x7.show()
						neokey.pixels[1] = 0xFF0000
						time.sleep(.5)
						neokey.pixels[1] = 0xFFFFFF
						light()
			if neokey[2]:
				neokey.pixels[2] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[2] = 0xFFFF00
				i = 0
				while True:
					i += 2
					s = math.sin(i / 50.0) * 2.0 + 6.0

					for x in range(0, 11):
						for y in range(0, 7):
							v = 0.3 + (0.3 * math.sin((x * s) + i / 4.0) * math.cos((y * s) + i / 4.0))
							matrix11x7.pixel(x, y, v)

					time.sleep(0.01)
					matrix11x7.show()
					if neokey[2]:
						matrix11x7.fill(0, 0, 0, 11, 7)
						matrix11x7.show()
						neokey.pixels[2] = 0xFF0000
						time.sleep(.5)
						neokey.pixels[2] = 0xFFFF00
						light()
			if neokey[3]:
				neokey.pixels[3] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[3] = 0x008000
				matrix11x7.set_brightness(0.8)
				while True:
					timestep = math.sin(time.time() / 18) * 1500
					for x in range(0, matrix11x7.width):
						for y in range(0, matrix11x7.height):
							v = swirl(x, y, timestep)
							matrix11x7.pixel(x, y, v)
					time.sleep(0.001)
					matrix11x7.show()
					if neokey[3]:
						matrix11x7.fill(0, 0, 0, 11, 7)
						matrix11x7.show()
						neokey.pixels[3] = 0xFF0000
						time.sleep(.5)
						neokey.pixels[3] = 0x008000
						light()
			z = z + 9
			if z > 18:
				z = 0
			disp.image(image)
			disp.show()
			time.sleep(1)
	except Exception as e:
		logfile.write(e)
		home()

# used by the light function to make a nice light effect
def swirl(x, y, step):
	x -= (matrix11x7.width / 2.0)
	y -= (matrix11x7.height / 2.0)
	dist = math.sqrt(pow(x, 2) + pow(y, 2))
	angle = (step / 10.0) + dist / 1.5
	s = math.sin(angle)
	c = math.cos(angle)
	xs = x * c - y * s
	ys = x * s + y * c
	r = abs(xs + ys)
	return max(0.0, 0.7 - min(1.0, r / 8.0))

# used by the gpsfun function to determine closest city from a csv database
# thanks to https://simplemaps.com/data/world-cities for the awesome free database
def cities(latcurrent, lngcurrent):
	latcurrent = latcurrent
	lngcurrent = lngcurrent
	distance = 10000.000
	city = 'nowhere'
	country = 'nowhere'
	population = '0'
	with open('/home/pi/Desktop/armatron/gps/worldcities.csv', encoding="utf8") as csv_file:
		csv_reader = csv.reader(csv_file)
		linecount = 0
		for row in csv_reader:
			if linecount == 0:
				linecount += 1
			else:
				city1 = row[0]
				lat1 = float(row[2])
				lng1 = float(row[3])
				distance1 = dist(latcurrent, lngcurrent, lat1, lng1)
				if distance1 < distance:
					city = city1
					distance = distance1
					country = row[4]
					if int(row[9]) > 1:
						population = str(row[9])
					else:
						population = '0'
	return city, str(distance), country, population

# used by the gpsfun function to determine closest city from a csv database
# steps to use the formula were found here: https://medium.com/analytics-vidhya/finding-nearest-pair-of-latitude-and-longitude-match-using-python-ce50d62af546
def dist(lat1, long1, lat2, long2):
	"""
	Replicating the same formula as mentioned in Wiki
	"""
	# convert decimal degrees to radians 
	lat1, long1, lat2, long2 = map(radians, [lat1, long1, lat2, long2])
	# haversine formula 
	dlon = long2 - long1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	# Radius of earth in kilometers is 6371
	km = 6371* c
	return km

def atmosall():
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()
	z = 0

	try:
		sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
	except (RuntimeError, IOError):
		sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
	logfile.write('Calibration data:')
	for name in dir(sensor.calibration_data):
		if not name.startswith('_'):
			value = getattr(sensor.calibration_data, name)
			if isinstance(value, int):
				logfile.write('{}: {}'.format(name, value))
	# These oversampling settings can be tweaked to
	# change the balance between accuracy and noise in
	# the data.
	sensor.set_humidity_oversample(bme680.OS_2X)
	sensor.set_pressure_oversample(bme680.OS_4X)
	sensor.set_temperature_oversample(bme680.OS_8X)
	sensor.set_filter(bme680.FILTER_SIZE_3)
	sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
	logfile.write('\n\nInitial reading:')
	for name in dir(sensor.data):
		value = getattr(sensor.data, name)
		if not name.startswith('_'):
			logfile.write('{}: {}'.format(name, value))
	sensor.set_gas_heater_temperature(320)
	sensor.set_gas_heater_duration(150)
	sensor.select_gas_heater_profile(0)
	# Up to 10 heater profiles can be configured, each
	# with their own temperature and duration.
	# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
	# sensor.select_gas_heater_profile(1)
	logfile.write('\n\nPolling:')
	try:
		while True:
			draw.rectangle((0, 0, width, height), outline=0, fill=0)
			if sensor.get_sensor_data():
				temp = str(sensor.data.temperature) + " C"
				pressure  = str(sensor.data.pressure) + " hPa"
				humidity = str(sensor.data.humidity) + " RH"

				if sensor.data.heat_stable:
					airqual = str("{:.2f}".format(sensor.data.gas_resistance)) + " Ohms"
					draw.text((0, top + 0 - z), "button1 and 2 - Home", font=font, fill=255)
					draw.text((0, top + 8 - z), temp, font=font, fill=255)
					draw.text((0, top + 16 - z), pressure, font=font, fill=255)
					draw.text((0, top + 25 - z), humidity, font=font, fill=255)
					draw.text((0, top + 34 - z), airqual, font=font, fill=255)
				else:
					draw.text((0, top + 0 - z), "button1 and 2 - Home", font=font, fill=255)
					draw.text((0, top + 8 - z), temp, font=font, fill=255)
					draw.text((0, top + 16 - z), pressure, font=font, fill=255)
					draw.text((0, top + 25 - z), humidity, font=font, fill=255)
			z = z + 9
			if z > 20:
				z = 0
			disp.image(image)
			disp.show()
			if neokey[0] and neokey[1]:
				neokey.pixels[0] = 0xFF0000
				neokey.pixels[1] = 0xFF0000
				time.sleep(.5)
				neokey.pixels[0] = 0x800080
				neokey.pixels[1] = 0xFFFFFF
				time.sleep(.5)
				home()
			time.sleep(1)
			
	except Exception as e:
		logfile.write(str(e))
		home()

def airquality():
	draw.rectangle((0, 0, width, height), outline=0, fill=0)
	padding = -2
	top = padding
	bottom = height-padding
	# Load default font.
	font = ImageFont.load_default()
	z = 0

	try:
		sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
	except (RuntimeError, IOError):
		sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
	# These oversampling settings can be tweaked to
	# change the balance between accuracy and noise in
	# the data.
	sensor.set_humidity_oversample(bme680.OS_2X)
	sensor.set_pressure_oversample(bme680.OS_4X)
	sensor.set_temperature_oversample(bme680.OS_8X)
	sensor.set_filter(bme680.FILTER_SIZE_3)
	sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
	sensor.set_gas_heater_temperature(320)
	sensor.set_gas_heater_duration(150)
	sensor.select_gas_heater_profile(0)
	# start_time and curr_time ensure that the
	# burn_in_time (in seconds) is kept track of.
	start_time = time.time()
	curr_time = time.time()
	burn_in_time = 300
	burn_in_data = []
	try:
		# Collect gas resistance burn-in values, then use the average
		# of the last 50 values to set the upper limit for calculating
		# gas_baseline.
		
		while curr_time - start_time < burn_in_time:
			curr_time = time.time()
			if sensor.get_sensor_data() and sensor.data.heat_stable:
				gas = sensor.data.gas_resistance
				burn_in_data.append(gas)
				logfile.write('Gas: {0} Ohms'.format(gas))
				draw.rectangle((0, 0, width, height), outline=0, fill=0)
				draw.text((0 - z, top + 0 ), "button1 and 2 - Home", font=font, fill=255)
				draw.text((0 - z, top + 8 ), "Wait for 5 mins: getting data", font=font, fill=255)
				disp.image(image)
				disp.show()
				time.sleep(1)
				z = z + 10
				if z > 50:
					z = 0
				if neokey[0] and neokey[1]:
					neokey.pixels[0] = 0xFF0000
					neokey.pixels[1] = 0xFF0000
					time.sleep(.5)
					neokey.pixels[0] = 0x800080
					neokey.pixels[1] = 0xFFFFFF
					time.sleep(.5)
					home()

		gas_baseline = sum(burn_in_data[-50:]) / 50.0

		# Set the humidity baseline to 40%, an optimal indoor humidity.
		hum_baseline = 40.0

		# This sets the balance between humidity and gas reading in the
		# calculation of air_quality_score (25:75, humidity:gas)
		hum_weighting = 0.25
		z=0
		while True:
			if sensor.get_sensor_data() and sensor.data.heat_stable:
				gas = sensor.data.gas_resistance
				gas_offset = gas_baseline - gas

				hum = sensor.data.humidity
				hum_offset = hum - hum_baseline

				# Calculate hum_score as the distance from the hum_baseline.
				if hum_offset > 0:
					hum_score = (100 - hum_baseline - hum_offset)
					hum_score /= (100 - hum_baseline)
					hum_score *= (hum_weighting * 100)

				else:
					hum_score = (hum_baseline + hum_offset)
					hum_score /= hum_baseline
					hum_score *= (hum_weighting * 100)

				# Calculate gas_score as the distance from the gas_baseline.
				if gas_offset > 0:
					gas_score = (gas / gas_baseline)
					gas_score *= (100 - (hum_weighting * 100))

				else:
					gas_score = 100 - (hum_weighting * 100)

				#str("{:.2f}".format(sensor.data.gas_resistance))
				# Calculate air_quality_score.
				air_quality_score = hum_score + gas_score
				draw.rectangle((0, 0, width, height), outline=0, fill=0)
				draw.text((0, top + 0 - z), "button1 and 2 - Home", font=font, fill=255)
				draw.text((0, top + 8 - z), "gas: " + str("{:.2f}".format(gas)) , font=font, fill=255)
				draw.text((0, top + 16 - z), "Humidity: " + str("{:.2f}".format(hum)) , font=font, fill=255)
				draw.text((0, top + 25 - z), "air quality %: " + str("{:.2f}".format(air_quality_score)) , font=font, fill=255)
				disp.image(image)
				disp.show()
				logfile.write('Gas: {0:.2f} Ohms,humidity: {1:.2f} %RH,air quality: {2:.2f}'.format(
					gas,
					hum,
					air_quality_score))

				if neokey[0] and neokey[1]:
					neokey.pixels[0] = 0xFF0000
					neokey.pixels[1] = 0xFF0000
					time.sleep(.5)
					neokey.pixels[0] = 0x800080
					neokey.pixels[1] = 0xFFFFFF
					time.sleep(.5)
					home()
				time.sleep(1)

	except Exception as e:
		logfile.write(e)
		home()


home()