import machine
from time import sleep_ms, sleep_us
from pybeerfiller.font import font
import ubinascii

Y_BOUNDRY           = 64
X_BOUNDRY           = 128//8

LCD_CLS             = 0x01
LCD_DISPLAYON       = 0x0C
LCD_DISPLAYCTRL     = 0x12
LCD_BASIC           = 0x30
LCD_EXTEND          = 0x34
LCD_GRAPHIC         = 0x36

class Screen:
    def __init__(self, spi_channel, slave_select_pin):
        self.cmdbuf = bytearray(33)
        self.cmdmv = memoryview(self.cmdbuf)
        self.fbuff = [memoryview(bytearray(X_BOUNDRY)) for x in range(Y_BOUNDRY)]

        self.spi = machine.SPI(spi_channel)
        self.slaveSelectPin = machine.Pin(slave_select_pin, machine.Pin.OUT)
        self.slaveSelectPin.value(1)

        self.send_flag(LCD_BASIC)
        sleep_ms(1)
        self.send_flag(LCD_DISPLAYON)
        sleep_ms(1)
        self.send_flag(LCD_CLS)
        sleep_ms(20)
        self.send_flag(LCD_EXTEND)
        sleep_us(100)
        self.send_flag(LCD_GRAPHIC)
        sleep_us(100)
        self.send_flag(LCD_DISPLAYCTRL)
        sleep_us(100)
        self.send_flag(LCD_CLS)
        sleep_ms(20)

        self.slaveSelectPin.value(0)


    def send_flag(self, b):
        self.cmdbuf[0] = 0b11111000  # rs = 0
        self.cmdbuf[1] = b & 0xF0
        self.cmdbuf[2] = (b & 0x0F) << 4

        submv = self.cmdmv[:3]
        self.spi.write(submv)
        del submv


    def send_address(self, b1, b2):
        self.cmdbuf[0] = 0b11111000  # rs = 0
        self.cmdbuf[1] = b1 & 0xF0
        self.cmdbuf[2] = (b1 & 0x0F) << 4
        self.cmdbuf[3] = b2 & 0xF0
        self.cmdbuf[4] = (b2 & 0x0F) << 4

        submv = self.cmdmv[:5]
        self.spi.write(submv)
        del submv


    def send_data(self, arr):
        arrlen = len(arr)
        count = (arrlen << 1) + 1

        for i in range(count): 
            self.cmdbuf[i] = 0

        self.cmdbuf[0] = 0b11111000 | 0x02  # rs = 1

        for i in range(arrlen):
            self.cmdbuf[1 + (i << 1)] = arr[i] & 0xF0
            self.cmdbuf[2 + (i << 1)] = (arr[i] & 0x0F) << 4

        submv = self.cmdmv[:count]
        self.spi.write(submv)
        del submv


    def clear(self):
        self.fbuff = [[0]*(128//8) for i in range(64)]


    def plot(self, x, y, set):
        if x<0 or x>=128 or y<0 or y>=64:
            return
        if set:
            self.fbuff[y][x//8] |= 1 << (7-(x%8))
        else:
            self.fbuff[y][x//8] &= ~(1 << (7-(x%8)))


    def line(self, x1, y1, x2, y2, set=True):
        diffX = abs(x2-x1)
        diffY = abs(y2-y1)
        shiftX = 1 if (x1 < x2) else -1
        shiftY = 1 if (y1 < y2) else -1
        err = diffX - diffY
        drawn = False

        while not drawn:
            self.plot(x1, y1, set)

            if x1 == x2 and y1 == y2:
                drawn = True
                continue

            err2 = 2 * err
            if err2 > -diffY:
                err -= diffY
                x1 += shiftX
            if err2 < diffX:
                err += diffX
                y1 += shiftY


    def put_char(self, c, x, y):
        y_pos = 0
        i = 8 * ord(c)
        rows = font[i:i+8]

        for i in range(len(rows)): 
            self.fbuff[y+y_pos][x//5] |= rows[i]
            y_pos += 1


    def put_string(self, s, x, y): 
        for i in range(len(s)):
            self.put_char(s[i], x+(i*5), y)


    def put_string_old(self, s, x, y):
        padding = 1
        y_pos = 0
        string_list = ['', '', '', '', '', '', '', '']

        for c in s:
            for i in range(len(font[ord(c)])):
                row = font[ord(c)][i]
                print(row)
                bin_string = bin(row)[2:]

                while len(bin_string) < (5+padding):
                    bin_string = "0" + bin_string

                string_list[i] += bin_string

        for i in range(8):
            string_list[i] = [string_list[i][0+c:8+c] for c in range(0, len(string_list[i]), 8)]

        for bs in string_list:
            x_pos = 0
            for s in bs:
                for i in range(len(s)):
                    self.plot(x+x_pos, y+y_pos, s[i] == "1")
                    x_pos +=1

            y_pos +=1


    def redraw(self, dx1=0, dy1=0, dx2=128, dy2=64):
        self.slaveSelectPin.value(1)

        for i in range(dy2):
            self.send_address(0x80 + i % 32, 0x80 + ((dx1 // 16) + (8 if i >= 32 else 0)))
            self.send_data(self.fbuff[i][dx1 // 16:(dx2 // 8)])

        self.slaveSelectPin.value(0)
