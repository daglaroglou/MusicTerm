import os
import json
import time
import curses
import psutil
import pypresence
import ytmusicapi
from datetime import datetime

ytmusic = ytmusicapi.YTMusic()

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"; import pygame

def process_exists(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

if process_exists('discord'):
    RPC = pypresence.Presence('1109236774972162069')
    RPC.connect()
    RPC.update(state="In menu", details="Browsing", large_image="https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif", large_text="MusicTerm", start=int(time.time()))

pygame.init()
pygame.mixer.init()

def set_terminal_title(title):
    print(f"\33]0;{title}\a", end="", flush=True)

def load_config():
    with open('settings.json', 'r') as f:
        return json.load(f)

def get_songs_directory(config):
    return os.path.join(os.getcwd(), config['settings']['folder'])

def get_supported_songs(songsDirectory, suffix):
    return [song for song in os.listdir(songsDirectory) if song.endswith(tuple(suffix))]

def print_menu(win, songs, selected_row_idx, volume):
    win.clear()
    h, w = win.getmaxyx()
    for idx, row in enumerate(songs):
        x = w//2 - len(row)//2
        y = h//2 - len(songs)//2 + idx
        if idx == selected_row_idx:
            win.addstr(y, x, row, curses.A_REVERSE)
        else:
            win.addstr(y, x, row)

    controls_info = "[Space] Play/Pause | [Up/Down] Navigate | [S] Stop | [Q] Quit | [=/-] Volume"
    win.addstr(h-2, 0, controls_info, curses.A_BOLD)

    title = "MusicTerm v1.0"
    win.addstr(0, w//2 - len(title)//2, title, curses.A_BOLD)

    volume_info = f"Volume: {volume}%"
    win.addstr(h-1, w - len(volume_info) - 1, volume_info, curses.A_BOLD)

    win.refresh()

def main(stdscr):
    curses.curs_set(0)

    config = load_config()
    songsDirectory = get_songs_directory(config)
    suffix = ['mp3', 'wav', 'ogg']
    songs = get_supported_songs(songsDirectory, suffix)

    current_row = 0
    current_playing_song = None 
    playing = False
    paused = False

    while True:
        volume_percentage = int(pygame.mixer.music.get_volume() * 100)
        print_menu(stdscr, songs, current_row, volume_percentage)
        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(songs) - 1:
            current_row += 1
        elif key == 32:
            if current_playing_song != current_row:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join(songsDirectory, songs[current_row]))
                pygame.mixer.music.play(-1)
                current_playing_song = current_row
                paused = False
                set_terminal_title(f"Playing: {songs[current_row]}")
                r = ytmusic.search(songs[current_row])
                if r:
                    img = r[0]['thumbnails'][0]['url']
                    RPC.update(state=f"Playing at {int(volume_percentage)}% volume", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
                else:
                    img = "https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif"
                    RPC.update(state=f"Playing at {int(volume_percentage)}%", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
                
            else:
                if not paused:
                    pygame.mixer.music.pause()
                    paused = True
                    set_terminal_title("Paused")
                    r = ytmusic.search(songs[current_row])
                    if r:
                        img = r[0]['thumbnails'][0]['url']
                        RPC.update(state="Paused", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
                    else:
                        img = "https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif"
                        RPC.update(state=f"Paused", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
                else:
                    pygame.mixer.music.unpause()
                    paused = False
                    r = ytmusic.search(songs[current_row])
                    if r:
                        img = r[0]['thumbnails'][0]['url']
                        RPC.update(state=f"Playing at {int(volume_percentage)}% volume", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
                    else:
                        img = "https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif"
                        RPC.update(state=f"Playing at {int(volume_percentage)}% volume", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))

        elif key == ord('q') or key == ord('Q'):
            break
        elif key == ord('s') or key == ord('S'):
            pygame.mixer.music.stop()
            set_terminal_title("Stopped")
            RPC.update(state="In menu", details="Browsing...", large_image="https://media.tenor.com/gxOAnTcT8tMAAAAi/musical-notes.gif", large_text="MusicTerm", start=int(time.time()))
        elif key == ord('='):
            volume = pygame.mixer.music.get_volume()
            new_volume = min(volume + 0.025, 1.0)
            pygame.mixer.music.set_volume(new_volume)
            if not paused:
                RPC.update(state=f"Playing at {int(volume_percentage)}% volume", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))
        elif key == ord('-'):
            volume = pygame.mixer.music.get_volume()
            new_volume = max(volume - 0.025, 0.0)
            pygame.mixer.music.set_volume(new_volume)
            if not paused:
                RPC.update(state=f"Playing at {int(volume_percentage)}% volume", details=songs[current_row], large_image=img, large_text="MusicTerm", start=int(time.time()))

if __name__ == "__main__":
    set_terminal_title("MusicTerm")
    curses.wrapper(main)