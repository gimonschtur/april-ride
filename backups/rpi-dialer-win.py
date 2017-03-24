from kivy.app import App
import time, random, serial
from time import gmtime, strftime, localtime
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.core.window import Window
Window.size = (240, 320)


receiverID = '09369356410'



##ser = serial.Serial(
##
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

    deleteMessage = fonaCommand('AT+CMGDA="DEL ALL"')
    if deleteMessage.startswith('OK'):
        print "All messages deleted"
        init_stat += 1
    else:
        print deleteMessage
	
    if init_stat == 5:
        print "Initialization COMPLETED.."
    else:
        print "Initialization INCOMPLETE!"

		
def sendSMS(cellNum, txt):
    noreply = ""
    flag = 1
    ser.write('AT+CMGS=\"' + cellNum + '\"' + '\r\n')
    while flag:
        reply = ser.readline()
        if reply.startswith('>'):
            initsendStat = reply
            flag = 0
    
    if initsendStat.startswith('>'):		
        txtStat = fonaCommand(txt)
        if txtStat.startswith('>'):			
            ser.write(chr(26))
            while (not (noreply.startswith('OK') or noreply.startswith('ERROR'))):				
                noreply = ser.readline()

    return noreply


def startCall(cellNum):
    noreply = ""
    timeOut = 0
    print('Calling ' + cellNum + '..')
    callStat = fonaCommand('ATD' + cellNum + ';')
    if callStat.startswith('OK'):
        print "Calling.."
        startTimer = time.clock()
        while (timeOut < 0):
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
    #sends AT commands to FONA. returns a list of values
    noreply = 1
    ser.write(req + '\r\n')
    item = ""
    indata = ""
    result = []
        
    while noreply:
        reply = ser.readline()
        if reply.startswith('ERROR') or reply.startswith('+'):
            if reply.startswith('ERROR'):
                indata = reply
            else:
                statPos = reply.find(": ")
                indata = reply[(statPos+2):]
            noreply = 0
            
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


class ImageButton(ButtonBehavior, Image):
    pass


class CPopup(Popup):
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False


class DPopup(Popup):
    recepient = StringProperty('EMD')
    
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False
    
    def on_press_dial(self, num):
        self.dialNumber += num

    def FONAendCall(self):
##        endCall()
        pass


class ScreenManagement(ScreenManager):
    pass


class MainScreen(Screen):  
		
    def FONAstartCall(self):
        startCall(receiverID)
        popup = DPopup()
        popup.open()
        
        

class DialScreen(Screen):    
    dialNumber = StringProperty()
    
    def on_press_dial(self, num):
        self.dialNumber += num
        
    def clear_screen(self):
        self.dialNumber = ''

    def call_num(self):
        popup = DPopup()
        popup.recepient = self.dialNumber
        if popup.recepient != '':
            popup.open()
            startCall(popup.recepient)

    def bckSpace(self):
        self.dialNumber = self.dialNumber[:(len(self.dialNumber)-1)]


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
    msgStat = StringProperty()
    msgStat = 'Message sent!'
    
    def build(self):
        root_widget = Builder.load_file("rpi-dialer.kv")
        self.event = Clock.schedule_interval(self.update, 2)
        return root_widget

    def update(self, *args):
        print("Updating..")
        self.timex = strftime("%I:%M %p", localtime())
        self.dayx = strftime("%A", localtime())
        self.datex = strftime("%d", localtime())
        self.monthx = strftime("%b", localtime())
        self.yearx = strftime("%Y", localtime())
##        self.battery_list = categorize_battery(checkLevel('AT+CBC'))
##        self.signal_list = categorize_signal(checkLevel('AT+CSQ'))
##        self.battery = self.battery_list[1]
##        self.signalstrength = self.signal_list
##        self.battPercent = str(int(self.battery_list[2])) + '%'
        self.battery = '100'
        self.signalstrength = '50'
        self.battPercent = str(int(82.0)) + '%'
##        print(str(self.battery_list) + " " + self.signalstrength)

    def FONAstartCall(self):
        popup = DPopup()
        popup.open()
##        startCall(receiverID)

    def FONAsendSMS(self):
        print "Sending message.."
##        sms = sendSMS(receiverID, 'This is a test. So Don\'t bother.')
##        print('sms: ' + str(sms))
##        if sms.startswith('OK'):
##            self.msgStat = 'Message sent!'
##        else:
##            self.msgStat = 'Message failed!'
        popup = CPopup()
        popup.open()
        
    def unschedUpdate(self):
        Clock.unschedule(self.event)

        
    def reschedUpdate(self):
        print("Done")
        self.event = Clock.schedule_interval(self.update, 2)        


##fonaINIT()
time.sleep(0.5)
DialerApp().run()
