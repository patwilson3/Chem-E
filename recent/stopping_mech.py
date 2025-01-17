import alg
import gpio
import threading
import time

chip = gpio.open_chip(0)
ps_motor = gpio.motor(12, chip)
stirrer = gpio.motor(16, chip)
button = gpio.button(25, True, chip)

def turn_on_stirrer():
	print("stirrer motor is on")
	stirrer.turn_on()
	while True:
		if not alg.operation_active.is_set():
			return
	
def turn_off_stirrer():
	print("stirrer motor is off")
	stirrer.turn_off()
	
def turn_on_ps():
	print("ps motor is on")
	ps_motor.turn_on()
	while True:
		if not alg.operation_active.is_set():
			return
	
def turn_off_ps():
	print("ps motor is off")
	ps_motor.turn_off()
	
def cleanup():
	print("cleaning up")
	ps_motor.cleanup()
	stirrer.cleanup()
	button.cleanup()
	gpio.close_chip(chip)
	
def algorithm():
	button.wait_for_press()
	print("button is pressed")
	alg_thread = threading.Thread(target=alg.running_alg)
	#record_cam = threading.Thread(target=capturevideo.record("./tests/test20241206_tbd.mp4", 100)
	ps_motor_thread = threading.Thread(target=turn_on_ps)
	stirrer_thread = threading.Thread(target=turn_on_stirrer)
	ps_motor_thread.start()
	stirrer_thread.start()
	alg_thread.start()
	#record_cam.start()
	#record_cam.join()
	alg.operation_active.set()
	alg_thread.join()
	alg.operation_active.clear()
	turn_off_ps()
	turn_off_stirrer()
	
	cleanup()
	exit(0)

def video(path, duration):
	button.wait_for_press()
	print("button is pressed")
	alg_thread = threading.Thread(target=alg.running_alg)
	record_cam = threading.Thread(target=capturevideo.record(f"./tests/{path}.mp4", duration))
	ps_motor_thread = threading.Thread(target=turn_on_ps)
	stirrer_thread = threading.Thread(target=turn_on_stirrer)
	ps_motor_thread.start()
	stirrer_thread.start()
	#alg_thread.start()
	record_cam.start()
	alg.operation_active.set()
	#alg_thread.join()
	record_cam.join()
	alg.operation_active.clear()
	turn_off_ps()
	turn_off_stirrer()
	
	cleanup()
	exit(0)

if __name__ == "__main__":
	#video("test20241206_tbd", 10)
	#algorithm()
	cleanup()
	
	
	
	
