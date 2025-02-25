import lgpio
import time

class button:
    def __init__(self, gpio_pin, pullup, chip, debounce=0.100):
        self.gpio_pin = gpio_pin
        self.pullup = pullup
        self.debounce = debounce
        self.chip = chip
        #chip will be negative if opening devce failed
        if self.chip < 0:
            raise RuntimeError(f"Failed to open gpiochip {self.chip}")
        #if it is a pull up then falling edge, and set line flags for status
        if self.pullup:
            self.line_flags = lgpio.SET_PULL_UP
            self.edge = lgpio.FALLING_EDGE
        #opposite for pull down
        else:
            self.line_flags = lgpio.SET_PULL_DOWN
            self.edge = lgpio.RISING_EDGE 


        #intialiaze gpio pin as an input, and declare whether it is a pull up or pull down
        status = lgpio.gpio_claim_input(self.chip, self.gpio_pin, self.line_flags)
        if status != 0:
            lgpio.gpiochip_close(self.chip)
            raise RuntimeError(f"Failed to claim GPIO {self.gpio_pin} as input")

        #debounce time for safety net
        self.set_debounce(self.debounce)

        self.callback = None

    def set_debounce(self, debounce_time):
        """#set debounce of the button"""
        self.debounce = debounce_time
        status = lgpio.gpio_set_debounce_micros(self.chip, self.gpio_pin, int(self.debounce * 1e6))
        if status != 0:
            raise RuntimeError(f"Failed to set debounce time on GPIO {self.gpio_pin}")

    def get_state(self):
        """Returns current state of gpio pin"""
        state = lgpio.gpio_read(self.chip, self.gpio_pin)
        if state < 0:
            raise RuntimeError(f"Failed to read GPIO {self.gpio_pin}")
        return state

    def wait_for_press(self):
        """
        Blocks until the button is pressed.
        Returns when a button press is detected
        """
        while True:
            state = self.get_state()
            if self.pullup:
                pressed = state == 0 
            else:
                pressed = state == 1 

            if pressed:
                time.sleep(self.debounce)
                if self.get_state() == state:
                    return
            time.sleep(0.01) 


    def button_pressed(self, callback_function):
        """
        Registers a callback function to be called when the button is pressed.
        """

        def _internal_callback(chip, gpio, level, timestamp):
            if self.pullup and level == 0:
                callback_function()
            elif not self.pullup and level == 1:
                callback_function()

        self.set_debounce(self.debounce)

        self.callback = lgpio.callback(self.chip, self.gpio_pin, self.edge, _internal_callback)

    def cleanup(self):
        """Cleans up resources by unregistering callbacks and closing the chip."""
        if self.callback:
            self.callback.cancel()
            self.callback = None

        lgpio.gpio_free(self.chip, self.gpio_pin)


class motor:
    def __init__(self, gpio_pin, chip):
        self.pin = gpio_pin
        self.chip = chip
        #intialize gpio pin as an output
        status = lgpio.gpio_claim_output(self.chip, self.pin)
        if status != 0:
            raise RuntimeError(f"Failed to claim GPIO {self.pin} as an output")
        
    def turn_on(self, seconds = 0):
        '''Turns on motor'''
        #set to 1 to send a high signal
        status = lgpio.gpio_write(self.chip, self.pin, level = 1)
        if(status != 0):
            raise RuntimeError(f"Something went wrong when trying to turn motor ON, GPIO pin {self.pin}")
        if seconds != 0:
            time.sleep(seconds)
            self.turn_off()

    def turn_off(self):
        '''Turns the motor off'''
        status = lgpio.gpio_write(self.chip, self.pin, level = 0)
        if(status != 0):
            raise RuntimeError(f"Something went wrong when trying to turn motor OFF, GPIO pin {self.pin}")
        

    def cleanup(self):
        if(lgpio.gpio_read(self.chip, self.pin) == 1):
            self.turn_off()

        lgpio.gpio_free(self.chip, self.pin)


class servo:
    '''TODO''' 

    MIN_PULSE_WIDTH = 500 / 1_000_000
    MAX_PULSE_WIDTH = 2500 / 1_000_000
    def __init__(self, gpio_pin, chip):
        self.pin = gpio_pin
        self.chip = chip
        self.max_angle = 180
        self.current_pulse = self.angle_to_pulse_width(90)
        
        self.set_angle(90)
    def pulse_width_to_dutycycle(self, pulse_width_us, period_us=20000):
        duty_cycle = (pulse_width_us / period_us) * 100
        return duty_cycle
        
        
    def angle_to_pulse_width(self, angle):
        if(0<= angle <=180):
            return int(500 + (angle/180.0) * (2500 - 500))
        raise ValueError("Angle must be between 0 and 180")
    
    def turn_on(self):
        time.sleep(0.1)
        status = lgpio.tx_pwm(self.chip, self.pin, 500, 50)
        time.sleep(0.1)
    
    def set_angle(self, angle):
        '''
        sets servo to specified angle
        '''
        pulse_width = self.angle_to_pulse_width(angle)
        if abs(pulse_width - self.current_pulse) < 5:
            return
        #send signal
        duty_cycle = self.pulse_width_to_dutycycle(pulse_width)
        
        
        self.send_pwm(50, duty_cycle)
        
        self.current_pulse = pulse_width
    def send_pwm(self, frequency, duty_cycle, pulse_offset = 0, pulse_cycles = 0):
        status = lgpio.tx_pwm(self.chip, self.pin, frequency, duty_cycle, pulse_offset=pulse_offset, pulse_cycles=pulse_cycles)
    def cleanup(self):
        status = lgpio.tx_pwm(self.chip, self.pin, 0, 0)
        lgpio.gpio_free(self.chip, self.pin)




'''GLOBAL FUNCTIONS FOR INITALIZING CHIPS'''
def open_chip(chip_number):
    '''
    function opens chip number, is then passed on to other objects as an argument during their initialization
    '''
    chip = lgpio.gpiochip_open(chip_number)
    if(chip < 0):
        raise RuntimeError(f"Error, something went wrong when trying to open chip number: {chip_number}")
    
    return chip

def close_chip(chip):
    '''
    function will clean GPIO chip
    '''
    if chip < 0:
        raise RuntimeError(f"Error, something went wrong when trying to clean chip, chip was not cleaned")
    
    else:
        lgpio.gpiochip_close(chip)

    return 0
