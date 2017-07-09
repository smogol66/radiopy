from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import ListProperty, NumericProperty, StringProperty
from datetime import datetime, timedelta, time
from enum import Enum
from copy import copy


class AlarmStates(Enum):
    wait=1
    alarm=2
    resumed=3
    stop=4
    end=5


class AlarmTypes(Enum):
    single=0
    daily=1


class Alarm:
    """Alarm class to handle all the thing to do with clock alarms"""
    resume_delays = [20, 10, 5]
    alarm_vol_inc = 100.0 / 2.0 / 60  # todo: add this as an option : volume delay (time to full volume)

    def __init__(self,atype=AlarmTypes.daily, alarm_time='08:00'):
        self.skipNext = 0
        self.type = None
        self.state = AlarmStates.wait
        self.alarmType = AlarmTypes.daily
        self.alarmDateTime = datetime.now()
        self.timeToWakeUp = datetime.now()
        self.daysToWakeUp = []
        self.resumed = -1
        self.alarm_actual_volume = 10
        self.media = 0
        self.Type = AlarmTypes.daily
        self.set_alarm(atype, alarm_time)

    def set_alarm(self, atype=AlarmTypes.daily,alarm_time='8:00'):
        # define the alarm with strings
        self.Type = atype
        altime=None
        try:
            if atype == AlarmTypes.daily:
                mytime = datetime.now()
                altime = datetime.combine(mytime.date(),datetime.strptime(alarm_time, '%H:%M').time())
                if mytime >= altime:
                    # if alarm in the past, set it in the future
                    altime = altime + timedelta(days=1)
                self.daysToWakeUp=range(7)
            if atype == AlarmTypes.single:
                altime = datetime.strptime(alarm_time, '%H:%M %d/%m')
                if altime >= altime:
                    altime = altime + timedelta(year=1)
            self.alarmDateTime = self.timeToWakeUp = altime
        except (IndexError, TypeError, ValueError):
            raise ValueError('Bad date or time conversion')

    def set_days(self, days=[]):
        self.daysToWakeUp = copy(days)

    def check_to_do(self):
        mytime = datetime.now()
        if self.skipNext == -1:
            # alarm is disabled
            self.state = AlarmStates.wait

        if self.state == AlarmStates.wait:
            # print('time to go: {}'.format(self.timeToWakeUp-mytime))
            if self.alarmType == AlarmTypes.daily:
                if mytime >= self.timeToWakeUp and mytime.weekday() in self.daysToWakeUp:
                    if self.skipNext == 0:
                        self.state= AlarmStates.alarm
                    else:
                        self.skipNext -= 1
                        self.state = AlarmStates.stop
            if self.alarmType == AlarmTypes.single:
                if mytime >= self.timeToWakeUp:
                    self.state = AlarmStates.alarm

        if self.state == AlarmStates.resumed:
            # print('resume time to go: {}'.format(self.timeToWakeUp - mytime))
            if mytime >= self.timeToWakeUp:
                self.state = AlarmStates.alarm

        if self.state == AlarmStates.stop:
            if self.alarmType == AlarmTypes.single:
                self.state = AlarmStates.end
            if self.alarmType == AlarmTypes.daily:
                self.timeToWakeUp = datetime.combine(mytime.date(), self.alarmDateTime.time()) + timedelta(days=1)
                self.state = AlarmStates.wait

        if self.state == AlarmStates.alarm:
            time_run = mytime - self.timeToWakeUp
            if time_run >= timedelta(minutes=10):
                self.state = AlarmStates.stop

        return self.state

    def resume_alarm(self):
        self.resumed += 1
        mytime = datetime.now()
        rdelay = 0
        if self.resumed >= len(self.resume_delays):
            rdelay = self.resume_delays[ - 1]
            self.resumed= len(self.resume_delays) - 1
        else:
            rdelay = self.resume_delays[self.resumed]
        self.timeToWakeUp = mytime + timedelta( seconds= rdelay)
        self.state = AlarmStates.resumed

    def stop_alarm(self):
        self.alarm_actual_volume = 10
        self.state = AlarmStates.stop
        self.resumed = -1

    def update_daily_alarm(self, hour, minute, days):
        mytime = datetime.now()
        self.alarmDateTime=self.alarmDateTime.combine(mytime.date(), time(hour=int(hour), minute=int(minute)))
        if mytime >= self.alarmDateTime:
            # if alarm in the past, set it in the future
            self.alarmDateTime += timedelta(days=1)
        daysenum = []
        for daynum,day in enumerate(days):
            if day==True:
                daysenum.append(daynum)
        del self.daysToWakeUp[:]
        self.daysToWakeUp = copy(daysenum)
        self.timeToWakeUp = self.alarmDateTime
        self.alarmType = AlarmTypes.daily

    def update_single_alarm(self, hour, minute, day, month):
        mytime = datetime.now()
        self.alarmDateTime = datetime(month=int(month), day=int(day), year=mytime.year,
                                      hour=int(hour), minute=int(minute))
        if self.alarmDateTime <= mytime:
            self.alarmDateTime = datetime(month=int(month), day=int(day), year=mytime.year + 1,
                                      hour=int(hour), minute=int(minute))
        self.timeToWakeUp = self.alarmDateTime
        self.alarmType = AlarmTypes.single


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    pass


class SelectableLabel(RecycleDataViewBehavior, BoxLayout):
    value = StringProperty('')
    type = StringProperty('')
    skip_next = StringProperty('')
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

data_list = []

class RVSAlarmScreen(Screen):

    def populate(self,database):

        if type(database) is list:
            if not database:
                return
            if isinstance(database[0], Alarm):
                # populathe the data with the values dictionaryy of alarm list
                del data_list [:]
                for alarm in database:
                    print (alarm.alarmType, alarm.alarmDateTime)
                    data_list.append({'value':datetime.strftime(alarm.alarmDateTime,'%H:%M'),\
                                      'type':'daily' if alarm.alarmType==AlarmTypes.daily else 'once',
                                      'skip_next':'enabled' if alarm.skipNext == 0 else 'skip ' + str(alarm.skipNext) \
                                                        if alarm.skipNext>0 else 'paused'},)
                self.rv.data=data_list

    def update(self, alarm, index):
        if self.rv.data:
            self.rv.data[index]['value'] = alarm.alarmDateTime.strftime('%H:%M') or 'default new value'
            self.rv.data[index]['type'] = 'daily' if alarm.alarmType==AlarmTypes.daily else 'single'
            self.rv.data[index]['skip_next'] = 'enabled' if alarm.skipNext == 0 else 'skip ' + str(alarm.skipNext) \
                                                        if alarm.skipNext>0 else 'paused'
            self.rv.refresh_from_data()

    def remove(self,index):
        del self.rv.data[index]
        self.rv.refresh_from_data()


class AlarmScreen(Screen):
    AlarmText = StringProperty('Alarm')
    AlarmType = StringProperty('')
    index = NumericProperty(0)
    Minute = StringProperty('00')
    Hour = StringProperty('08')
    Month = StringProperty('01')
    Day = StringProperty('01')
    Days = ListProperty([True, False, True,False,False,False,False])
    media = StringProperty('')


class AlarmRunScreen(Screen):
    index = NumericProperty(-1)
    alarmText = StringProperty('Alarm')
    mediaText = StringProperty('')


class DisableAlarmPopup(Popup):
    next_alarms = StringProperty('all')
    index = NumericProperty(-1)
