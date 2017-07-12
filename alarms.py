from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, NumericProperty, StringProperty, BooleanProperty
from datetime import datetime, timedelta, time

from enum import Enum
from copy import copy

data_list = []


class AlarmStates(Enum):
    wait = 1
    alarm = 2
    resumed = 3
    stop = 4
    end = 5


class AlarmTypes(Enum):
    single = 0
    daily = 1


class Alarm:
    """Alarm class to handle all the thing to do with clock alarms"""
    resume_delays = [20, 10, 5]
    alarm_vol_inc = 100.0 / 2.0 / 60  # todo: add this as an option : volume delay (time to full volume)

    def __init__(self, al_type=AlarmTypes.daily, alarm_time='08:00'):
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
        self.set_alarm(al_type, alarm_time)

    def update_alarm(self):
        # update alarm if is was in the past
        my_time = datetime.now()
        al_time = self.timeToWakeUp
        if self.Type == AlarmTypes.daily:
            days=1
            while my_time >= al_time:
                al_time = self.alarmDateTime + timedelta(days=days)
                days += 1

        if self.Type == AlarmTypes.single:
            while my_time >= al_time:
                al_time = al_time + timedelta(days=365)
        self.timeToWakeUp = copy(al_time)
        self.resumed = -1

    def set_alarm(self, al_type=AlarmTypes.daily, alarm_time='8:00'):
        # define the alarm with strings
        self.Type = al_type
        al_time = None
        try:
            my_time = datetime.now()
            if self.Type == AlarmTypes.daily:
                self.alarmDateTime = al_time = datetime.combine(my_time.date(), datetime.strptime(alarm_time, '%H:%M').time())
                self.daysToWakeUp = range(7)
            if self.Type == AlarmTypes.single:
                self.alarmDateTime = datetime.strptime(alarm_time, '%H:%M %d/%m')
            self.update_alarm()

        except (IndexError, TypeError, ValueError):
            raise ValueError('Bad date or time conversion')

    def set_days(self, days):
        self.daysToWakeUp = copy(days)

    def check_to_do(self):
        my_time = datetime.now()
        if self.state == AlarmStates.wait:
            # print('time to go: {}'.format(self.timeToWakeUp-my_time))
            if self.alarmType == AlarmTypes.daily:
                if my_time >= self.timeToWakeUp and my_time.weekday() in self.daysToWakeUp:
                    self.state = AlarmStates.alarm
            if self.alarmType == AlarmTypes.single:
                if my_time >= self.timeToWakeUp:
                    self.state = AlarmStates.alarm

        if self.state == AlarmStates.resumed:
            # print('resume time to go: {}'.format(self.timeToWakeUp - my_time))
            if my_time >= self.timeToWakeUp:
                self.state = AlarmStates.alarm

        if self.state == AlarmStates.stop:
            if self.alarmType == AlarmTypes.single:
                self.state = AlarmStates.end
            if self.alarmType == AlarmTypes.daily:
                self.state = AlarmStates.wait
                self.timeToWakeUp = self.alarmDateTime
                self.update_alarm()

        if self.state == AlarmStates.alarm:
            time_run = my_time - self.timeToWakeUp
            if time_run >= timedelta(minutes=10):
                self.state = AlarmStates.stop

        return self.state

    def resume_alarm(self):
        self.resumed += 1
        self.alarm_actual_volume = 10
        my_time = datetime.now()
        if self.resumed >= len(self.resume_delays):
            r_delay = self.resume_delays[-1]
            self.resumed = len(self.resume_delays) - 1
        else:
            r_delay = self.resume_delays[self.resumed]
        self.timeToWakeUp = my_time + timedelta(seconds=r_delay)
        self.state = AlarmStates.resumed

    def stop_alarm(self):
        if self.state in (AlarmStates.alarm, AlarmStates.resumed):
            self.alarm_actual_volume = 10
            self.state = AlarmStates.stop
            self.resumed = -1

    def update_daily_alarm(self, hour, minute, days):
        my_time = datetime.now()
        self.alarmDateTime = self.alarmDateTime.combine(my_time.date(), time(hour=int(hour), minute=int(minute)))
        if my_time >= self.alarmDateTime:
            # if alarm in the past, set it in the future
            self.alarmDateTime += timedelta(days=1)
        days_enum = []
        for day_num, day in enumerate(days):
            if day:
                days_enum.append(day_num)
        del self.daysToWakeUp[:]
        self.daysToWakeUp = copy(days_enum)
        self.timeToWakeUp = self.alarmDateTime
        self.alarmType = AlarmTypes.daily

    def update_single_alarm(self, hour, minute, day, month):
        mytime = datetime.now()
        self.alarmDateTime = datetime(month=int(month), day=int(day), year=mytime.year,
                                      hour=int(hour), minute=int(minute))
        if self.alarmDateTime <= mytime:
            self.alarmDateTime = datetime(month=int(month), day=int(day), year=mytime.year + 1, hour=int(hour),
                                          minute=int(minute))
        self.timeToWakeUp = self.alarmDateTime
        self.alarmType = AlarmTypes.single

    def skip_days(self,days):
        if self.alarmType== AlarmTypes.daily:
            if 0 < days < 7:
                next_alarm = self.timeToWakeUp + timedelta(days=days)
            elif days == 0:
                next_alarm = self.alarmDateTime
            else:
                next_alarm = self.alarmDateTime + timedelta(days=1000)
            self.timeToWakeUp = copy(next_alarm)
            # self.alarmDateTime = copy(next_alarm)
            self.update_alarm()

    def getNextSkipped(self):
        if self.alarmType == AlarmTypes.daily:
            self.update_alarm()
            delay = self.timeToWakeUp - datetime.now()
            if delay.days > 7:
                # extend the alarm
                self.timeToWakeUp +=  timedelta(days=1000)
            return delay.days if delay.days < 7 else -1
        else:
            return  0


