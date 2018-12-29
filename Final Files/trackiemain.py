########################################################################
#!/usr/bin/env python
# 	trackiemain.py
#	Created by: Ryan Howard
#	PERFORMANCE:
#	Python code for the Mobile Mechanic which controls the user inter-
#	face, including the lcd screen, switches and buttons, and leds. This
#	program also controls the camera and servo board used for the track-
#	ing light system. Lastly, it controls signals that are sent to the
#	Arduino via simple input pins to control the code on the other board
#	as well.
########################################################################

#Imports the GPIO library for pin numbering,time library for delays,
#numpy for some mathmatical formulas used in the camera tracking,ADS1x15
#for the ADC, the LCD library, and finally a servo library for the servo
#board chip we used in the project.
import RPi.GPIO as GPIO
import time
import numpy as np
import Adafruit_ADS1x15
import Adafruit_CharLCD as LCD
from SunFounder_PCA9685 import Servo

#initializing the adc as the ADS1015 model and assigning it to the var-
#iable adc for easy access.
adc = Adafruit_ADS1x15.ADS1015()

#Declaring a variable which will easily change the gain on the ADC, in
#this case, a gain of 1 = +/-4.096V.
GAIN = 1

#setting the GPIO mode to BCM numbering scheme
GPIO.setmode(GPIO.BCM)

#Initializing the LCD through the library and assiging it to lcd for
#easy calls to the LCD screen.
lcd = LCD.Adafruit_CharLCDPlate()

#Sets the backlight of the lcd screen to be blue
lcd.set_color(1,0,0)

#imports cv2 which is a powerful library for color tracking with the Pi
#as well as some libraries used to interface with the Picamera
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

#Debugging Options useful for testing, SHOW_IMAGE will show the capture
#of the camera,the binary filter as well as the contour filter when set
#to equal TRUE. Cannot be run from console if TRUE. VERBOSE toggles the
#console print outs of what coordinates the object is and what the
#servos should be doing if TRUE. Lastly, MOTORS controls if the motors 
#will run or not, this is useful for testing the camera tracking without
#the motors running.
SHOW_IMAGE = False 
VERBOSE = True
MOTORS = True
#HSV thresholds for color, these thresholds tell the camera what range 
#of color to track. For this program, we tracked a bright neon green
THRESHOLD_LOW = (29, 86, 6)
THRESHOLD_HIGH = (80, 255, 255)

#Variable used for determining the minimum radius of color tracking
#which can help filter out background colors of similar hue
MIN_RADIUS = 3

#Variables to declare the BCM pins of all the LEDs
BACKUP_LED = 27
CHARGE_LED = 17
MAX_LIFT_LED = 9
LED_BAR = 14

#Variables to declare all the buttons and switches in BCM
BACKUP_MODE_SWITCH = 21
STOPPER = 16
TURN_LEFT = 26
TURN_RIGHT = 5

#Variables to assign the pins for the Digital Signals to Arduino
STOPPER_SIGNAL = 4
TURN_LEFT_SIGNAL = 6
TURN_RIGHT_SIGNAL = 13
BACKUP_MODE_SIGNAL = 20

#Constants used for camera tracking
min_pwm_angle_x = 10 #minimum angle the pan servo can go in X direction
max_pwm_angle_x = 120 #maximum angle the pan servo can go in X direction
min_pwm_angle_y = 10 #minimum angle the tilt servo can go in Y direction
max_pwm_angle_y = 80 #maximum angle the tilt servo can go in Y direction
midScreenWindow = 20 #buffer error for coordinates
panStepSize = 1 # degree of change for each pan update
tiltStepSize = 1 # degree of change for each tilt update
servoPanPosition = 90 # initial pan position x
servoTiltPosition = 45 # initial tilt position y


#Setup Servo using a for loop and an array called my servo for channels
#14 and 15.
myservo = []
for i in range(14, 16):
        myservo.append(Servo.Servo(i))  # channel 14
        Servo.Servo(i).setup()
        print 'myservo%s'%i #print for debug

