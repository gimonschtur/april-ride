from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.colorpicker import ColorPicker

class PaintWindow(BoxLayout):
    pass

class CPopup(Popup):
    def on_press_dismiss(self, *args):
        self.dismiss()
        return False

class PixPaint(App):
    def build(self):
        pw = PaintWindow()
        popup = CPopup();
        popup.open()
        return pw

if __name__ == '__main__':
    PixPaint().run()
