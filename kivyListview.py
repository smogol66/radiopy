from kivy.uix.screenmanager import ScreenManager, Screen
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
# shuffle it
random.shuffle(medias)

player = vlc.MediaPlayer(medias[0])

Builder.load_file('kivyListview.kv')

class MenuButton(ListItemButton):
    index = NumericProperty(0)


class MenuPageScreen(Screen):
    M = SoundLoader.load('http://stream.srg-ssr.ch/m/rsj/mp3_128')

    def plays(self):
        if not MenuPageScreen.M is None:
            if MenuPageScreen.M.state == 'stop':
                MenuPageScreen.M.play()
            else:
                MenuPageScreen.M.stop()

    def args_converter(self, row_index, title):
        print ("{0}={1}".format(row_index, title))
        return {
            'index': row_index,
            'text': title
        }


class PageScreen(Screen):
    labelText = StringProperty('My label')
    index = NumericProperty('My Label')

    def plays(self):
        if player.is_playing():
            player.pause()
        else:
            print("Play " + self.labelText)
            media = Instance.media_new(self.labelText)
            player.set_media(media)
            player.audio_set_volume(100)
            player.play()


class TestApp(App):
    # data = ListProperty(["Item #{0}".format(i) for i in range(50)])
    data = ListProperty(medias)

    def build(self):
        sm = ScreenManager()
        self.menu = MenuPageScreen(name='menu')
        sm.add_widget(self.menu)
        for i in range(tmp):
            name = PageScreen(name=str(i))
            name.index = int(i)
            name.labelText = medias[i]
            sm.add_widget(name)
        return sm

    def on_menu_selection(self, index):
        print(index)
        self.root.current = str(index)
        # self.sm.get_screen(str(index)).index=index
        self.menu.plays()

    def stop_and_return(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    TestApp().run()