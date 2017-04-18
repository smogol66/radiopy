from kivy.app import App
from kivy.core.audio import SoundLoader

class StreamApp(App):
    def build(self):
        sound = SoundLoader.load('http://stream.srg-ssr.ch/m/rsj/mp3_128')
        if sound:
            print("Sound found at %s" % sound.source)
        print("Sound is %.3f seconds" % sound.length)
        sound.play()

if __name__ == '__main__':
    StreamApp().run()