import kivy
kivy.require("1.9.0")

import time
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup

class CustomPopup(Popup):
    pass

class SampBoxLayout(BoxLayout):

    checkbox_is_active = ObjectProperty(False)
    localtime = ObjectProperty()

    def update(self, *args):
        self.ids.time_display.text = time.asctime( time.localtime(time.time()) )

    def checkbox_18_clicked(self, instance, value):
        self.ids.gigimon.text = "Hala ka Gigi"
        if value is True:
            print("Checkbox Checked")
            self.ids.gigimon.text = "Hala ka Gigi"
        else:
            print("Checkbox is Unchecked")
            self.ids.gigimon.text = "Ok la it"

    blue = ObjectProperty(True)
    red = ObjectProperty(False)
    green = ObjectProperty(False)

    def switch_on(self, instance, value):
        if value is True:
            print("Switch On")
        else:
            print("Switch Off")

    def open_popup(self):
        the_popup = CustomPopup()
        the_popup.open()

    def spinner_clicked(self, value):
        print("Spinner value: " + value)
        

class SampleApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        mySample = SampBoxLayout()
        Clock.schedule_interval(mySample.update, 1)
        return mySample

sample_app = SampleApp()
sample_app.run()
