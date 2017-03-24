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
##from kivy.core.window import Window
##Window.size = (240, 320)



ser = serial.Serial(
  
   # port='/dev/serial0',
   port='/dev/ttyS0',
   baudrate = 9600,
   parity=serial.PARITY_NONE,
   stopbits=serial.STOPBITS_ONE,
   bytesize=serial.EIGHTBITS,
   timeout=1
)


def fonaCommand(req):
    ser.write(req + '\r\n')
	
    while True:
        reply = ser.readline()
        if reply.startswith('OK') or reply.startswith('NO CARRIER') or reply.startswith('ERROR') or reply.startswith('>'):
            return reply
            break

			
def fonaINIT():
    init_stat = 0
	
    ATstat = fonaCommand('AT')
    ATstat = fonaCommand('AT')
    if ATstat.startswith('OK'):
        init_stat += 1
    print "AT: " + ATstat
            
    SIMstat = fonaCommand('AT+CCID')
    if SIMstat.startswith('OK'):
        init_stat += 1
    print "SIM: " + SIMstat
		
    COPSstat = fonaCommand('AT+COPS?')
    if COPSstat.startswith('OK'):
        init_stat += 1
    print "Signal: " + str(COPSstat)
	
    MessageMode = fonaCommand('AT+CMGF=1')
    if MessageMode.startswith('OK'):
        init_stat += 1
    print "Message Mode: " + str(MessageMode)

    deleteMessage = fonaCommand('AT+CMGDA="DEL ALL"')
    if deleteMessage.startswith('OK'):
        init_stat += 1
    print "Msg Del: " + str(deleteMessage)
	
    if init_stat == 5:
        print "Initialization COMPLETED.."
    else:
        print "Initialization INCOMPLETE!"

		
def sendSMS(cellNum, txt):
    noreply = ""
    ser.write('AT+CMGS=\"' + cellNum + '\"' + '\r\n')
    while True:
        reply = ser.readline()
        if reply.startswith('>'):
            initsendStat = reply
            break
    
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
    callStat = fonaCommand('ATD' + cellNum + ';')
    if callStat.startswith('OK'):
        print('Calling ' + cellNum + '..')

    return callStat


def endCall():
    endstat = fonaCommand('ATH')
    if endstat.startswith('OK'):
        print "Call ended"


class params:
    battery_list = []
    signal_list = ''
    battStat = StringProperty()
    battPercent = StringProperty()
    signalstrength = StringProperty()

    def sendATcommand(self, req):
        #sends AT commands to FONA. returns a list of values
        ser.write(req + '\r\n')
        item = ""
        indata = ""
        result = []
            
        while True:
            reply = ser.readline()
            if reply.startswith('ERROR') or reply.startswith('+CBC') or reply.startswith('+CSQ'):
                if reply.startswith('ERROR'):
                    indata = reply
                else:
                    statPos = reply.find(": ")
                    indata = reply[(statPos+2):]
                    break
        for (i, data) in enumerate(indata):
            if data != ",":
                item += data 
            if data == "," or i == (len(indata)-1):
                result.append(float(item))
                item = ""
                
        return result


    def checkSignal(self, inSignal):
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


    def checkBatt(self, inBatt):
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


    def checkLevels(self):
        self.battery_list = self.checkBatt(self.sendATcommand('AT+CBC'))            
        self.signal_list = self.checkSignal(self.sendATcommand('AT+CSQ'))
        self.battStat = self.battery_list[1]
        self.signalstrength = self.signal_list
        self.battPercent = str(int(self.battery_list[2])) + '%'


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

class InCallPopup(Popup):
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False


class ScreenManagement(ScreenManager):
    pass


class MainScreen(Screen):  		
    pass

class DialScreen(Screen):    
    dialNumber = StringProperty()
    
    def on_press_dial(self, num):
        self.dialNumber += num
        
    def clear_screen(self):
        self.dialNumber = ''

    def bckSpace(self):
        self.dialNumber = self.dialNumber[:(len(self.dialNumber)-1)]


