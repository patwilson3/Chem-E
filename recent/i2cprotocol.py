#please check requirements.txt for the required libraries for this program
#ina226 library from https://github.com/e71828/pi_ina226/blob/main/ina226.py
#LCD library from https://github.com/sterlingbeason/LCD-1602-I2C/blob/master/LCD.py
from dependencies import ina226
from dependencies import LCD

lcd_addr = 0x27
ina226_add = 0x40
max_expected = None #value to be determined
lcd = LCD.LCD(lcd_addr=0x27)
ammeter = ina226.INA226(address=ina226_add, max_expected_amps=max_expected)


def get_voltage():
    '''Returns float in volts'''
    return ammeter.voltage()

def get_current():
    '''Returns float in milliamps'''
    return ammeter.current()

def send_readings_to_lcd():
    '''Send a message to the lcd'''
    volt_message = get_voltage()
    amp_message = get_current()
    #Sends message to the first line of lcd
    LCD.message(f"{volt_message} V", 1)
    #Sends message to the second line of lcd
    LCD.message(f"{amp_message} mA", 2)