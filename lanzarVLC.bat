"C:\Program Files\VideoLAN\VLC\vlc" -vvv "C:\Users\Usuario\Desktop\redes\lab2Redes\videoplayback.mp4" –sout "#transcode{vcodec=mp4v,acodec=mpga}:rtp{proto=udp, mux=ts,dst=127.0.0.1, port=65534}" --loop --ttl 1