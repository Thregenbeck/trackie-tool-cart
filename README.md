# Trackie Tool Cart
Autonomous tracking tool cart using python and OpenCV.
  ## trackiemain.py
  trackiemainpy holds the Python code for the Trackie Tool Cart which controls the user interface, including the lcd screen,
switches, buttons, and leds. This program also controls the camera and servo board used for the camera tracking light system.
Lastly, it controls signals that are sent to the Arduino via simple input pins to control the code on the arduino board as well.
  ## trackiemain.ino
  trackiemainino holds the code that controls the drive wheel motors, lift motor, sonic sensors, antenna control, and the lift and
lower buttons as well as the turning left and right buttons. The arduino recieves signals from the Raspberry Pi through input 
GPIO pins to add logic to the wheels.
# Test Files
The test branch are certian test code I created to test the certain components functionality as well as other uses after the project
was completed
  ## send_a_picture_to_email.py 
  Testing the functionality of the camera module as well as internet capablities, this program will take a picture of the current
  view of the camera and sends the picture as a .jpg to an email account instantaniously with a push of a wired button.
  ## ultrasonic.py
  Testing the ultrasonic sensors on the cart by printing to console the detecting distance an object was away from the sensors by
  calculating how long the wave takes to be sent and return 
  ## char_lcd_plate.py
  Tested the full functionality of the lcd plate including different backlight colors, custom pixel characters, message display and
  clearing, and directional buttons