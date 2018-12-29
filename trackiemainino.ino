/***********************************************************************
*
* {Trackiemain.ino}
* Created by: Ryan Howard
* PERFORMANCE:
* This code controls the Drive wheel motors, lift motor, sonic sensors,
* antenna control, and the lift and lower buttons as well as the turning
* left and right buttons. The arduino recieves signals from the
* Raspberry Pi through input GPIO pins to add logic to the wheels.
*
***********************************************************************/

//-Define-PWM-Pins------------------------------------------------------
#define LEFT_DIRECTION 4
#define LEFT_PWM 5
#define RIGHT_DIRECTION 7
#define RIGHT_PWM 6
#define LIFT_PWM 3
#define LIFT_DIRECTION 2

//-Define-Lift-Buttons--------------------------------------------------
#define LIFT_BUTTON 9
#define LOWER_BUTTON 10

//-Define-Sonic-Sensor-Pins---------------------------------------------
#define PING_BOT 11
#define PING_TOP 12

//-Signals-From-The-Pi--------------------------------------------------
#define STOPPER_SIGNAL 13
#define PUSH_LEFT_SIGNAL A1
#define PUSH_RIGHT_SIGNAL A2
#define BACKUP_MODE A3

//-Antenna-input-Pin-and-voltage-variables------------------------------
#define SPEAKER_FROM_WALKIETALKIE A0
uint16_t voltage = 0;

