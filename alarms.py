from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import ListProperty, NumericProperty, StringProperty
from datetime import datetime, timedelta, time
from enum import Enum
from copy import copy

AlarmStates = Enum('AlarmsStates','wait alarm resumed stop end')
AlarmTypes  = Enum('AlarmTypes', 'single daily')


class Alarm:
    """Alarm class to handle all the thing to do with clock alarms"""
    skipNext = 0
    type = None
    state = AlarmStates.wait
    alarmType = AlarmTypes.daily
    alarmDateTime = datetime.now()
    timeToWakeUp = datetime.now()
    daysToWakeUp = []
    resumed = -1
    # resumeDelay= [20,10,5]
    resumeDelay = [1, 1, 1]
    media = None

    def __init__(self, atype=AlarmTypes.daily,alarm_time='8:00'):
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
        if self.state == AlarmStates.wait:
            if self.alarmType == AlarmTypes.daily:
                if mytime >= self.timeToWakeUp and mytime.weekday() in self.daysToWakeUp:
                    if self.skipNext == 0:
                        self.state= AlarmStates.alarm
                    else:
                        self.skipNext -= 1
                        self.state = AlarmStates.stop
            if AlarmTypes == AlarmTypes.single:
                if mytime >= self.timeToWakeUp:
                    self.state = AlarmStates.alarm

        if self.state == AlarmStates.resumed and mytime >= self.timeToWakeUp:
            self.state = AlarmStates.alarm

        if self.state == AlarmStates.stop:
            if AlarmTypes.single:
                self.state = AlarmTypes.end
            if AlarmTypes.daily:
                self.timeToWakeUp = self.alarmDateTime.time()
                self.state = AlarmStates.wait

        return self.state

    def resume_alarm(self):
        self.resumed += 1
        mytime = datetime.now()
        rdelay = 0
        if self.resumed > len(self.resumeDelay):
            rdelay = timedelta( minutes=self.resumeDelay[-1])
        else:
            rdelay = timedelta(minutes=self.resumeDelay[self.resumed])
        self.timeToWakeUp = mytime + rdelay
        self.state = AlarmStates.resumed

    def stop_alarm(self):
        self.state = AlarmStates.stop

    def update_daily_alarm(self, hour, minute, days):
        mytime = datetime.now()
        altime = datetime.combine(mytime.date(), time(hour=int(hour), minute=int(minute)))
        if mytime >= altime:
            # if alarm in the past, set it in the future
            altime = altime + timedelta(days=1)
        daysenum = []
        for daynum,day in enumerate(days):
            if day==True:
                daysenum.append(daynum)
        self.daysToWakeUp = copy(daysenum)
        self.timeToWakeUp = altime

    def update_single_alarm(self, hour, minute, day, month):
        mytime = datetime.now()
        altime = datetime.combine(mytime.date, datetime(month=int(month), day=int(day), hour=int(hour),
                                                        minute=int(minute)))
        if altime >= mytime:
            altime = altime + timedelta(year=1)
        self.timeToWakeUp = altime




class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    pass


class SelectableLabel(RecycleDataViewBehavior, BoxLayout):
    value = StringProperty('')
    more = StringProperty('')
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
            if isinstance(database[0],Alarm):
                # populathe the data with the values dictionaryy of alarm list
                del data_list [:]
                for alarm in database:
                    print (alarm.alarmType, alarm.alarmDateTime)
                    data_list.append({'value':datetime.strftime(alarm.alarmDateTime,'%H:%M'),\
                                      'more':'daily' if alarm.alarmType==AlarmTypes.daily else 'once'})
                self.rv.data=data_list


    def update(self, value,more, index):
        if self.rv.data:
            self.rv.data[index]['value'] = value or 'default new value'
            self.rv.data[index]['more'] = more or 'daily'
            self.rv.refresh_from_data()


class AlarmScreen(Screen):
    AlarmText = StringProperty('Alarm')
    AlarmType = StringProperty('')
    index = NumericProperty(0)
    Minute = StringProperty('00')
    Hour = StringProperty('08')
    Month = StringProperty('08')
    Day = StringProperty('01')
    Days = ListProperty([True, False, True,False,False,False,False])
    media = StringProperty('')

