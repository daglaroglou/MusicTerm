import os
import time
import pypresence
import psutil

now = time.time()
p = psutil.process_iter()
if 'discord' in p.name():
    RPC = pypresence.Presence('1109236774972162069')
    RPC.connect()

    while True:
        RPC.update(state="In menu", details="Browsing", large_image="https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif", large_text="MusicTerm", start=now)
        time.sleep(5)