from kivy.uix.listview import ListItemButton
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, SmoothLine
from kivy.uix.floatlayout import FloatLayout
from math import cos, sin, pi
from kivy.clock import Clock
from kivy.lang import Builder
import vlc
from os import path, walk, system
import datetime
from kivy.config import Config
from extendedsettings import ExtendedSettings
from settingsjson import settings_json


try:
    import RPi.GPIO
    rpi = True
except ImportError:
    rpi = False

media_list = None


def load_media(folder, scan_folders=False):

    def recursive_walk(start_folder, with_sub_folders):
        for folderName, sub_folders, file_names in walk(start_folder.encode('utf8')):
            if folderName != start_folder and not with_sub_folders:
                return
            else:
                print('\nFolder: ' + folderName + '\n')
            for filename in file_names:
                if filename.lower().split('.')[-1] in ('mp3','ogg'):
                    media = Instance.media_new(path.join(folderName, filename))
                    media_list.add_media(media)
            if sub_folders:
                for sub_folder in sub_folders:
                    recursive_walk(sub_folder, with_sub_folders)

    global media_list
    if media_list:
        media_list.release()
        media_list = Instance.media_list_new()
    else:
        media_list = Instance.media_list_new()

    media_list.add_media(Instance.media_new('http://stream.srg-ssr.ch/m/rsj/mp3_128'))
    media_list.add_media(Instance.media_new('http://stream.srg-ssr.ch/m/rsj/mp3_128'))
    media_list.add_media(Instance.media_new('http://streaming.radio.funradio.fr/fun-1-48-192'))
    media_list.add_media(Instance.media_new('http://streaming.radio.rtl2.fr/rtl2-1-44-128'))
    media_list.add_media(Instance.media_new('http://stream.srg-ssr.ch/m/couleur3/mp3_128'))

    recursive_walk(folder, scan_folders)

    list_player.set_media_list(media_list)


class MyClockWidget(FloatLayout):
    def do_press(self):
        self.ids.label.text = 'pressed'

    def do_release(self):
        self.ids.label.text = ''


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
            hour_radius = 0.7
            th = time.hour * 60 + time.minute
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+hour_radius*self.r*sin(pi/360*th),
                       self.center_y+hour_radius*self.r*cos(pi/360*th)], width=5, cap="round",
                       overdraw_width=1.6)
            Color(0.35, .35, 0.35)
            min_radius = 1
            tm = time.minute + time.second / 60.0
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+min_radius*self.r*sin(pi/30*tm),
                       self.center_y+min_radius*self.r*cos(pi/30*tm)], width=4, cap="round",
                       overdraw_width=1.6)
            Color(0.8, 0.2, 0.2)
            sec_radius = 1.06
            ts = time.second+time.microsecond / 1000000.0
            SmoothLine(points=[self.center_x, self.center_y, self.center_x+sec_radius*self.r*sin(pi/30*ts),
                       self.center_y+sec_radius*self.r*cos(pi/30*ts)], width=2, cap="round",
                       overdraw_width=1.6)


class ClockScreen(Screen):
    def do_press(self):
        self.ids.label.text = 'pressed'

    def do_release(self):
        self.ids.label.text = ''


class MenuButton(ListItemButton):
    index = NumericProperty(0)


class MenuPageScreen(Screen):

    def plays(self, index):
        pass

    def args_converter(self, row_index, title):
        title.parse()
        if title.is_parsed():
            song_title = ''
            song_artist = ''
            try:
                if not title.get_meta(0) is None:
                    song_title = title.get_meta(0).decode('utf-8')

                if not title.get_meta(1) is None:
                    song_artist = title.get_meta(1).decode('utf-8')
            except ValueError:
                pass  # do not print nothing

            text = "{} by {}".format(song_title, song_artist) if song_artist != '' else song_title
            text = title.get_mrl().replace('%20',' ').split('/')[-1] if text == '' else text
        return {
            'index': row_index,
            'text': text
        }


