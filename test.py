import RPi.GPIO as GPIO
from gpiozero import LED, Button
from time import sleep
import Adafruit_CharLCD as LCD
import time
from threading import Timer
keypad = [ ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*','0','#'],]
row = [4,17,27,22] # 2 7 6 5     7 11 13 15
col = [18,23,24] # 3 1 4         12 16 18
values = { '1':['1','*','#'],
           '2':['a','b','c','2'],
           '3':['d','e','f','3'],
           '4':['g','h','i','4'],
           '5':['j','k','l','5'],
           '6':['m','n','o','6'],
           '7':['p','q','r','7'],
           '8':['s','t','u','v','8'],
           '9':['w','x','y','z','9'],
           '*':['shift'],
           '0':['space'],
           '#':['back'],}
lcd = LCD.Adafruit_CharLCD(26,19, 13, 6, 5, 11,
                                   16, 2, 4)
lcd.show_cursor(True)
class Keypad(object):
    count = 0
    prevkey = None
    _string = ""
    char = ""
    same = None
    cursorx = 0
    cursory = 0
    cursorm =None
    shiftmode= None
    def __init__(self):
        for x in range(3):
            GPIO.setup(col[x], GPIO.OUT)
            GPIO.output(col[x], 1)
        for y in range(4):
            GPIO.setup(row[y], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    def get_present(self,start):
        return time.time()-start
    def start(self):
        try:
            start = time.time()
            timeout =None
            while(True):
                for x in range(3):
                    GPIO.output(col[x], 0)
                    for y in range(4):
                        if GPIO.input(row[y])==0:
                            while (GPIO.input(row[y])==0):
                                if keypad[y][x]=='5':
                                    pass # hold to three
                            self.get_keys(keypad[y][x])
                            sleep(.3)
                            if not (keypad[y][x] in ['*','#']) :
                                timeout = self.get_present(start)
                            if self.cursorx >0 and timeout:
                                lcd.set_cursor(self.cursorx-1,self.cursory)
                    if timeout:
                        if self.get_present(start) - timeout >=3:
                            self.csr_upd()
                            self.prevkey, self.same = None, None
                            present = None
                            self.count =0
                            timeout = None
                    GPIO.output(col[x], 1)
        except KeyboardInterrupt:
            GPIO.cleanup()
    def get_keys(self,key):
        self.char = str(values.get(key)[self.count])
        if key == '*' or key == '#':
            self.spc_func(key)
            self.csr_upd()
            return
        if len(self._string)>=32:
            return
        if self.shiftmode:
            self.char = self.char.capitalize()
        if self.prevkey ==key:
            self.count+=1                             # change current char
            self.char = values.get(key)[self.count]
            self.chg_char()
            if self.shiftmode:
                self.char = self.char.capitalize()
            if self.count == len(values.get(key))-1:
                self.count =0; self.same=self.prevkey; self.prevkey=None
            return
        self.prevkey=key
        if self.same == key: #change current char
            self.chg_char()
            return
        self.add_char()
    def add_char(self): #add char
        self._string = (self._string[:self.cursorx] + self.char
                +self._string[self.cursorx:])#add to current cursor
        self.cursorx+=1
        self.show()
    def chg_char(self):
        self._string = (self._string[:self.cursorx-1] + self.char +
                self._string[self.cursorx:])
        self.show()
    def csr_upd(self):
        lcd.set_cursor(self.cursorx,self.cursory)
    def show(self):
        lcd.clear()
        lcd.blink(True)
        if len(self._string)==17 and "\n" not in self._string:
            self._string = self._string[:16] + "\n" + self._string[16:]
        if len(self._string)==16:
            str.replace("\n", "")
        lcd.message(self._string)
    def spc_func(self, func):
        if func == "*":
            if self.shiftmode:
                self.shiftmode =None
            elif not self.shiftmode:
                self.shiftmode = 1
            return
        if len(self._string) > 0:
            self._string = (self._string[:self.cursorx-1]+
                    self._string[self.cursorx:])
            self.cursorx-=1
            self.show()
            print self.cursorx
a = Keypad()
a.start()
