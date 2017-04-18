from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.listview import ListItemButton
from kivy.properties import ListProperty, NumericProperty
import requests
import vlc
from time import sleep
import random
from os import  listdir, path

rpi = False
if rpi:
    i = vlc.Instance('--aout=alsa', '--alsa-audio-device=dmixer')
else:
    i = vlc.Instance()

medialist = i.media_list_new()
p = i.media_list_player_new()
pl = i.media_player_new()
p.set_media_player(pl)

if rpi:
    basepath = '/home/pi/sound/Audio/'
else:
    basepath = '/home/juan/Musique/'
    #  basepath= '/home/Gemeinsame Dateien/Audio/'

playlists = set(['pls','m3u'])
medias = []
Instance = vlc.Instance()

Builder.load_string('''
#:import la kivy.adapters.listadapter
#:import factory kivy.factory

<MenuButton>:
    size_hint_y: None
    height: dp(30)
    on_release: app.on_menu_selection(self.index)

<MenuPage>:
    BoxLayout:
        BoxLayout:
            size_hint:(.1, None)
            Button:
                text: 'Credit'
                #on_press:root.show_popup()
        ListView:
            size_hint: .8,.9
            adapter:
                la.ListAdapter(
                data=app.data,
                cls=factory.Factory.MenuButton,
                selection_mode='single',
                allow_empty_selection=True,
                args_converter=root.args_converter)



<Page>:
    BoxLayout:
        BoxLayout:
            size_hint:(.1, None)
            Button:
                text: 'MENU'
                on_press:
                    app.stop_and_return()
        BoxLayout:
            orientation:'vertical'
            Button:
                id: 'titleButton'
                text:'Title'
                size_hint:(1, .2)
            Image:
                source: 'carrousel_fictions132.png'
                size_hint:(1, .8)

''')

class MenuButton(ListItemButton):
    index = NumericProperty(0)


class MenuPage(Screen):
    # M = SoundLoader.load('/usr/share/sounds/ubuntu/stereo/bell.ogg')
    M = SoundLoader.load('http://stream.srg-ssr.ch/m/rsj/mp3_128')

    def plays(self,url):
        if not MenuPage.M is None:
            if MenuPage.M.state == 'stop':
                MenuPage.M.play()
            else:
                MenuPage.M.stop()

    def args_converter(self, row_index, title):
        print ("{0}={1}".format(row_index, title))

        return {
            'index': row_index,
            'text': title
        }

    def stop_and_return(self):
        self.root.current = 'main'

class Page(Screen):
    pass


class TestApp(App):
    data = medialist

    def build(self):
        sm = ScreenManager()
        self.menu = MenuPage(name='menu')
        sm.add_widget(self.menu)
        for i, media in enumerate(medialist) :

            name = Page(name=str(i))
            sm.add_widget(media)
        return sm

    def on_menu_selection(self, index):
        self.root.current = str(index)
        self.menu.plays(medialist[index])

    def stop_and_return(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    # create a list of medias

    medias.append("http://stream.srg-ssr.ch/m/rsj/mp3_128")
    medias.append("http://streaming.radio.funradio.fr/fun-1-48-192")
    medias.append("http://streaming.radio.rtl2.fr/rtl2-1-44-128")
    medias.append("http://stream.srg-ssr.ch/m/couleur3/mp3_128")
    tmp = 4
    for f in listdir(basepath):
        if f.lower().endswith('.mp3'):
            tmp += 1
            url = path.join(basepath, f)
            medias.append(url)
    # shuffle it
    random.shuffle(medias)

    # create a vlc medial list from the shuffled list
    for url in medias:
        item = i.media_new(url)
        medialist.add_media(item.get_mrl())

    TestApp().run()