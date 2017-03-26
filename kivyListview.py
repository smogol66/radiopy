from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.listview import ListItemButton
from kivy.properties import ListProperty, NumericProperty

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

        BoxLayout:
            size_hint:(.1, None)
            Button:
                text: 'atlas'


<Page>:
    BoxLayout:
        BoxLayout:
            size_hint:(.1, None)
            Button:
                text: 'MENU'
                on_press: root.manager.current = 'menu'
        BoxLayout:
            orientation:'vertical'
            Button:
                id: 'titleButton'
                text:'Title'
                size_hint:(1, .2)
            Image:
                source: '/home/juan/Images/Capture du 2015-12-30 11:23:20.png'
                size_hint:(1, .8)
        BoxLayout:
            size_hint:(.1, None)

            Button:
                text: 'atlas'
''')

class MenuButton(ListItemButton):
    index = NumericProperty(0)

class MenuPage(Screen):
    M = SoundLoader.load('/usr/share/sounds/ubuntu/stereo/bell.ogg')

    def plays(self):
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

class Page(Screen):
    pass

class TestApp(App):
    data = ListProperty(["Item #{0}".format(i) for i in range(50)])

    def build(self):
        sm = ScreenManager()
        self.menu = MenuPage(name='menu')
        sm.add_widget(self.menu)
        for i in range(50):
            name = Page(name=str(i))
            sm.add_widget(name)
        return sm

    def on_menu_selection(self, index):
        self.root.current = str(index)
        self.menu.plays()

if __name__ == '__main__':
    TestApp().run()