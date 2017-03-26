import requests
import vlc
from time import sleep

urls = [
    'http://stream.srg-ssr.ch/m/rsj/mp3_128',
    'http://streaming.radio.funradio.fr/fun-1-48-192',
    'http://streaming.radio.rtl2.fr/rtl2-1-44-128',
    'http://stream.srg-ssr.ch/m/couleur3/mp3_128'
    ]

playlists = set(['pls','m3u'])

Instance = vlc.Instance()


for url in urls:
    ext = (url.rpartition(".")[2])[:3]
    test_pass = False
    try:
        if url[:4] == 'file':
            test_pass = True
        else:
            r = requests.get(url, stream=True)
            test_pass = r.ok
    except Exception as e:
        print('failed to get stream: {e}'.format(e=e))
        test_pass = False
    else:
        if test_pass:
            print('Sampling for 15 seconds')
            player = Instance.media_player_new()
            Media = Instance.media_new(url)
            Media_list = Instance.media_list_new([url])
            Media.get_mrl()
            player.set_media(Media)
            if ext in playlists:
                list_player = Instance.media_list_player_new()
                list_player.set_media_list(Media_list)
                if list_player.play() == -1:
                    print ("Error playing playlist")
            else:
                if player.play() == -1:
                    print ("Error playing Stream")

            for vol in range(0,100,10):
                player.audio_set_volume(vol)
                print(vlc.libvlc_audio_get_volume(player))
                sleep(0.2)
            player.audio_set_volume(100)
            sleep(15)

            if ext in playlists:
                list_player.stop()

            else:
                # player.stop()
                volume_player = player
                print('fading volume')
                for vol in range(100, 0, -10):
                    player.audio_set_volume(vol)
                    print(vlc.libvlc_audio_get_volume(player))
                    sleep(0.2)
                player.stop()


        else:
            print('error getting the audio')