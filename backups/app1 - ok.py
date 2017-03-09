from kivy.app import App
import time
import serial
from time import gmtime, strftime, localtime
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
Window.size = (240, 320)

import random


receiverID = '09778201866'



##ser = serial.Serial(
##  
##   # port='/dev/serial0',
##   port='/dev/ttyS0',
##   baudrate = 9600,
##   parity=serial.PARITY_NONE,
##   stopbits=serial.STOPBITS_ONE,
##   bytesize=serial.EIGHTBITS,
##   timeout=1
##)


def fonaCommand(req):
    noreply = 1
    ser.write(req + '\r\n')
	
    while noreply:
        reply = ser.readline()
        if reply.startswith('OK') or reply.startswith('NO CARRIER') or reply.startswith('ERROR') or reply.startswith('>'):
            return reply
            noreply = 0
			
def fonaINIT():
    init_stat = 0
	
    ATstat = fonaCommand('AT')
    ATstat = fonaCommand('AT')
    if ATstat.startswith('OK'):
        print "AT initialization done"
        init_stat += 1
    else:
        print ATstat
		
    SIMstat = fonaCommand('AT+CCID')
    if SIMstat.startswith('OK'):
        print "SIM card is OK"
        init_stat += 1
    else:
        print SIMstat
		
    COPSstat = fonaCommand('AT+COPS?')
    if COPSstat.startswith('OK'):
        print "Signal is OK"
        init_stat += 1
    else:
        print COPSstat
	
    MessageMode = fonaCommand('AT+CMGF=1')
    if MessageMode.startswith('OK'):
        print "Message mode activated"
        init_stat += 1
    else:
        print MessageMode
	
    if init_stat == 4:
        print "Initialization COMPLETED.."
    else:
        print "Initialization INCOMPLETE!"
		
def sendSMS(cellNum, txt):
    noreply = ""
    initsendStat = fonaCommand('AT+CMGS=\"' + cellNum + '\"')
    if initsendStat.startswith('>'):		
        txtStat = fonaCommand(txt)
        if txtStat.startswith('>'):			
            ser.write(chr(26))
            while (not (noreply.startswith('OK') or noreply.startswith('ERROR'))):				
                noreply = ser.readline()
                print noreply				
            print "Successfully sent!"

def startCall(cellNum):
    noreply = ""
    timeOut = 0
    callStat = fonaCommand('ATD' + cellNum + ';')
    if callStat.startswith('OK'):
        print "Calling.."
        startTimer = time.clock()
        while (timeOut < 10):
            endTimer = time.clock()
            noreply = ser.readline()
            if (noreply.startswith('NO CARRIER')):
                print "No Carrier"
                break
            elif (noreply.startswith('BUSY')):
                print "BUSY"
                break
            elif (noreply.startswith('NO ANSWER')):
                print "NO ANSWER"
                break
            elif (noreply.startswith('NO DIALTONE')):
                print "NO DIALTONE"
                break
            timeOut = 1000 * (endTimer - startTimer)

def endCall():
    endstat = fonaCommand('ATH')
    if endstat.startswith('OK'):
        print "Call ended"

def checkLevel(req):
    noreply = 1
    ser.write(req + '\r\n')
	
    while noreply:
        reply = ser.readline()
        if reply.startswith('ERROR') or reply.startswith('+'):
            if reply.startswith('ERROR'):
                return reply
            else:
                statPos = reply.find(": ")
                return reply[(statPos+2):]
            noreply = 0

def csvToList(indata):
    item = ""
    result = []
    for (i, data) in enumerate(indata):
        if data != ",":
            item += data 
        if data == "," or i == (len(indata)-1):
            result.append(float(item))
            item = ""
    return result
	
def categorize_signal(inSignal):
    #returns signal status - filename of the corresponding image
    asu = inSignal[0]
    if asu >= 22:
        return '100'
    elif asu >= 14 and asu <= 21:
        return '75'
    elif asu >= 7 and asu <= 13:
        return '50'
    elif asu >= 2 and asu <= 6:
        return '25'
    elif asu < 2:
        return 'no_signal'
                    
def categorize_battery(inBatt):
    #returns a list containing: full charge flag, battery status (fname of the corr. image), battery percentage

    isCharging = inBatt[0]
    battPercent = inBatt[1]
    result = [0, '', battPercent]
    
    if isCharging == 2:
        result[0] = '1'  
    if isCharging == 1:
        result[1] = 'charge'  
    elif (isCharging == 0 and battPercent > 75 and battPercent <= 100) or isCharging == 2:
        result[1] = '100'
    elif isCharging == 0 and battPercent > 50 and battPercent <= 75:
        result[1] = '75'
    elif isCharging == 0 and battPercent > 25 and battPercent <= 50:
        result[1] = '50'
    elif isCharging == 0 and battPercent < 25:
        result[1] = '25'

    return result

class CPopup(Popup):
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False

class ScreenManagement(ScreenManager):
    pass

class MainScreen(Screen):
    
    def on_pressed(self):
        print "Pressed"
        popup = CPopup()
        popup.open()
        #time.sleep(3)
        
    def FONAsendSMS(self):
        pass
        #time.sleep(5)
        #sendSMS(receiverID, 'This is a test. So Don\'t bother.')

		
    def FONAstartCall(self):
        #startCall(receiverID)
        pass
        
        
class DialScreen(Screen):
    def on_pressed(self):
        pass
    def FONAendCall(self):
        #endCall()
        pass

    
class DialerApp(App):
    timex = StringProperty()
    dayx = StringProperty()
    datex = StringProperty()
    monthx = StringProperty()
    yearx = StringProperty()
    battery_list = []
    signal_list = ''
    battery = StringProperty()
    battPercent = StringProperty()
    signalstrength = StringProperty()
    
    def build(self):
        #Window.clearcolor = (1, 1, 1, 1)
        root_widget = Builder.load_file("tu.kv")
        Clock.schedule_interval(self.update, 2)
        return root_widget

    def update(self, *args):
        self.timex = strftime("%I:%M %p", localtime())
        self.dayx = strftime("%A", localtime())
        self.datex = strftime("%d", localtime())
        self.monthx = strftime("%b", localtime())
        self.yearx = strftime("%Y", localtime())
##        self.battery_list = categorize_battery(csvToList(checkLevel('AT+CBC')))
##        self.signal_list = categorize_signal(csvToList(checkLevel('AT+CSQ')))
##        self.battery = self.battery_list[1]
##        self.signalstrength = self.signal_list
##        self.battPercent = str(int(self.battery_list[2])) + '%'
        self.battery = 'charge'
        self.signalstrength = '25'
        self.battPercent = str(int(100.0)) + '%'
        #print(str(self.battery_list) + " " + self.signalstrength)


##fonaINIT()
time.sleep(0.5)
DialerApp().run()
