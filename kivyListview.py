from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.lang import Builder
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.listview import ListItemButton
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.widget import Widget
import vlc
import requests
from time import sleep
import random
from os import listdir, path

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

player = vlc.MediaPlayer(medias[0])

Builder.load_file('kivyListview.kv')

class MenuButton(ListItemButton):
    index = NumericProperty(0)


class MenuPageScreen(Screen):
    M = SoundLoader.load('http://stream.srg-ssr.ch/m/rsj/mp3_128')

    def plays(self,index):
        if not MenuPageScreen.M is None:
            if MenuPageScreen.M.state == 'stop':
                MenuPageScreen.M.play()
            else:
                MenuPageScreen.M.stop()

    def args_converter(self, row_index, title):
        print ("{0}={1}".format(row_index, title))
        names = title.split('/')
        return {
            'index': row_index,
            'text': names[-1]
        }


class PageScreen(Screen):
    labelText = StringProperty('Pause')
    index = NumericProperty(0)
    songTitle = StringProperty(' ')
    songArtist = StringProperty(' ')
    playVolume = NumericProperty(100)

    def on_pre_enter(self):
        self.index = int(self.index)
        print('Entering, index{}'.format(self.index))
        if player.is_playing():
            player.stop()
        print("Play " + medias[self.index])
        media = Instance.media_new(medias[self.index])
        player.set_media(media)
        player.audio_set_volume(100)

        media.parse()
        if media.is_parsed():
            try:
                if not media.get_meta(0) is None:
                    self.songTitle = media.get_meta(0).decode('utf-8')
                    print("Tislider texttle        : {}".format(media.get_meta(0).decode('utf-8')))
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
            self.labelText="Play"
        else:
            player.play()
            self.labelText="Pause"

    def set_volume(self, volume):
        player.audio_set_volume(int(volume))
        self.playVolume = volume

class TestApp(App):
    data = ListProperty(medias)
    playScreen = None

    def build(self):
        sm = ScreenManager(transition=SwapTransition (direction='right'))
        self.menu = MenuPageScreen(name='menu')
        sm.add_widget(self.menu)
        self.playScreen = PageScreen(name='play')
        self.playScreen.index = 0
        sm.add_widget(self.playScreen)
        return sm

    def on_menu_selection(self, index):
        print(index)
        self.playScreen.index = index
        self.root.current = 'play'
        # self.sm.get_screen(str(index)).index=index
        self.menu.plays(index)

    def stop_and_return(self):
        self.root.direction= 'left'
        self.root.current = 'menu'



if __name__ == '__main__':
    TestApp().run()