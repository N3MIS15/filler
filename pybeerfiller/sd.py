import os, machine
from lib.sdcard import SDCard

class cardSD:
    def __init__(self, spi_channel, slave_select_pin, path):
        spi = machine.SPI(spi_channel)
        ss_pin = machine.Pin(slave_select_pin)
        self.sd = SDCard(spi, ss_pin)
        self.path = path

    def mount(self):
        os.mount(self.sd, self.path)

    def umount(self):
        print("Unmounting ", self.path)
        os.umount(self.path)

    def test(self):
        return os.listdir(self.path)[1]