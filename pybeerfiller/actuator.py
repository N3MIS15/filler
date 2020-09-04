import machine
from pyb import Servo
import sys, time

class Actuator:
    def __init__(self, actuator):
        self.servo      = None
        self.stepper    = None
        self.pin        = actuator['pin']
        self.idle       = 0
        self.active     = 1
        self.speed      = 0
        self.time       = 0
        self.delay      = 0
        self.actuator   = None
        self.sensor     = None
        self.trigger    = 40000
        self.triggered  = False

        if "idle_state" in actuator:    self.idle = actuator['idle_state']
        if "active_state" in actuator:  self.active = actuator['active_state']
        if "speed" in actuator:         self.speed = actuator['speed']
        if "time" in actuator:          self.time = actuator['time']
        if "delay" in actuator:         self.delay = actuator['delay']
        if 'trigger' in actuator:       self.trigger = actuator['trigger']
        if "sensor" in actuator:        self.sensor = machine.ADC(actuator['sensor'])

        if not isinstance(self.pin, dict):
            if self.speed: # Assume servo
                x = int(self.pin[1:])+1
                self.servo = Servo(x)

            else:
                self.actuator = machine.Pin(self.pin, machine.Pin.OUT)

        else:
            #TODO Handle Stepper motor
            pass

        self.current_state = self.idle


    def isActivated(self): return self.current_state == self.active


    def triggerActuator(self, value):
        try:
            if isinstance(self.pin, dict):
                print("TODO: triggerActuator handle stepper motors")
                pass

            else:
                if self.servo:
                    self.servo.angle(value, self.speed)

                else:
                    self.actuator.value(value)

        except Exception as e:
            sys.print_exception(e)


    def activate(self):
        print("Activating %s: %s" % (self.pin, self.active))
        self.triggerActuator(self.active)
        self.current_state = self.active

        if not isinstance(self.pin, dict) and not self.sensor:
            print("time: %i" % self.time)
            time.sleep_ms(self.time)

        if not self.sensor:
            self.deactivate()
            print("delay: %i" % self.delay)
            time.sleep_ms(self.delay)
        else:
            pass

    def deactivate(self):
        print("Deativating %s: %s" % (self.pin, self.idle))
        self.triggerActuator(self.idle)
        self.current_state  = self.idle


    def readSensor(self):
        if self.isActivated():
            sensor_value = self.sensor.read_u16()
            self.triggered = sensor_value >= self.trigger
            print(self.sensor, self.triggered, sensor_value)

        return self.triggered

