from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
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
import alarms



try:
    import RPi.GPIO
    rpi = True
except ImportError:
    rpi = False

media_list = None
song_list = []


def load_media(folder, scan_folders=False):

    global media_list

    def recursive_walk(start_folder, with_sub_folders):
        try:
            for folderName, sub_folders, file_names in walk(start_folder.encode('utf8')):
                if folderName != start_folder and not with_sub_folders:
                    return
                else:
                    #print('\nFolder: ' + folderName + '\n')
                    pass
                for filename in file_names:
                    if filename.lower().split('.')[-1] in ('mp3','ogg'):
                        media_path = path.join(folderName, filename)
                        media = Instance.media_new(path.join(folderName, filename))
                        media_list.add_media(media)
                        song_list.append({'media_file': media_path, 'type': 'local'})

                if sub_folders:
                    for sub_folder in sub_folders:
                        recursive_walk(sub_folder, with_sub_folders)
        except UnicodeDecodeError:
            pass

    def add_radio(radio_url):
        media = Instance.media_new(radio_url)
        media_list.add_media(media)
        song_list.append({'media_file': radio_url, 'type': 'radio'})

    if media_list:
        media_list.release()
        media_list = Instance.media_list_new()
        del song_list[:]
    else:
        media_list = Instance.media_list_new()
        del song_list[:]

    add_radio('http://stream.srg-ssr.ch/m/rsj/mp3_128')
    add_radio('http://streaming.radio.funradio.fr/fun-1-48-192')
    add_radio('http://streaming.radio.rtl2.fr/rtl2-1-44-128')
    add_radio('http://stream.srg-ssr.ch/m/couleur3/mp3_128')

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

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    print ('selected')


