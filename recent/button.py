from gpiozero import LED, Button, DigitalOutputDevice, Servo
import alg
import time
import threading
import cv2
from picamera2 import Picamera2, Preview
import numpy as np
import sys
import i2cprotocol
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
stop_signal = DigitalOutputDevice(STOP_SIGNAL_PIN)
stirrer = DigitalOutputDevice(STIRRER_PIN)
button = Button(BUTTON_PIN, pull_up=True)
reset_button = Button(RESET_PIN, pull_up=True)
forward_motor = DigitalOutputDevice(forwardPin)
backward_motor = DigitalOutputDevice(backwardPin)
led = LED(LED_PIN)
led2 = LED(LED_PIN2)

#stops the car but setting stop_signal_pin to low
def setStopPinOn():
    stop_signal.off()  # Sets pin to LOW
    led.off() 
    
def turnStirrerOn():
    stirrer.on()    

def setStopPinOff():
    # Moves the card by adding a high signal to designated stop signal
    time.sleep(0.2)
    stop_signal.on()  #set pin to a high, raspberry pi sends out a high signal from specified pin
    time.sleep(0.2) 
    led.on() 

def motor_open():
    forward_motor.on()  # Sets forward pin to HIGH
    backward_motor.off()  # Sets backward pin to LOW
    time.sleep(delayTime)
    # stop
    forward_motor.off()
    backward_motor.off() 

def motor_close():
    forward_motor.off()
    backward_motor.on()
    time.sleep(delayTime) # i added this no sure if this is right
    # stop
    forward_motor.off()
    backward_motor.off()

def motor():
    # spinforward
    forward_motor.on()
    backward_motor.off() 
    time.sleep(delayTime)

    # stop
    forward_motor.off()
    backward_motor.off() 
    time.sleep(8)

    # spinbackwards
    forward_motor.off()
    backward_motor.on()
    time.sleep(delayTime)

    # stop
    forward_motor.off() 
    backward_motor.off()


def startOperations():
    # if operationactive not on, start operations
     
    led2.on() # Turning on an LED that is connected to LED_PIN2

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
        

def buttonPressedCallback():
    # if statements act as safety net to make sure no multiple threads can run
    if not alg.operation_active.is_set():
         print("Im Starting")
         startOperations()
       

def resetButtonCallback():
    #global motor_opened
    # if thread is active clear/reset it and make sure car is stopped
    if alg.operation_active.is_set():
        alg.operation_active.clear()
        print("Operations were reset")
    # not active so ignore reset press
    #if motor_opened:
        #motor_opened = False
        #motor_close()
    #setStopPinOn()
    
# awaits button press events
button.when_pressed = buttonPressedCallback()
reset_button.when_pressed = resetButtonCallback()


# enters infinite loop so the program does not stop running
try:
    while True:
        time.sleep(0.1)
        i2cprotocol.send_message()

#CTRL C to quit and cleanup GPIO
except KeyboardInterrupt:
    print("finished")
