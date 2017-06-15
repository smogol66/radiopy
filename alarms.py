from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.properties import ListProperty, NumericProperty, StringProperty
from datetime import time, date


class Alarm:
    Type = None
    StoredTime = None
    timeToWait = 0

    def __init__(self, type='weekly', alarm_time='08:00', alarm_date=''):
        self.Type = type
        if type == 'weekly':
            a = alarm_time.split(':')
            self.StoredTime = time(hour = a[0], min= a[1])
        elif type == 'one':
            a = alarm_time.split(':') + alarm_date.split("/")
            self.StoredTime = date(hour=a[0], min=a[1], day=a[2], month=a[3], year=a[4])


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


class RVSScreen(Screen):
    def populate(self,database):
        self.rv.data = database

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

