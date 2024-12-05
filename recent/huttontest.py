import lgpio
import time

MOS_PIN = 16
BUTTON_PIN = 25

chip = lgpio.gpiochip_open(0)

try:
	lgpio.gpio_claim_output(chip, MOS_PIN)
	lgpio.gpio_claim_input(chip, BUTTON_PIN)
	
	while (True):
		if (lgpio.gpio_read(chip, BUTTON_PIN) == 0):
			print(f"setting pin to high")
			lgpio.gpio_write(chip, MOS_PIN, 1)
			
			time.sleep(5)
	
			print(f"setting pin to low")
			lgpio.gpio_write(chip, MOS_PIN, 0)
		
finally:
	lgpio.gpio_write(chip, MOS_PIN, 0)
	lgpio.gpiochip_close(chip)