#setup LED OUTPUT pins and set LED_BAR to low because it is active high.
GPIO.setup(BACKUP_LED, GPIO.OUT)
GPIO.setup(CHARGE_LED, GPIO.OUT)
GPIO.setup(MAX_LIFT_LED, GPIO.OUT)
GPIO.setup(LED_BAR, GPIO.OUT)
GPIO.output(LED_BAR, 0)

#SETUP ARDUINO SIGNALS as outputs to be sent to the Arduino
GPIO.setup(STOPPER_SIGNAL, GPIO.OUT)
GPIO.setup(TURN_LEFT_SIGNAL, GPIO.OUT)
GPIO.setup(TURN_RIGHT_SIGNAL, GPIO.OUT)
GPIO.setup(BACKUP_MODE_SIGNAL, GPIO.OUT)

#SETUP INPUT PINS to be pull up resistor pins so that they are grounded
#when the buttons are pressed or switched.
GPIO.setup(BACKUP_MODE_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(STOPPER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TURN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TURN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480) #sets the camera resolution to 640x480
camera.framerate = 50 #sets the fps to 50 to help with performance
camera.hflip = True #flips the picture horizontally so its not mirrored

#captures the image
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup with a quick sleep
time.sleep(0.1)

########################################################################
#	movetop(angletop)
#	PERFORMANCE:
#	Takes an argument as the top angle and moves the servo to the speci-
#	fied angle.
########################################################################
def movetop(angletop):
	#if the angle is greater than or equal to the minimum angle and less
	#than the max angle move the servo to that angle
    if (min_pwm_angle_y <= angletop <= max_pwm_angle_y):
		
		#if motors debug option = TRUE then write the angle to the servo
		#on channel 15 which is the top servo.
		if MOTORS:
			myservo[15].write(angletop)
		#if verbose debug option is true, print out the angle to the
		#console.
		if VERBOSE:
			print str(angletop)
	#if the angle is not inbetween the min and max print an error.
    else:
        print "Servo angle must be an integer between 10 and 120.\n"
########################################################################
#	movebottom(anglebottom)
#	PERFORMANCE:
#	Takes an argument as the bottom angle and moves the servo to the
#	specified angle.
########################################################################
def movebottom(anglebottom):
	#if the angle is greater than or equal to the minimum angle and less
	#than the max angle move the servo to that angle
    if (min_pwm_angle_x <= anglebottom <= max_pwm_angle_x):
		
		#if motors debug option = TRUE then write the angle to the servo
		#on channel 14 which is the bottom servo.
		if MOTORS:
			myservo[14].write(anglebottom)
		#if verbose debug option is true, print out the angle to the
		#console.
		if VERBOSE:
			print str(anglebottom)
	#if the angle is not inbetween the min and max print an error.
    else:
        print "Servo angle must be an integer between 0 and 180.\n"

if __name__ == '__main__':
	#All the code is wrapped in a try block with an exception for key
	#board interrupt.
	try:
		#Initialization of LCD and clearing the screen to display that
		#the system is ready
		lcd.clear()
		lcd.message('Mobile Mechanic   \n     Ready      ')
		time.sleep(3)
		while True:
			#This method returns a frame  from the video stream. The 
			#frame then has an array  property, which corresponds to the
			#frame in NumPy array format
			for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
				#reads the adc on channel 1, assigns the gain to 1, and
				#assigns the number to pressurevalue variable
				pressurevalue = adc.read_adc(1,gain = GAIN)
				#if the pressure value is less than or equal to 800
				#turn on the LED_BAR and CHARGE_LED LEDs.
				if pressurevalue <= 800:
					GPIO.output(LED_BAR, 0)
					GPIO.output(CHARGE_LED, 1)
				#else turn them off
				else:
					GPIO.output(LED_BAR, 1)
					GPIO.output(CHARGE_LED, 0)
				# grab the raw NumPy array representing the image, then
				# initialize the timestamp and occupied/unoccupied text
				image = frame.array
				#copies the image and blurs it for the filter display
				image_filter = cv2.GaussianBlur(image.copy(), (3,3),0)

				#converts the image from BGR to HSV
				image_filter = cv2.cvtColor(image_filter,cv2.COLOR_BGR2HSV)
				#copies the image again to display the binar filter
				img_binary = cv2.inRange(image_filter.copy(), THRESHOLD_LOW, THRESHOLD_HIGH)
				img_binary = cv2.dilate(img_binary, None, iterations = 1)
				#copies the image again to create the contours filter
				img_contours = img_binary.copy()
				contours = cv2.findContours(img_contours, cv2.RETR_EXTERNAL, \
					cv2.CHAIN_APPROX_SIMPLE)[-2]
					
				#declares the middle of the screen to be halfway between
				#the 640x480 resolution for adjusting the motors.
				midScreenX = (640/2)
				midScreenY = (480/2)
				
				#assigns the center of the object to initialize to be
				#none and the radius to be 0	
				center = None
				radius = 0
				
				#finds the specified color and uses the slope intercept
				#formula to return the x,y coordinates of the detected
				#center or the colored object and assigns it to the 
				#variable center. if the radius is less than the
				#specified minimum radius, it insteads assigns the
				#center = None.
				if len(contours) > 0:
					c = max(contours, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)
					if M["m00"] > 0:
						center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
						if radius < MIN_RADIUS:
							center = None
				
				#if the center is not equal to None
				if center != None:
					#if the verbose debug = true print the coordinates
					#and radius
					if VERBOSE:
						print str(center) + " " + str(radius)
					#the X coordinate is the first term in the array
					centerX = center[0]
					#the Y coordinate is the second term in the array
					centerY = center[1]
					#Find out if the X component of the circle is to the
					#right of the middle of the screen.
					if(centerX < (midScreenX - midScreenWindow)):
						#Update the pan position variable to move the 
						#servo to the right.
						servoPanPosition -= panStepSize
						#if Verbose debug is true print the directions
						if VERBOSE:
							print str(centerX) + " > " + str(midScreenX) + " : Pan Right : " + str(servoPanPosition)
					#Find out if the X component of the circle is to the
					#right of the middle of the screen.
					elif(centerX > (midScreenX + midScreenWindow)):
						#Update the pan position variable to move the 
						#servo to the left.
						servoPanPosition += panStepSize
						#print pan left if motors go left
						if VERBOSE:
							print str(centerX) + " < " + str(midScreenX) + " : Pan Left : " + str(servoPanPosition)
					else:
						if VERBOSE:
							print str(centerX) + " ~ " + str(midScreenX) + " : " + str(servoPanPosition)
					
					#assigns the angle to panposition if less than max,
					#but if it is larger just assign the max value. also
					#compares the pan position to the minimum and if its 
					#less than minimum, just assign it to be the minimum
					servoPanPosition = min(servoPanPosition, max_pwm_angle_x)
					servoPanPosition = max(servoPanPosition, min_pwm_angle_x)
					
					#if the pressurevalue is less than or equal to 1000
					#assign the angle to the function movebottom which
					#moves the bottom servo to that position
					if pressurevalue <= 1000:
						movebottom(servoPanPosition)

					#Find out if the Y component of the circle is below 
					#the middle of the screen.
					if(centerY < (midScreenY - midScreenWindow)):
						#Update the tilt position variable to lower the
						#tilt servo.
						servoTiltPosition -= tiltStepSize
						if VERBOSE:
							print str(centerY) + " > " + str(midScreenY) + " : Tilt Down : " + str(servoTiltPosition)
					#Find out if the Y component of the face is above 
					#the middle of the screen.
					elif(centerY > (midScreenY + midScreenWindow)):
						#Update the tilt position variable to raise the 
						#tilt servo.
						servoTiltPosition += tiltStepSize
						if VERBOSE:
							print str(centerY) + " < " + str(midScreenY) + " : Tilt Up : " + str(servoTiltPosition)
					else:
						if VERBOSE:
							print str(centerY) + " ~ " + str(midScreenY) + " : " + str(servoTiltPosition)
					
					#assigns the angle to panposition if less than max,
					#but if it is larger just assign the max value. also
					#compares the pan position to the minimum and if its 
					#less than minimum, just assign it to be the minimum
					servoTiltPosition = min(servoTiltPosition, max_pwm_angle_y)
					servoTiltPosition = max(servoTiltPosition, min_pwm_angle_y)
					
					#if the pressurevalue is less than or equal to 1000
					#assign the angle to the function movetop which
					#moves the top servo to that position
					if pressurevalue <= 1000:
						movetop(servoTiltPosition)
				
				#draws a circle on the screen around the center of the
				#object on the screen if there is a center	
				if center != None:
					cv2.circle(image, center, int(round(radius)), (0, 255, 0))
				#if the pressurevalue is less than 1000 and the center
				#is none incriment the iterator by 5, this is the scan
				#function of the servos if the color is not detected. 
				#which incriments the angle by 5 each time and assigns 
				#it to the bottom servo.
				if pressurevalue <= 1000:
					if center == None:
						i += 5
						if i == 120:
							i = 0
						for channel in range(14, 15):
							myservo[channel].write(i)
							time.sleep(0.1)
				#if the SHOW_IMAGE debug option is TRUE, create the
				#three windows showing the video feed with different
				#filters for testing.
				if SHOW_IMAGE:
					cv2.imshow('webcam', image)
					cv2.imshow('binary', img_binary)
					cv2.imshow('contours', img_contours)
				#assigns key to stop the code
				key = cv2.waitKey(1) & 0xFF
			 
				# clear the stream in preparation for the next frame
				rawCapture.truncate(0)
		 
				# if the `q` key was pressed, break from the loop
				if key == ord("q"):
					break
				#if the Stopper is pressed, set the stopper signal to
				#the Arduino high, and turn on the max lift led and 
				#print to the LCD screen.
				if (GPIO.input(STOPPER) == 0):
					GPIO.output(STOPPER_SIGNAL, 1)
					GPIO.output(MAX_LIFT_LED, 1)
					lcd.message('Max Lift Height!\n                ')
				
				#if the stopper is not pressed, set the arduino signal
				#low and the Max life LED off
				if (GPIO.input(STOPPER) == 1):
					GPIO.output(STOPPER_SIGNAL, 0)
					GPIO.output(MAX_LIFT_LED, 0)
				
				#if the turn left button is pressed, send a high signal
				#to the arduino	
				if (GPIO.input(TURN_LEFT) == 0):
					GPIO.output(TURN_LEFT_SIGNAL, 1)
				
				#if the turn left button is not pressed, send a low
				#signal to the arduino	
				if (GPIO.input(TURN_LEFT) == 1):
					GPIO.output(TURN_LEFT_SIGNAL, 0)
				
				#if the turn right button is pressed, send a high signal
				#to the arduino	
				if (GPIO.input(TURN_RIGHT) == 0):
					GPIO.output(TURN_RIGHT_SIGNAL, 1)
				
				#if the turn right button is not pressed, send a low
				#signal to the arduino	
				if (GPIO.input(TURN_RIGHT) == 1):
					GPIO.output(TURN_RIGHT_SIGNAL, 0)
				
				#if the backup mode switch is pressed, send a high
				#signal to the arduino and turn on the Backup LED.	
				if (GPIO.input(BACKUP_MODE_SWITCH) == 0):
					GPIO.output(BACKUP_MODE_SIGNAL, 1)
					GPIO.output(BACKUP_LED, 1)
				
				#if the backupmode switch is not pressed, send a low 
				#signal to the arduino and turn of the backup led
				if (GPIO.input(BACKUP_MODE_SWITCH) == 1):
					GPIO.output(BACKUP_MODE_SIGNAL, 0)
					GPIO.output(BACKUP_LED, 0)	
	#end of the try block which if detects a keyboard input, clean up
	#the gpio pins to default values.			
	except KeyboardInterrupt:
		GPIO.cleanup()