class DialerApp(App):
    receiverID = '09369356410'
    timex = StringProperty()
    dayx = StringProperty()
    datex = StringProperty()
    monthx = StringProperty()
    yearx = StringProperty()
    msgStat = StringProperty() 
    battery = StringProperty()
    battPercent = StringProperty()
    signalstrength = StringProperty()
    callStatus = StringProperty("Calling")
    callIcon = StringProperty("call_ok") 
    
    def build(self):
        root_widget = Builder.load_file("rpi-dialer.kv")
        self.event = Clock.schedule_interval(self.update, 2)
        return root_widget

    def update(self, *args):
        param = params()
        print("Updating..")
        self.timex = strftime("%I:%M %p", localtime())
        self.dayx = strftime("%A", localtime())
        self.datex = strftime("%d", localtime())
        self.monthx = strftime("%b", localtime())
        self.yearx = strftime("%Y", localtime())
        
##        ------For windows testing------
##        self.battery = '100'
##        self.signalstrength = '50'
##        self.battPercent = str(int(82.0)) + '%'
##        ------For windows testing------

        try:
            param.checkLevels()
        except Exception as err:
            print str(err)
        else:
            self.battery = param.battStat
            self.signalstrength = param.signalstrength
            self.battPercent = param.battPercent            
        print(str(self.battery) + " " + str(self.battPercent) + " " + self.signalstrength)
        
    def incomingCall(self):
        popup = InCallPopup()
        popup.open()

    def FONACallEMD(self, rcvID):
        self.unschedUpdate()
        popup = DPopup()
        popup.open()
        call = startCall(rcvID)
        print "Call: " + str(call)
        self.schedCallstat()

    def FONACallother(self, rcvID):
        self.unschedUpdate()
        popup = DPopup()
        popup.recepient = rcvID
        if rcvID != '':
            popup.open()
            call = startCall(rcvID)
            print "Call: " + str(call)
        self.schedCallstat()       
            
    def FONAendCall(self):
        endCall()
        self.callStatus = "Calling"
        self.callIcon = 'call_ok'
        self.unschedCallstat()
        self.reschedUpdate()

    def FONAsendSMS(self, rcvID):
        print "Sending message.."
        sms = sendSMS(rcvID, 'This is a test. So Don\'t bother.')
        print('sms: ' + str(sms))
        if sms.startswith('OK'):
            self.msgStat = 'Message sent!'
        else:
            self.msgStat = 'Message failed!'
        popup = CPopup()
        popup.open()

    def checkCallStat(self, *args):        
        noreply = ser.readline()
        print "Checking call stat.."
        if (noreply.startswith('NO CARRIER')):
            print "No Carrier"
            self.callStatus = "No Carrier"
            self.callIcon = 'call_nocarrier'
            self.unschedCallstat()
        elif (noreply.startswith('BUSY')):
            print "Busy"
            self.callStatus = "Busy"
            self.callIcon = 'call_busy'
            self.unschedCallstat()
        elif (noreply.startswith('NO ANSWER')):
            print "No Answer"
            self.callStatus = "No Answer"
            self.callIcon = 'call_blocked'
            self.unschedCallstat()
        elif (noreply.startswith('NO DIALTONE')):
            print "No Dialtone"
            self.callStatus = "No Dialtone"
            self.callIcon = 'call_nocarrier'
            self.unschedCallstat() 
        
    def unschedUpdate(self):
        Clock.unschedule(self.event)
        print "Update STOP"

    def reschedUpdate(self):
        print "Update START"
        self.event = Clock.schedule_interval(self.update, 2)

    def schedCallstat(self):
        self.callevent = Clock.schedule_interval(self.checkCallStat, 1)

    def unschedCallstat(self):
        Clock.unschedule(self.callevent)


fonaINIT()
time.sleep(0.5)
DialerApp().run()
