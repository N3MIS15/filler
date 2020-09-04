from time import sleep_us
from machine import Pin

class Stepper:
    def __init__(self, step_pin, dir_pin, delay):
        self.step_pin   = pin(step_pin, Pin.OUT)
        self.dir_pin    = pin(dir_pin, Pin.OUT)
        self.delay      = delay
        
