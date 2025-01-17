from gpiozero import*
from signal import pause
import atexit
import time
import i2cprotocol
import lgpio


#POWER_BUTTON = Button(6, pull_up=True)
#OWER_BUTTON = DigitalInputDevice(6)

#RESET_BUTTON = Button("GPIO19")
MAINMOTOR_PIN = DigitalOutputDevice(5)

BUTTON_PIN = 6 

#intialize chip

chip = lgpio.gpiochip_open(0)

#Set gpio pin as an input

lgpio.gpio_claim_input(chip, BUTTON_PIN)



def button_pressed():
	time.sleep(0.1)
	print("button pressed")
	MAINMOTOR_PIN.on()
	count = 0
	while count < 4:
		i2cprotocol.send_message()
		MAINMOTOR_PIN.on()
		time.sleep(2)
		MAINMOTOR_PIN.off()
		count += 1
		
	MAINMOTOR_PIN.off()
	cleanup()
	print("Cleaned up and now terminating")
	i2cprotocol.send_message()
		

def cleanup():
	lgpio.gpiochip_close(chip)
	MAINMOTOR_PIN.off()
	MAINMOTOR_PIN.close()
	

	
try:
	print(f"Monitoring GPIO pin {BUTTON_PIN} for a rising edge...")
	
	#variable to store the previous state of the pin
	prev_state = lgpio.gpio_read(chip, BUTTON_PIN)
	
	while True: 
		#Read the current state of the pin
		current_state = lgpio.gpio_read(chip, BUTTON_PIN)
		
		#Detect a rising edge
		if current_state == 0:
			print("Rising edge detected !")
			button_pressed()
			exit(0)
			
		prev_state = current_state
		
		time.sleep(0.5)
		
except KeyboardInterrupt:
	print("\nExiting program.")

finally:
	#clean up
	lgpio.gpiochip_close(chip)
	print("GPIO chip closed.")
#atexit.register(cleanup)

'''
LCD AND AMMETER: WORKS
MOTOR MOSFET: WORKS
BUTTON PRESS: DOES NOT WORK, DOES WORK WHEN CONNECTED TO GND AND GPIO 16
SERVOS: IDK

'''

