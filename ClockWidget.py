import kivy
kivy.require('1.0.5')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, SmoothLine
from kivy.uix.floatlayout import FloatLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder

import datetime

class MyClockWidget(FloatLayout):
    def do_press(self):
        self.ids.label.text='pressed'

    def do_release(self):
        self.ids.label.text=''


class Ticks(Widget):
    def __init__(self, **kwargs):
        super(Ticks, self).__init__(**kwargs)
        self.bind(pos=self.update_clock)
        self.bind(size=self.update_clock)

    def update_clock(self, *args):
        self.canvas.clear()
        with self.canvas:
            time = datetime.datetime.now()
            Color(0.25, 0.25, 0.25)
            hour_radius=0.7
            th = time.hour*60 + time.minute
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+hour_radius*self.r*sin(pi/360*th),
                         self.center_y+hour_radius*self.r*cos(pi/360*th)], width=5, cap="round",
                       overdraw_width=1.6)
            Color(0.35, .35, 0.35)
            min_radius=1
            tm = time.minute + time.second/60.0
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+min_radius*self.r*sin(pi/30*tm),
                         self.center_y+min_radius*self.r*cos(pi/30*tm)], width=4, cap="round",
                       overdraw_width=1.6)
            Color(0.8, 0.2, 0.2)
            sec_radius=1.06
            ts = time.second+time.microsecond / 1000000.0
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+sec_radius*self.r*sin(pi/30*ts),
                         self.center_y+sec_radius*self.r*cos(pi/30*ts)], width=2, cap="round",
                       overdraw_width=1.6)

Builder.load_file('MyClock.kv')

class MyClockApp(App):
    def build(self):
        clock = MyClockWidget()
        Clock.schedule_interval(clock.ticks.update_clock, 0.1)
        return clock

if __name__ == '__main__':
    MyClockApp().run()