class PlayerScreen(Screen):
    labelImage = StringProperty('img/pause.png')
    index = NumericProperty(0)
    songTitle = StringProperty(' ')
    songArtist = StringProperty(' ')
    playVolume = NumericProperty(100)
    time_elapsed = StringProperty('00:00')
    song_progress = NumericProperty(0)
    last_index = 0
    duration = 0
    schedule = None
    SCHEDULE_DELAY = 0.5
    media = None

    def on_pre_enter(self):
        self.index = int(self.index)

        if list_player.is_playing():
            if self.last_index != self.index:
                list_player.stop()
            else:
                return  # continue to play the same song
        list_player.play_item_at_index(self.index)
        list_player.play()

        self.last_index = self.index
        self.labelImage = 'img/pause.png'
        if self.schedule is None:
            self.schedule = Clock.schedule_interval(self.update_time, self.SCHEDULE_DELAY)

    def plays(self):
        if player.is_playing():
            player.pause()
            self.labelImage = 'img/play.png'
            Clock.unschedule(self.schedule)
            self.schedule = None
        else:
            player.play()
            self.labelImage = 'img/pause.png'
            self.schedule = Clock.schedule_interval(self.update_time, self.SCHEDULE_DELAY)

    def prev_song(self):
        self.index -= 1
        if self.index < 0:
            self.index = media_list.count()-1
        self.last_index = -1
        self.song_progress = 0
        self.on_pre_enter()

    def next_song(self):
        self.index += 1
        if self.index > media_list.count()-1:
            self.index = 0
        self.last_index = -1
        self.song_progress = 0
        self.on_pre_enter()

    def set_volume(self, volume):
        player.audio_set_volume(int(volume))
        self.playVolume = volume
        # App.config.set('Base','startupvolume',int(volume))

    def update_time(self, *args):
        if self.media is None:
            self.media = player.get_media()
            self.media.parse()

        if self.media.is_parsed():
            try:
                self.songTitle = ''
                if not self.media.get_meta(0) is None:
                    self.songTitle = self.media.get_meta(0).decode('utf-8')
                self.songArtist = ''
                if not self.media.get_meta(1) is None:
                    self.songArtist = self.media.get_meta(1).decode('utf-8')
            except ValueError:
                pass  # do not print nothing

            self.duration = self.media.get_duration()
            self.media = None

        if self.duration != 0:
            diff = self.duration - player.get_time()
            progress = player.get_time() / float(self.duration) * 100.0
        else:
            diff = player.get_time()
            progress = 0

        # check a difference in the song position
        if abs(self.song_progress - self.ids.song_pos.value) > 5:
            # the cursor has been changed by the user, correct song position
            millis = self.duration * self.ids.song_pos.value / 100
            player.set_time(int(millis))
            self.song_progress = self.ids.song_pos.value
        else:
            self.song_progress = progress

        m, s = divmod(diff / 1000, 60)
        h, m = divmod(m, 60)
        if h == 0:
            self.time_elapsed = "{:02d}:{:02d}".format(m, s)
        else:
            self.time_elapsed = "{:02d}:{:02d}:{:02d}".format(h, m, s)
        if not list_player.is_playing():
            self.next_song()


class RadioPyApp(App):
    data = ListProperty()
    playScreen = None
    menuScreen = None
    clockScreen = None
    last_index = -1

    def build(self):

        self.settings_cls = ExtendedSettings
        media_path = self.config.get('Base', 'mediapath')
        sub = self.config.get('Base', 'boolsub_folders') == u'1'
        load_media(media_path,sub)
        sm = ScreenManager(transition=SwapTransition(direction='right'))
        self.clockScreen = ClockScreen(name='clock')
        sm.add_widget(self.clockScreen)
        self.menuScreen = MenuPageScreen(name='menu')
        sm.add_widget(self.menuScreen)
        self.data = media_list
        self.playScreen = PlayerScreen(name='play')
        self.playScreen.index = 0
        self.playScreen.playVolume = self.config.get('Base','startupvolume')
        sm.add_widget(self.playScreen)

        Clock.schedule_interval(self.clockScreen.ticks.update_clock, 0.25)
        # sm.current = 'clock'
        return sm

    def build_config(self, config):
        config.setdefaults('Base', {
            'startupvolume': 100,
            'baselamp': 'off',
            'mediapath': base_path,
            'runcolor': '#ffffffff',
            'boolsub_folders': 'False',
            'reboot':'False'
        })

    def build_settings(self, settings):
        settings.add_json_panel('Radio Py',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        if key=='mediapath' or key=='boolsub_folders':
            sub = self.config.get(section,'boolsub_folders')
            folder = self.config.get(section,'mediapath')
            load_media(folder, sub)
            self.data = media_list
        if key=='reboot':
            self.config.set(section,'reboot','False')
            self.config.write()
            if rpi:
                system('sudo reboot')
            else:
                App.get_running_app().stop()

    def on_menu_selection(self, index):
        if index != self.last_index:
            self.last_index = index

        self.playScreen.index = index
        self.root.current = 'play'
        self.menuScreen.plays(index)

    def stop_and_return(self):
        self.root.current = 'menu'

    def show_clock(self):
        self.root.current = 'clock'

    def show_player(self):
        self.root.current = 'play'

    def show_alarms(self):
        pass

if rpi:
    Instance = vlc.Instance('--aout=alsa', '--alsa-audio-device=dmixer')
else:
    Instance = vlc.Instance()

if rpi:
    base_path = '/home/pi/sound/Audio/'
else:
    base_path = '/home/Gemeinsame Dateien/Audio'

player = Instance.media_player_new()
list_player = Instance.media_list_player_new()
list_player.set_media_player(player)

if not rpi:
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')

Builder.load_file('radioPyvy.kv')

if __name__ == '__main__':
    RadioPyApp().run()
