import machine, sys, time, pyb, array
from lib.st7920 import Screen
from pybeerfiller.actuator import Actuator
from pybeerfiller.config import *
from pybeerfiller.sd import cardSD

can_x_pos = 110
can_y_pos = 0
can_x_pix = 17
can_y_pix = 28


class pyBeerFiller:
    def __init__(self):
        print("Initializing")

        self.lcd            = Screen(lcd_spi_channel, lcd_slave_select_pin)

        #self.sd             = cardSD(sdcard_spi_channel, sdcard_slave_select_pin, sdcard_path)
        #self.sd.mount()
        
        #self.lcd.put_string(self.sd.test(), 1, 50)

        self.feeder             = Actuator(actuators['feed_actuator'])
        self.pre_purge          = Actuator(actuators['pre_purge_actuator'])
        self.post_purge         = Actuator(actuators['post_purge_actuator'])
        self.gantry             = Actuator(actuators['gantry_actuator'])
        self.fillers            = [Actuator(x) for x in actuators['fill_actuators']]

        self.reset_flag         = False
        self.cans_filled        = 0

        start_switch            = machine.Pin(start_button_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        start_switch.irq(         trigger=machine.Pin.IRQ_FALLING, handler=self.readButton)

        self.deactiveAll()
        self.current_state      = "Idle"
        self.filling            = False
        self.triggered_fillers  = []
        self.can_anim_pos       = can_y_pos + can_y_pix + 2
        self.can_anim_list      = []

        """lcd_timer = machine.Timer(
            -1, 
            freq=2, 
            mode=machine.Timer.PERIODIC, 
            callback=lambda t:self.drawLCD()
        )"""

        #self.lcd.put_string("Test", 0, 0)
        #self.lcd.redraw()


    def getState(self):
        return self.current_state


    def setState(self, state):
        print(state)
        self.current_state = state


    def reset(self, do_reset=False):
        if do_reset:
            print("Resetting")
            self.reset_flag = True
        return self.reset_flag


    def shutdown(self, text):
        print(text)
        try:
            self.deactiveAll()
            #self.sd.umount()

        except Exception as e:
            sys.print_exception(e)


    def deactiveAll(self):
        for x in self.fillers: x.deactivate()
        self.pre_purge.deactivate()
        self.post_purge.deactivate()
        self.feeder.deactivate()
        self.gantry.deactivate()


    def putCan(self):
        self.lcd.line(can_x_pos, can_y_pos+3, can_x_pos, can_y_pos+can_y_pix)
        self.lcd.line(can_x_pos+can_x_pix, can_y_pos+3, can_x_pos+can_x_pix, can_y_pos+can_y_pix)
        self.lcd.line(can_x_pos+2, can_y_pos, (can_x_pos+can_x_pix)-2, can_y_pos)
        self.lcd.line(can_x_pos+2, can_y_pos+3+can_y_pix, (can_x_pos+can_x_pix)-2, can_y_pos+3+can_y_pix)
        self.lcd.line(can_x_pos, can_y_pos+3, can_x_pos+3, can_y_pos)
        self.lcd.line(can_x_pos+can_x_pix, can_y_pos+3, (can_x_pos+can_x_pix)-3, can_y_pos)
        self.lcd.line(can_x_pos+3, can_y_pos+3+can_y_pix, can_x_pos, can_y_pos+can_y_pix)
        self.lcd.line((can_x_pos+can_x_pix)-3, can_y_pos+3+can_y_pix, can_x_pos+can_x_pix, can_y_pos+can_y_pix)

        if self.filling:
            if self.can_anim_pos in [can_y_pos+1, (can_y_pos+can_y_pix+3)-1]:
                x = [can_x_pos+3, (can_x_pos+can_x_pix)-3]
            elif self.can_anim_pos in [can_y_pos+1, (can_y_pos+can_y_pix+3)-1]:
                x = [can_x_pos+3, (can_x_pos+can_x_pix)-3]
            elif self.can_anim_pos in [can_y_pos+2, (can_y_pos+can_y_pix+3)-2]:
                x = [can_x_pos+2, (can_x_pos+can_x_pix)-2]
            else:
                x = [can_x_pos+1, (can_x_pos+can_x_pix)-1]

            self.can_anim_list.append([x[0], self.can_anim_pos, x[1], self.can_anim_pos])
            self.can_anim_pos -= 1

            for x in self.can_anim_list: self.lcd.line(x[0], x[1], x[2], x[3])

            if self.can_anim_pos < can_y_pos:
                self.can_anim_pos   = can_y_pos + can_y_pix + 2
                self.can_anim_list  = []

        else:
            self.can_anim_pos   = can_y_pos + can_y_pix + 2
            self.can_anim_list  = []


    def getReadings(self):
        [x.readSensor() for x in self.fillers if x.pin not in self.triggered_fillers]
        for x in self.fillers:
            if x.triggered and x.pin not in self.triggered_fillers:
                x.deactivate()
                self.triggered_fillers.append(x.pin)


    def startFillTimer(self): 
        self.timer = machine.Timer(
            -1, 
            freq=sensor_frequency_hz, 
            mode=machine.Timer.PERIODIC, 
            callback=lambda t:self.getReadings()
        )


    def stopFillTimer(self):
        self.timer.deinit()
        del self.timer
        self.timer = None


    def drawLCD(self):
        self.lcd.clear()
        self.lcd.put_string_old("Status:%s" % self.current_state, 1, 0)
        self.lcd.put_string_old("Cans Filled:%i" % self.cans_filled, 1, 20)
        self.putCan()
        self.lcd.redraw()


    def readState(self):
        self.drawLCD()

        try:
            if self.current_state == "Idle":
                pass

            elif self.current_state == "Feeding":
                self.feeder.activate()
                self.setState("Pre Purge")

            elif self.current_state == "Pre Purge":
                self.pre_purge.activate()
                self.setState("Filling")


            elif self.current_state == "Filling":
                if not self.filling:
                    self.startFillTimer()

                    for x in self.fillers: 
                        x.activate()

                    self.filling = True

                if len(self.triggered_fillers) == len(self.fillers):
                    self.stopFillTimer()
                    self.cans_filled += (len(self.fillers))

                    # Clean up
                    self.triggered_fillers = []
                    self.filling = False
                    for x in self.fillers: x.triggered = False
                    print("all closed")
                    
                    # Change State
                    self.setState("Post Purge")
                        

            elif self.current_state == "Post Purge":

                self.setState("Idle")

        except Exception as e:
            self.shutdown(e)
            self.reset(True)


    def readButton(self, pin):
        print("Start Button Pressed")
        if self.current_state == "Idle":
            self.setState("Feeding")
            
        else:
            self.shutdown("Emergency Stop Pressed")
            self.reset(True)