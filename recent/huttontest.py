import lgpio
import time
from dependencies import ina226
from dependencies import LCD
import time

MOS_PIN = 16
BUTTON_PIN = 25

chip = lgpio.gpiochip_open(0)

lcd_addr = 0x27
ina226_add = 0x40
max_expected = 4 #value to be determined


def send_message():
    msg = ammeter.current()
    msg1 = ammeter.voltage()
    time.sleep(0.05)
    lcd.message(f"{msg:.4f} mA", 1)
    lcd.message(f"{msg1:.4f} V", 2)

try:
	lgpio.gpio_claim_output(chip, MOS_PIN)
	lgpio.gpio_claim_input(chip, BUTTON_PIN)
	
	lcd = LCD.LCD(i2c_addr=0x27)
	lcd.clear()
	ammeter = ina226.INA226(address=ina226_add, max_expected_amps=max_expected, shunt_ohms=0.115)
	ammeter._calibrate(20, 5, 4)
	
	while (True):
		if (lgpio.gpio_read(chip, BUTTON_PIN) == 0):
			print(f"setting pin to high")
			lgpio.gpio_write(chip, MOS_PIN, 1)
			
			for i in range(1, 101):
				send_message()
	
			print(f"setting pin to low")
			lgpio.gpio_write(chip, MOS_PIN, 0)
			time.sleep(1)
			send_message()
		
finally:
	lgpio.gpio_write(chip, MOS_PIN, 0)
	lgpio.gpiochip_close(chip)

