import RPi.GPIO as GPIO
from gpiozero import LED, Button

keypad = [ ['1','2','3'],
            ['4','5','6'],
            ['7','8','9'],
            ['*',0,'#'],]
row = [7,11,13,15]
col = [12,16,18]
values = { '1':['','*','#'],
           '2':['a','b','c'],
           '3':['d','e','f'],
           '4':['g','h','i'],
           '5':['j','k','l'],
           '6':['m','n','o'],
           '7':['p','q','r'],
           '8':['s','t','u','v'],
           '9':['w','x','y','z'],
           '*':['shift'],
           '0':['0','space'],
           '#':['0','back'],}
class Keypad(object):
    GPIO.setmode(GPIO.BOARD)
    count = 0
    prevkey = None
    def __init__(self):
        for x in range(3):
            GPIO.setup(col[x], GPIO.OUT)
            GPIO.output(col[x], 1)
        for y in range(4):
            GPIO.setup(row[y], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    def start(self):
        try:
            while(True):
                for x in range(3):
                    GPIO.output(col[x], 0)
                    for y in range(4):
                        if GPIO.input(row[y])==0:
                            while (GPIO.input(row[y])==0):
                                if keypad[y][x]=='5':
                                    pass # hold to three
                            self.get_keys(keypad[y][x])
                    GPIO.output(col[x], 1)
        except KeyboardInterrupt:
            GPIO.cleanup()
    def get_keys(self,key):
        print key
        if self.prevkey == key:
            self.count+=1
            if len(values.get(key))==self.count:
                self.count = 0
                return
            print values.get(key)[self.count]
            return
        self.count=0
        self.prevkey = key
class Display(object):
    def __init__(self):
        pass
a = Keypad()
a.start()
