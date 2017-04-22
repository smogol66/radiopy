import kivy
kivy.require('1.0.5')
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.listview import ListItemButton
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, SmoothLine
from kivy.uix.floatlayout import FloatLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
import vlc
from os import listdir, path
import datetime

rpi = False
try:
  import RPi.GPIO as gpio
  rpi = True
except ImportError:
  rpi = False

if rpi:
    Instance = vlc.Instance('--aout=alsa', '--alsa-audio-device=dmixer')
else:
    Instance = vlc.Instance()

if rpi:
    basepath = '/home/pi/sound/Audio/'
else:
    basepath = '/home/Gemeinsame Dateien/Audio'
    #  basepath= '/home/Gemeinsame Dateien/Audio/'

medias = []
medias.append("http://stream.srg-ssr.ch/m/rsj/mp3_128")
medias.append("http://streaming.radio.funradio.fr/fun-1-48-192")
medias.append("http://streaming.radio.rtl2.fr/rtl2-1-44-128")
medias.append("http://stream.srg-ssr.ch/m/couleur3/mp3_128")
print('I am here '+ basepath)
tmp = 4
for f in listdir(basepath):
    if f.lower().endswith('.mp3'):
        tmp += 1
        url = path.join(basepath,f)
        medias.append(url)
        # print(url)

media_list = Instance.media_list_new()
player = Instance.media_player_new()
list_player = Instance.media_list_player_new()
list_player.set_media_player(player)

#create a vlc medial list from the medias
for url in medias:
    item = Instance.media_new(url)
    media_list.add_media(item.get_mrl())

list_player.set_media_list(media_list)

Builder.load_file('kivyListview.kv')

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


class MenuButton(ListItemButton):
    index = NumericProperty(0)


class MenuPageScreen(Screen):

    def plays(self,index):
        pass

    def args_converter(self, row_index, title):
        print ("{0}={1}".format(row_index, title))
        names = title.split('/')
        return {
            'index': row_index,
            'text': names[-1]
        }


class PageScreen(Screen):
    labelImage = StringProperty('img/pause.png')
    index = NumericProperty(0)
    songTitle = StringProperty(' ')
    songArtist = StringProperty(' ')
    playVolume = NumericProperty(100)
    last_index = 0

    def on_pre_enter(self):
        self.index = int(self.index)
        print('Entering, index{}'.format(self.index))

        media = Instance.media_new(medias[self.index])
        if list_player.is_playing():
            if self.last_index != self.index:
                self.last_index = self.index
                list_player.stop()
            else:
                return  # continue to play the same song
        print("Play " + medias[self.index])

        list_player.play_item_at_index(self.index)

        media.parse()
        if media.is_parsed():
            try:
                self.songTitle = ''
                if not media.get_meta(0) is None:
                    self.songTitle = media.get_meta(0).decode('utf-8')
                    print("Title        : {}".format(media.get_meta(0).decode('utf-8')))
                self.songArtist = ''
                if not media.get_meta(1) is None:
                    self.songArtist = media.get_meta(1).decode('utf-8')
                    print("Artist       : {}".format(media.get_meta(1).decode('utf-8')))
                print self.songTitle
            except:
                pass  # do not print nothing
            m, s = divmod(media.get_duration() / 1000, 60)
            h, m = divmod(m, 60)
            print("Song duration: {:02d}:{:02d}:{:02d}".format(h, m, s))
        player.play()

    def plays(self):
        if player.is_playing():
            player.pause()
            self.labelImage='img/play.png'
        else:
            player.play()
            self.labelImage='img/pause.png'

    def prev_song(self):
        self.index -= 1
        if self.index < 0:
            self.index = len(medias)-1
        print(self.index)
        self.on_pre_enter()

    def next_song(self):
        self.index += 1
        if self.index > len(medias)-1:
            self.index = 0
        self.on_pre_enter()

    def set_volume(self, volume):
        player.audio_set_volume(int(volume))
        self.playVolume = volume


class ClockScreen(Screen):
    def do_press(self):
        self.ids.label.text='pressed'

    def do_release(self):
        self.ids.label.text=''


class TestApp(App):
    data = ListProperty(medias)
    playScreen = None
    menuScreen = None
    clockScreen = None
    last_index = -1

    def build(self):
        sm = ScreenManager(transition=SwapTransition (direction='right'))
        self.menuScreen = MenuPageScreen(name='menu')
        sm.add_widget(self.menuScreen)
        self.playScreen = PageScreen(name='play')
        self.playScreen.index = 0
        sm.add_widget(self.playScreen)
        self.clockScreen = ClockScreen(name='clock')
        sm.add_widget(self.clockScreen)
        Clock.schedule_interval(self.clockScreen.ticks.update_clock, 0.1)
        return sm

    def on_menu_selection(self, index):
        print(index)
        if index != self.last_index:
            self.last_index = index
        else:
            pass
            # TODO:: avoid the selected item to toggle

        self.playScreen.index = index
        self.root.current = 'play'
        self.menuScreen.plays(index)

    def stop_and_return(self):
        self.root.current = 'menu'

    def show_clock(self):
        self.root.current = 'clock'

    def show_player(self):
        self.root.current = 'play'



if __name__ == '__main__':
    TestApp().run()