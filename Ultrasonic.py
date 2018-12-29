#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
#GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
#GPIO_TRIGGER = 5
#GPIO_ECHO = 6
#SIG = 18
 
#set GPIO direction (IN / OUT)
#GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
#GPIO.setup(GPIO_ECHO, GPIO.IN)
#GPIO.setup(SIG, GPIO.OUT)
 
def distance(SIG):
    GPIO.setup(SIG, GPIO.OUT)
    # set Trigger to HIGH
    GPIO.output(SIG, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(SIG, False)
    GPIO.setup(SIG, GPIO.IN)
    
    StartTime = time.time()
    StopTime = time.time()
    
 
    # save StartTime
    while GPIO.input(SIG) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(SIG) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
#if __name__ == '__main__':
 #   try:
 #       while True:
#            dist = distance()
 #           if dist < 30:
  #              print ("Object detected %.1fcm away" % dist)
 #           else:
  #              print ("No objects detected")
 #           time.sleep(1)
 
        # Reset by pressing CTRL + C
 #   except KeyboardInterrupt:
  #      print("Measurement stopped by User")
  #     GPIO.cleanup()
