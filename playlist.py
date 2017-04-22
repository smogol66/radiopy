import vlc
from os import  listdir, path
from time import sleep
import random
from urllib2 import unquote


rpi = False

if rpi:
    basepath = '/home/pi/sound/Audio/'
else:
    basepath = '/home/juan/Musique/'
    #  basepath= '/home/Gemeinsame Dateien/Audio/'

if rpi:
    i = vlc.Instance('--aout=alsa', '--alsa-audio-device=dmixer')
else:
    i = vlc.Instance()

medialist = i.media_list_new()
p = i.media_list_player_new()
pl = i.media_player_new()
p.set_media_player(pl)

#create a list of medias
medias = []
medias.append("http://stream.srg-ssr.ch/m/rsj/mp3_128")
medias.append("http://streaming.radio.funradio.fr/fun-1-48-192")
medias.append("http://streaming.radio.rtl2.fr/rtl2-1-44-128")
medias.append("http://stream.srg-ssr.ch/m/couleur3/mp3_128")
tmp = 4
for f in listdir(basepath):
    if f.lower().endswith('.mp3'):
        tmp += 1
        url=path.join(basepath,f)
        medias.append(url)
# shuffle it
random.shuffle(medias)

#create a vlc medial list from the shuffled list
for url in medias:
    item = i.media_new(url)
    medialist.add_media(item.get_mrl())

p.set_media_list(medialist)

# play it
MAXVOL=100
pl.audio_set_volume(MAXVOL)
for playlist in range(tmp):
    p.play()
    sleep(0.5)
    media = medialist[playlist]
    media.parse()
    if media.is_parsed():
        try:
            if not media.get_meta(0) is None:
                print("Title        : {}".format(media.get_meta(0).decode('utf-8')))
            if not media.get_meta(1) is None:
                print("Artist       : {}".format(media.get_meta(1).decode('utf-8')))
        except:
            pass  # do not print nothing
        m, s = divmod(media.get_duration() / 1000, 60)
        h, m = divmod(m, 60)
        print("Song duration: {:02d}:{:02d}:{:02d}".format(h, m, s))

    sleep(10)
    for vol in range(MAXVOL, 0, -10):
        ret=pl.audio_set_volume(vol)
        sleep(0.4)
    p.next()
    ret=pl.audio_set_volume(MAXVOL)

p.stop()

