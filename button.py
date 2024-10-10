import RPi.GPIO as GPIO
import algremastered_new as alg
import time
import threading
import cv2
from picamera2 import Picamera2, Preview
import numpy as np
import sys

LED_PIN = 6
STOP_SIGNAL_PIN = 16
BUTTON_PIN = 22
RESET_PIN = 26
forwardPin = 17
backwardPin = 27
delayTime = 2
motor_opened = False

#setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(forwardPin, GPIO.OUT)
GPIO.setup(backwardPin, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

#stops the car but setting stop_signal_pin to low
def setStopPinOn():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STOP_SIGNAL_PIN, GPIO.OUT)
    GPIO.output(STOP_SIGNAL_PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)

def setStopPinOff():
    # Moves the card by adding a high signal to designated stop signal
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STOP_SIGNAL_PIN, GPIO.OUT)
    time.sleep(0.2)
    GPIO.output(STOP_SIGNAL_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(LED_PIN, GPIO.HIGH)

def motor_open():
    GPIO.output(forwardPin, GPIO.HIGH)
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
    if not alg.operation_active.is_set():
        threading.Thread(target=sequentialOperations).start()
    else:
        print("already running")


def sequentialOperations():
    #global motor_opened
    try:
        # set operation_active on, allowing window for reset button to be used
        alg.operation_active.set()
        # defining stop pin
        setStopPinOn()
        # motor will run regardless of thread but algorithm will not run if reset while motor is running
        motor()
        print("motor done")
        # if reset button was pressd algorithm will not run
        if alg.operation_active.is_set():
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
