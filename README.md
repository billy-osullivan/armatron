ARMATRON v1.0 Personal Augmentation Platform
 SHED TECH
 12 Jan 2022
 Billy O Sullivan

On your raspberry pi, plae a directory called 'armatron' on the Desktop.
In there place the armatron.py code. Also create a directory for the GPS CSV file in there.
The directory map will look like this - 
'home/pi/Desktop/armatron/gps/'
In the GPS directory place the worldcities.csv file


 ARMATRON DESCRIPTION
 The ARMATRON is a wearable computer or Personal Augmentation Platform
 The platform is based on a Raspberry Pi Zero 2. It allows the user
 to plug in i2c sensors and display the results on an OLED.
 It also has a USB C port which is planned to be used as a 'Rubber Ducky'
 USB HID interface in a future version.


 


 DEFAULT SCREENS DESCRIPTION
 
 Main menu screen
 This screen by default will look for the GPS i2c device and the 4 in 1
 environmental i2c device.
 If present it will display the time and temperature on the screen. 
 It will also display the IP address of the Raspberry Pi on the local
 network.


 i2c devices and addresses
 
 Use this command to see what is 
 plugged in and available in bash, 				sudo i2cdetect -y 1
 should show most devices

 BME688 4-in-1 environmental sensor				0x76 or 0x77
 PA1010D GPS receiver module 						0x10
 MLX90614-DCC Non-contact IR Temperature Sensor 	0x5a
 11x7 LED Matrix Breakout							0x75/0x77 (cut trace)
 neokey 1*4 keypad									0x30
 Adafruit 2.23" Monochrome OLED Bonnet				0x32	



 libraries to install

 sudo pip3 install adafruit-blinka
 sudo pip3 install adafruit-circuitpython-seesaw
 sudo pip3 install pa1010d
 sudo pip3 install matrix11x7
 sudo pip3 install adafruit-circuitpython-mlx90614
 sudo pip3 install bme680
 sudo pip3 install netifaces
 sudo pip3 install adafruit-circuitpython-neokey