class MediaSelectable(RecycleDataViewBehavior, BoxLayout):
    song_title = StringProperty('')
    artist = StringProperty('')
    type = StringProperty('')
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(MediaSelectable, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(MediaSelectable, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        title = media_list[index]
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

            self.song_title = song_title
            self.artist = song_artist

        if is_selected:
           pass

        else:
            pass

    def select(self, index):
        self.selected = True
        self.parent.select_with_touch(self.index)

class AlarmMediaSelectable(RecycleDataViewBehavior, BoxLayout):
    song_title = StringProperty('')
    artist = StringProperty('')
    type = StringProperty('')
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(AlarmMediaSelectable, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(AlarmMediaSelectable, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        title = media_list[index]
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

            self.song_title = song_title
            self.artist = song_artist

        if is_selected:
           pass

        else:
            pass

    def select(self, index):
        self.selected = True
        self.parent.select_with_touch(self.index)


class RVSongScreen(Screen):
    def populate(self):
        self.rv.data = song_list

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

class BlankScreen(Screen):
    pass

class SongPopup(Popup):
    def populate(self):
        self.rv.data = song_list

alarms_data = [alarms.Alarm(),alarms.Alarm(atype=alarms.AlarmTypes.daily,alarm_time='10:00')]

class RadioPyApp(App):
    songsData = ListProperty()
    playScr = None
    menuScreen = None
    clockScr = None
    rvsSongsScr = None
    rvsAlarmsScr = None
    blankScr = None
    last_index = -1
    RVS = None
    alarmScr = None
    AlarmSchedule = None
    BlankSchedule = None
    lastScreen = ''

    def build(self):
        # update settings
        self.settings_cls = ExtendedSettings
        media_path = self.config.get('Base', 'mediapath')
        sub = self.config.get('Base', 'boolsub_folders') == u'1'
        load_media(media_path,sub)
        val = self.config.get('Base', 'brightness')
        if rpi:
            system('sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))
        else:
            print('call to: sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))

        # generate GUI
        sm = ScreenManager(transition=SwapTransition(direction='right'))

        self.clockScr = ClockScreen(name='clock')
        sm.add_widget(self.clockScr)

        self.rvsSongsScr = RVSongScreen(name='play_list')
        self.rvsSongsScr.populate()
        sm.add_widget(self.rvsSongsScr)

        self.songsData = media_list
        self.playScr = PlayerScreen(name='play')
        self.playScr.index = 0
        self.playScr.playVolume = self.config.get('Base', 'startupvolume')
        sm.add_widget(self.playScr)

        self.rvsAlarmsScr = alarms.RVSAlarmScreen(name='alarm_list')
        self.rvsAlarmsScr.populate(alarms_data)
        sm.add_widget(self.rvsAlarmsScr)

        self.alarmScr = alarms.AlarmScreen(name='alarm')
        sm.add_widget(self.alarmScr)

        self.blankScr = BlankScreen(name='blank')
        sm.add_widget(self.blankScr)

        sm.current = 'clock'

        # setup schedulers
        Clock.schedule_interval(self.clockScr.ticks.update_clock, 0.25)
        self.AlarmSchedule = Clock.schedule_interval(self.check_alarms, 1)

        sm.bind(on_press=self.reset_blank)
        self.reset_blank()
        return sm

    def blank_screen(self,*args):
        self.lastScreen = self.root.current
        self.root.current = 'blank'
        if rpi:
            system('sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(0))
        else:
            print('call to: sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(0))
        print 'blank rst'

    def wake_up(self):
        self.reset_blank()
        self.root.current = self.lastScreen
        val = self.config.get('Base', 'brightness')
        if rpi:
            system('sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))
        else:
            print('call to: sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))

    def reset_blank(self):
        if self.BlankSchedule:
            self.BlankSchedule.cancel()
        self.BlankSchedule = Clock.schedule_once(self.blank_screen, 20)

    def check_alarms(self,*args):
        for index, alarm in enumerate(alarms_data):
            print('alarm {} : {}'.format(index, alarm.check_to_do()))


    def build_config(self, config):
        config.setdefaults('Base', {
            'startupvolume': 100,
            'baselamp': 'off',
            'mediapath': base_path,
            'brightness': 255,
            'runcolor': '#ffffffff',
            'boolsub_folders': 'False',
            'shutdown':'False',
            'reboot':'False',
        })

    def build_settings(self, settings):
        settings.add_json_panel('Radio Py',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        print('entering config key:{}'.format(key))
        if key=='mediapath' or key=='boolsub_folders':
            sub = self.config.get(section,'boolsub_folders')
            folder = self.config.get(section,'mediapath')
            load_media(folder, sub)
            self.songsData = media_list
        if key=='reboot':
            self.config.set(section,key,'False')
            self.config.write()
            if rpi:
                system('sudo reboot')
            else:
                App.get_running_app().stop()
        if key=='shutdown':
            self.config.set(section,key,'False')
            self.config.write()
            if rpi:
                system('sudo shutdown')
                App.get_running_app().stop()
            else:
                App.get_running_app().stop()
        if key=='brightness':
            val = int(self.config.get(section,'brightness'))
            print('value is {}'.format(val))
            if val < 7:
                self.config.set(section, key, 7)
                self.config.write()
                val = 7
            if val > 255:
                self.config.set(section, key, 255)
                self.config.write()
                val = 255

            self.config.write()
            if rpi:
                system('sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))
            else:
                print('call to: sudo bash -c "echo {} > /sys/class/backlight/rpi_backlight/brightness"'.format(val))
            config.read("radiopy.ini")

    def on_menu_selection(self, index):
        if index != self.last_index:
            self.last_index = index

        self.playScr.index = index
        self.root.current = 'play'

    def stop_and_return(self):
        sub = self.config.get('Base', 'boolsub_folders')
        folder = self.config.get('Base', 'mediapath')
        try:
            load_media(folder, sub)
        except UnicodeDecodeError:
            pass
        self.root.current = 'play_list'

    def show_clock(self):
        self.root.current = 'clock'

    def show_player(self):
        self.root.current = 'play'

    def show_alarms(self):
        self.root.current = 'alarm_list'

    def alarm_edit(self,index, more):
        self.alarmScr.index = index
        self.alarmScr.AlarmType = more
        if more=='daily':
            self.alarmScr.ids.daily.state= 'down'
        else:
            self.alarmScr.ids.single.state = 'down'
        self.root.current='alarm'
        print('edit alarm at {} as {}'.format(index, more))

    def alarm_active(self,index, value):
        if value:
            print('alarm {} activated'.format(index))
        else:
            print('alarm {} disabled'.format(index))

    def add_alarm(self):
        print('had to add alarm')

    def set_alarm(self,index):
        print('AlarmType: {} at index {}'.format(self.alarmScr.AlarmType, index))

        if self.alarmScr.AlarmType == 'daily':
            alarms_data[index].update_daily_alarm(self.alarmScr.Hour,
                                            self.alarmScr.Minute,
                                            self.alarmScr.Days)
        elif self.alarmScr.AlarmType == 'single':
            alarms_data[index].update_single_alarm(self.alarmScr.Hour,
                                            self.alarmScr.Minute,
                                            self.alarmScr.Day,
                                            self.alarmScr.Month)


        days = self.alarmScr.Days
        print(days)
        self.root.current = 'alarm_list'

    def choose_alarm_media(self,index):
        popup = SongPopup()
        popup.populate()
        print('Alarm index: {}'.format(index))
        popup.open()

    def on_alarm_media_selection(self,index):

        print('Alarm sond index: {}'.format(index))

    def cancel(self):
        self.root.current = 'alarm_list'
        self.reset_blank()


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
Builder.load_file('alarms.kv')

if __name__ == '__main__':
    RadioPyApp().run()
