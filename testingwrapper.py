import gpio
import lgpio
import i2cprotocol
from threading import Thread
import time
import gpiozero



chip = gpio.open_chip(0)

button = gpio.button(6, True, chip)
motor = gpio.motor(5, chip)
#servo = gpiozero.AngularServo(16, min_pulse_width = 0.0006, max_pulse_width = 0.0023)


def mainprog():
	print("Waiting for button press")

	# Non-blocking check for button press
	button.wait_for_press()
	print("Button pressed")
	#spin_servo()
	turn_on_mosfet(5)
	button.cleanup()
	motor.cleanup()
	gpio.close_chip(chip)

	print("quitting main prog")

def turn_on_mosfet(n):
	print("MOSFET turned on")
	motor.turn_on(5)  # Assuming you want to turn on the motor (MOSFET)
	
def spin_servo():
	for i in range(2): 
		servo.angle = 90
		time.sleep(2)
		servo.angle = -90
		time.sleep(2)

def send_message():
    while True:
        i2cprotocol.send_message()
        time.sleep(0.1)  # Small delay to avoid busy-waiting

if __name__ == '__main__':
	thread = Thread(target=send_message)
	thread2 = Thread(target=mainprog)
	thread.start()
	thread2.start()
	thread2.join()  # Ensure mainprog finishes before exiting
	time.sleep(5)
	print("quitting prog")
	exit(0)
