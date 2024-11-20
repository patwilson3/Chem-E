import RPi.GPIO as GPIO
import alg
import time
import threading
import cv2
from picamera2 import Picamera2, Preview
import numpy as np
import sys
import sendMessage
#from gpiozero import Servo
#This is a test to see if everyone sees
#initializing constants
'''
TODOS:
Need a function for magnetic stirer:
specs: Needs a pin to output a HIGH signal 3 seconds After the motor turns (a new pin is needed)

Need a function for stepper motor:
Specs: Need a new motor function that works with a stepper motor. Research how to configure a stepper motor
This function will replace the old motor function, do not delete old motor function but update it (Can use current motor pins)

Need to call sendMessage somehow, but first need to verify is this function is working. *TESTS REQUIRED*

'''
LED_PIN = 6
STOP_SIGNAL_PIN = 16
BUTTON_PIN = 22
RESET_PIN = 26
forwardPin = 17
backwardPin = 27
delayTime = 2
motor_opened = False

#2,3
# Pin that connects the LED
LED_PIN2 = 10

#Pin that connects the stirrer
STIRRER_PIN = 24

#setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(forwardPin, GPIO.OUT)
GPIO.setup(backwardPin, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

#stops the car but setting stop_signal_pin to low
def setStopPinOn():
    GPIO.setmode(GPIO.BCM) #BCM so program can understand what pins on the Raspberry pi we are using (GPIO pins) and what that pin will be used for
    GPIO.setup(STOP_SIGNAL_PIN, GPIO.OUT) #Setup is used to tell the Raspberry pi which pin will be used
    GPIO.output(STOP_SIGNAL_PIN, GPIO.LOW) #Send a low signal to the specified pin
    GPIO.output(LED_PIN, GPIO.LOW)
    
def turnStirrerOn():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STIRRER_PIN, GPIO.OUT)
    GPIO.output(STIRRER_PIN, GPIO.HIGH)
    
    
    

def setStopPinOff():
    # Moves the card by adding a high signal to designated stop signal
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STOP_SIGNAL_PIN, GPIO.OUT) #GPIO.OUT meaning it will be used as an output pin 
    time.sleep(0.2)
    GPIO.output(STOP_SIGNAL_PIN, GPIO.HIGH) #set pin to a high, raspberry pi sends out a high signal from specified pin
    time.sleep(0.2) 
    GPIO.output(LED_PIN, GPIO.HIGH) 

def motor_open():
    GPIO.output(forwardPin, GPIO.HIGH) # motor turns a certain direction with one output pin high, and one low (motor will turn in direction of current flow)
    GPIO.output(backwardPin, GPIO.LOW) 
    time.sleep(delayTime)
    # stop
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.LOW)


def motor_close():
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.HIGH)
    time.sleep(delayTime)

    # stop
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.LOW)

def motor():
    # spinforward
    GPIO.output(forwardPin, GPIO.HIGH)
    GPIO.output(backwardPin, GPIO.LOW)
    time.sleep(delayTime)

    # stop
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.LOW)
    time.sleep(8)

    # spinbackwards
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.HIGH)
    time.sleep(delayTime)

    # stop
    GPIO.output(forwardPin, GPIO.LOW)
    GPIO.output(backwardPin, GPIO.LOW)


def startOperations():
    # if operationactive not on, start operations
    
    GPIO.output(LED_PIN2, GPIO.HIGH) # Turning on an LED that is connected to LED_PIN2

    if not alg.operation_active.is_set(): #checks to see if thread is already running
        threading.Thread(target=sequentialOperations).start() #starts thread if it is not already running after start buttton is pressed
    else:
        print("already running")


def sequentialOperations():
    #global motor_opened
    try:
        # set operation_active on, allowing window for reset button to be used
        alg.operation_active.set()
        # defining stop pin
        setStopPinOn()
        motor() #motor will run regardless of reset button
        #time.sleep(3)
        #call to stir function
        turnStirrerOn()
        
        
        print("motor done")
        
        if alg.operation_active.is_set(): #if reset button was pressd algorithm will not run (this is used to avoid connecting the rasberry pi to a monitor and physically stopping the algorithm)
            # begin moving the car
            setStopPinOff()
            # start alg
            alg.running_alg()
            
            motor_open()
            #motor_opened = True

    finally:
        # stop car
        setStopPinOn()
        # clear thread
        alg.operation_active.clear()
        # open motor to neutralize reaction
        




def buttonPressedCallback(channel):
    # if statements act as safety net to make sure no multiple threads can run
    if channel == BUTTON_PIN and not alg.operation_active.is_set():
        print("Im Starting")
        startOperations()


def resetButton(channel):
    #global motor_opened
    # if thread is active clear/reset it and make sure car is stopped
    if alg.operation_active.is_set() and channel == RESET_PIN:
        alg.operation_active.clear()
        print("Operations were reset")
    # not active so ignore reset press
    #if motor_opened:
        #motor_opened = False
        #motor_close()
    #setStopPinOn()
    


# awaits button press events
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=buttonPressedCallback, bouncetime=100)
GPIO.add_event_detect(RESET_PIN, GPIO.FALLING, callback=resetButton, bouncetime=100)

# enters infinite loop so the program does not stop running
try:
    while True:
        time.sleep(0.1)

#CTRL C to quit and cleanup GPIO
except KeyBoardInterrupt:
    print("finished")
    GPIO.cleanup()
