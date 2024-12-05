#please check requirements.txt for the required libraries for this program
#ina226 library from https://github.com/e71828/pi_ina226/blob/main/ina226.py
#LCD library from https://github.com/sterlingbeason/LCD-1602-I2C/blob/master/LCD.py
from dependencies import ina226
from dependencies import LCD
import time

lcd_addr = 0x27
ina226_add = 0x40
max_expected = 4 #value to be determined
lcd = LCD.LCD(i2c_addr=0x27)
lcd.clear()
ammeter = ina226.INA226(address=ina226_add, max_expected_amps=max_expected, shunt_ohms=0.115)
ammeter._calibrate(20, 5, 4)

def send_message():
    msg = ammeter.current()
    msg1 = ammeter.voltage()
    time.sleep(0.5)
    lcd.message(f"{msg:.4f} mA", 1)
    lcd.message(f"{msg1:.4f} V", 2)
    