class SelectableRecycleBoxLayout(LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    # Adds selection and focus behaviour to the view.
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
        # Catch and handle the view changes
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        # Add selection on touch down
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        # Respond to the selection of items in the view.
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))


class RVSAlarmScreen(Screen):

    def populate(self, database):

        if type(database) is list:
            if not database:
                return
            if isinstance(database[0], Alarm):
                # populathe the data with the values dictionaryy of alarm list
                del data_list[:]
                for alarm in database:
                    print (alarm.alarmType, alarm.alarmDateTime)
                    if alarm.alarmType == AlarmTypes.daily:
                        skip = alarm.getNextSkipped()
                        data_list.append({'value': datetime.strftime(alarm.alarmDateTime, '%H:%M'),
                                          'type': 'daily' if alarm.alarmType == AlarmTypes.daily else 'once',
                                          'skip_next': 'enabled' if skip == 0 else 'skip {}'.format(skip)
                                            if skip > 0 else 'paused'}, )
                    else:
                        data_list.append({'value': datetime.strftime(alarm.alarmDateTime, '%H:%M'),
                                          'type': 'daily' if alarm.alarmType == AlarmTypes.daily else 'once',
                                          'skip_next': ''} )
                self.rv.data = data_list

    def update(self, alarm, index):
        if self.rv.data:
            self.rv.data[index]['value'] = alarm.alarmDateTime.strftime('%H:%M') or 'default new value'
            self.rv.data[index]['type'] = 'daily' if alarm.alarmType == AlarmTypes.daily else 'single'
            if alarm.alarmType == AlarmTypes.daily:
                skip = alarm.getNextSkipped()
                self.rv.data[index]['skip_next'] = 'enabled' if skip == 0 else 'skip ' + str(skip) \
                    if skip > 0 else 'paused'
                self.rv.data[index]['status'] = True
            else:
                self.rv.data[index]['skip_next'] = ''
                self.rv.data[index]['status'] = False
            self.rv.refresh_from_data()

    def remove(self, index):
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
    Days = ListProperty([True, False, True, False, False, False, False])
    media = StringProperty('')


class AlarmRunScreen(Screen):
    index = NumericProperty(-1)
    alarmText = StringProperty('Alarm')
    mediaText = StringProperty('')


class DisableAlarmPopup(Popup):
    next_alarms = StringProperty('all')
    index = NumericProperty(-1)
