import RPi.GPIO as GPIO
from gpiozero import LED, Button
from time import sleep
import Adafruit_CharLCD as LCD
import time
keypad = [ ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*','0','#'],]
row = [4,17,27,24] # 2 7 6 4    7 11 13 18
col = [18,23,22] # 3 1 5        12 16 15
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
           '0':['0', ' '],
           '#':['back'],}
lcd = LCD.Adafruit_CharLCD(26,19, 13, 6, 5, 11,
                                   16, 2, 4)
lcd.show_cursor(True)
class Keypad(object):
    count = 0
    prevkey = None
    _string = char = ""
    same = None
    csrx = 0
    csry = 0
    csrm =None
    shiftmode= None
    def __init__(self):
        for x in range(3):
            GPIO.setup(col[x], GPIO.OUT)
            GPIO.output(col[x], 1)
        for y in range(4):
            GPIO.setup(row[y], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(21,GPIO.OUT)
        GPIO.output(21, 0)
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
                            hold = self.get_present(start)
                            while (GPIO.input(row[y])==0):
                                if keypad[y][x]=='5':
                                    if self.get_present(start) - hold >=3:
                                        GPIO.output(21, 1)
                                        self.csrm=1
                            if self.csrm:
                                self.mv_csr(keypad[y][x])
                            else:
                                self.get_keys(keypad[y][x])
                            sleep(.3)
                            if not (keypad[y][x] in ['*','#']) :
                                timeout = self.get_present(start)
                            if self.csrx >0 and timeout:
                                lcd.set_cursor(self.csrx-1,self.csry)
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
    def mv_csr(self,direction):
        limit = len(self._string)
        if direction is '5':
            self.csrm = None
        elif direction is '2':
            if len(self._string) > 0:
                self.csrx-=1
        elif direction is '6':
            if self.csrx< len(self._string):
                self.csrx+=1
        elif direction is '2':
            self.csry=0
        elif direction is '8':
            if len(self._string) >=16:
                self.csry=1
        else:
            pass
        self.csr_upd()
    def get_keys(self,key):
        if key in ['*', '#']:
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
        self.count = 0
        self.char = str(values.get(key)[self.count])
        self.prevkey=key
        if self.shiftmode:
            self.char = self.char.capitalize()
        if self.same == key: #change current char
            self.chg_char()
            return
        self.add_char()
    def add_char(self): #add char
        self._string = (self._string[:self.csrx] + self.char
                +self._string[self.csrx:])#add to current cursor
        self.csrx+=1
        self.show()
    def chg_char(self):
        self._string = (self._string[:self.csrx-1] + self.char +
                self._string[self.csrx+1:])
        self.show()
    def csr_upd(self):
        if len(self._string)>=16:
            lcd.set_cursor(self.csrx-16,self.csry)
            return
        lcd.set_cursor(self.csr,self.csry)
        print self.csrx, "    ", self.csry
    def show(self):
        lcd.clear()
        lcd.blink(True)
        todisplay = self._string
        if len(self._string)>=16 :
            todisplay = self._string[:16] + '\n'+ self._string[16:]
            self.csry=1
        elif len(self._string)<=15:
            self.csry=0
            todisplay.replace('\n', '')
        lcd.message(todisplay)
    def spc_func(self, func):
        if func == "*":
            if self.shiftmode:
                self.shiftmode =None
            elif not self.shiftmode:
                self.shiftmode = 1
            return
        if len(self._string) > 0:
            self._string = (self._string[:self.csrx-1]+
                    self._string[self.csrx:])
            self.csrx-=1
            self.show()
            self.count =0
a = Keypad()
a.start()
