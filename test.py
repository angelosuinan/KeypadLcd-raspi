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
    display_string = ""
    same = 0
    cursorx = 0
    cursory = 0
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
            start=time.time()
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
                    GPIO.output(col[x], 1)

        except KeyboardInterrupt:
            GPIO.cleanup()
    def get_keys(self,key):
        if self.prevkey ==key:
            self.count+=1;
            if len(values.get(key)) ==1:
                self.count = 0 ; self.prevkey = None; 
                return
            print values.get(key)[self.count] # change current char
            if self.count == len(values.get(key))-1:
                self.count =0; self.prevkey = None; same=self.prevkey
            return
        self.count =0
        self.prevkey=key
        if self.same == key:
            print values.get(key)[self.count] #change current char
            return
        print values.get(key)[self.count] #add char
        self.parse_string(values.get(key)[self.count])
    def parse_string(self,char):
        before= self.display_string
        if not before:
            self.display_string += char
        print self.display_string
        lcd.clear()
        lcd.blink(True)
        if len(self.display_string)==17:
            self.display_string = self.display_string[:16] + "\n" + self.display_string[16:]
        if len(self.display_string)>=32:
            lcd.message(before)
            return
        self.show()
    def cursor_update(x,y):
        pass
    def show(self):
        lcd.message(self.display_string)
a = Keypad()
a.start()