/***********************************************************************
*	{setup()}
*	Sets all the pins to the corresponding IN or out Functions as well
*	as the 2 buttons to be in Pullup resistor mode so they can be read.
*	It also begins the Serial program which recieves information that
*	was used for testing and debugging. 
***********************************************************************/
void setup(){
  Serial.begin(9600);
  pinMode(LEFT_PWM, OUTPUT);
  pinMode(LEFT_DIRECTION, OUTPUT);
  pinMode(RIGHT_PWM, OUTPUT);
  pinMode(RIGHT_DIRECTION, OUTPUT);
  pinMode(LIFT_PWM, OUTPUT);
  pinMode(LIFT_DIRECTION, OUTPUT);
  
  pinMode(LIFT_BUTTON, INPUT_PULLUP);
  pinMode(LOWER_BUTTON, INPUT_PULLUP);

  pinMode(BACKUP_MODE, INPUT);
  pinMode(PUSH_LEFT_SIGNAL, INPUT);
  pinMode(PUSH_RIGHT_SIGNAL, INPUT);
  pinMode(SPEAKER_FROM_WALKIETALKIE, INPUT);
  pinMode(STOPPER_SIGNAL, INPUT);
}
/***********************************************************************
*	loop()
*	Infinitely looping main code. Inside of this loop is all the main 
*	functions of the PWM and signals that control the motors.
***********************************************************************/
void loop() {
  //-declaring-variables-for-the-sonic-sensors--------------------------
  long top_duration, bot_duration, top_distance, bot_distance;
  
  //-variable-to-control-the-speed-of-the-motor-from-0-to-255-----------
  int pwm_value=255;
  
  //-assigns-the-values-outputted-from-the-sonic-sensor-functions-------
  //-to-variables-that-can-be-used-to-stop-the-motors-if-within-a-------
  //-certain-distance---------------------------------------------------
  top_duration = distance(PING_TOP);
  top_distance = microsecondsToCentimeters(top_duration);
  bot_duration = distance(PING_BOT);
  bot_distance = microsecondsToCentimeters(bot_duration);  
  
  //-When-the-Backup-switch-is-on,-rotate-both-motors backwards---------
  if (digitalRead(BACKUP_MODE) == HIGH)
  {
    digitalWrite(LEFT_DIRECTION, LOW);
    analogWrite(LEFT_PWM, pwm_value);
    digitalWrite(RIGHT_DIRECTION, LOW);
    analogWrite(RIGHT_PWM, pwm_value);
    delay(30);
  }
  
  //-assigns-the-reading-from-walkie-talkie-board-to-voltage------------
  voltage = analogRead(SPEAKER_FROM_WALKIETALKIE);
  
  //-if-the-radio-is-transmitting-and-both-turn-buttons-arnt-pressed----
  //-move-forward-------------------------------------------------------
  
  if ((voltage > 300) and (digitalRead(PUSH_LEFT_SIGNAL) == LOW) and (digitalRead(PUSH_RIGHT_SIGNAL) == LOW) ) 
  {
    digitalWrite(LEFT_DIRECTION, HIGH);                                 
    analogWrite(LEFT_PWM,pwm_value);                               
    digitalWrite(RIGHT_DIRECTION, HIGH);
    analogWrite(RIGHT_PWM,pwm_value);
  }
  
  //-if-the-radio-is-not-transmitting,-both-turn-buttons-are-not--------
  //-pressed-or-if-an-object-is-within-15cm-of-the-top-or-bottom--------
  //-sonic-sensor-turn-off-motors---------------------------------------
  if ((voltage < 300) and (digitalRead(PUSH_LEFT_SIGNAL) == LOW) and (digitalRead(PUSH_RIGHT_SIGNAL) == LOW) or (top_distance <= 15) or (bot_distance <= 15) ) 
  {
    digitalWrite(LEFT_DIRECTION, HIGH);                                 
    analogWrite(LEFT_PWM, 0);                              
    digitalWrite(RIGHT_DIRECTION, HIGH);
    analogWrite(RIGHT_PWM, 0);
  }
  
  //-if-the-left-button-is-pressed-and-right-is-not-turn-the-bot-left---
  if ((digitalRead(PUSH_LEFT_SIGNAL) == HIGH) and (digitalRead(PUSH_RIGHT_SIGNAL) == LOW)) 
  {
    digitalWrite(LEFT_DIRECTION, LOW);                                  
    analogWrite(LEFT_PWM,pwm_value);                               
    digitalWrite(RIGHT_DIRECTION, HIGH);
    analogWrite(RIGHT_PWM,pwm_value);
  }
  
  //-if-the-right-button-is-pressed-and-left-is-not,-turn-the-bot-right-
  if ((digitalRead(PUSH_LEFT_SIGNAL) == LOW) and (digitalRead(PUSH_RIGHT_SIGNAL) == HIGH)) 
  {
    digitalWrite(LEFT_DIRECTION, HIGH);                                          
    analogWrite(LEFT_PWM,pwm_value);                  
    digitalWrite(RIGHT_DIRECTION, LOW);
    analogWrite(RIGHT_PWM,pwm_value);
  }
  
  
  //-if-the-lift-button-is-pressed-and-lower-button-is-not-pressed-and--
  //-stopper-button-is-not-pressed-raise-with-the-lift------------------
  if ((digitalRead(LIFT_BUTTON) == LOW) and (digitalRead(LOWER_BUTTON) == HIGH) and (digitalRead(STOPPER_SIGNAL) == LOW))
  {
    digitalWrite(LIFT_DIRECTION, LOW);
    analogWrite(LIFT_PWM,pwm_value);
  }
  //-if-the-lift-button-is-not-pressed-and-lower-button-is-not-pressed--
  //-and-stopper-button-is-not-pressed-turn-off-motor-------------------
  if ((digitalRead(LIFT_BUTTON) == LOW) and (digitalRead(LOWER_BUTTON) == LOW) and (digitalRead(STOPPER_SIGNAL) == LOW))
  {
    digitalWrite(LIFT_DIRECTION, LOW);
    analogWrite(LIFT_PWM, 0);
  }
  
  //-if-the-lift-button-is-pressed-and-lower-button-is-pressed----------
  //-and-stopper-button-is-not-pressed-turn-off-motor-------------------
  if ((digitalRead(LIFT_BUTTON) == HIGH) and (digitalRead(LOWER_BUTTON) == HIGH) and (digitalRead(STOPPER_SIGNAL) == LOW))
  {
    digitalWrite(LIFT_DIRECTION, LOW);
    analogWrite(LIFT_PWM, 0);
  }
  
  //-if-the-lift-button-is-not-pressed-and-lower-button-is-pressed------
  //-lower-the-top------------------------------------------------------
  if ((digitalRead(LIFT_BUTTON) == HIGH) and (digitalRead(LOWER_BUTTON) == LOW))
  {
    digitalWrite(LIFT_DIRECTION, HIGH);
    analogWrite(LIFT_PWM,pwm_value);
  }
  
  //-if-lift-button-is-pressed-and-lower-button-is-not-pressed-but-the--
  //-stopper-button-is,-emergency-stop-the-motor-because-of-max-height--
  if ((digitalRead(LIFT_BUTTON) == LOW) and (digitalRead(LOWER_BUTTON) == HIGH) and (digitalRead(STOPPER_SIGNAL) == HIGH))
  {
    digitalWrite(LIFT_DIRECTION, HIGH);
    analogWrite(LIFT_PWM, 0);
  }
  
}
/***********************************************************************
*	distance(Sensor)
*	Returns the distance an object is from the sonic sensor in micro-
*	seconds. Takes in an argument named sensor, which is the pin of the
*	signal on the sensor so it can be used for multiple sensors.
***********************************************************************/
long distance(long Sensor) 
{
  //-declares-the-variable-which-is-assigned-the-distance-in-ms---------
  long sensorduration;
  
  //assigns-the-sensor-as-an-output-pin-and-rapidly-turns-on-and-off----
  //the-pin.------------------------------------------------------------
  pinMode(Sensor, OUTPUT);
  digitalWrite(Sensor, LOW);
  delayMicroseconds(2);
  digitalWrite(Sensor, HIGH);
  delayMicroseconds(5);
  digitalWrite(Sensor, LOW);

  //-The-same-pin-is-used-to-read-the-signal-from-the-sensor:-a-HIGH-pulse
  //-whose-duration-is-the-time-(in-microseconds)-from-the-sending-of---
  //-the-ping-to-the-reception-of-its-echo-off-of-an-object.------------
  pinMode(Sensor, INPUT);
  sensorduration = pulseIn(Sensor, HIGH);
  return sensorduration;
}
/***********************************************************************
*	microsecondsToCentimeters(microseconds)
*	This function converts the distance reading from microseconds into
*	centemeters by dividing by the speed of sound which is 340 m/s or
*	29 microseconds per centimeter. Then, it is divided again by 2
*	because half the distance would be where the object is since it is
*	initially returning the time to and from the object.
***********************************************************************/
long microsecondsToCentimeters(long microseconds) 
{
  return microseconds / 29 / 2;
}
