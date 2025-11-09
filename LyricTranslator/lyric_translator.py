
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time

import keyboard

from opencc import OpenCC

class LyricTranslator:

    def __init__(self):
        self.converter_t2s = OpenCC('t2s')
    
    def run(self):
        self.open_browser()
        lyrics_sim = self.set_lyrics(3)

        print("ESC to stop")
        while(True):
            lyrics_sim = self.set_lyrics()

            if not self.hasLyrics:
                continue

            if keyboard.is_pressed("esc"):
                try:
                    self.driver.quit()
                except Exception as e:
                    pass
                print("Stopped.")
                break

            time.sleep(0.01)
    
    #extension: compatibility for multiple browser types
    def open_browser(self):
        #chrome for now

        #driver stuff
        options = webdriver.ChromeOptions()
        
        #driver init
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            print("Sign in with account, then start playing")
            #opens a new chrome browser
            self.driver.get("https://open.spotify.com")

            #fullscreen
            self.driver.maximize_window()

            #we need the user to sign in
            #input("Sign in with your account then press enter to continue")
            while not self.check_for_login():
                time.sleep(1)

            #we want to be on https://www.open.spotify.com/lyrics so reassign the url
            self.driver.get("https://open.spotify.com/lyrics")

            time.sleep(1)
        except (WebDriverException) (KeyboardInterrupt):
            pass
    
    def check_for_login(self):
        
        if 'https://accounts.spotify.com' in self.driver.current_url or 'https://challenge.spotify.com/' in self.driver.current_url:
            return False
        
        try:
            sign_in_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="login-button"]')
        except Exception as e:
            return True
        
        if sign_in_button is not None:
            return False

        return True

    def get_current_lyrics(self, lyrics, lyric_index, lines=5):
        #get like 5 lines of lyrics
        #make sure to account for the length of the thingy at the end
        #so that there is no overdraft when less than 5 lines is avaliable
        lyric_current = ""
        for i in range(lines):

            if len(lyrics) > lyric_index + i:
                lyric_current += lyrics[lyric_index+i][0] + "\n"
        return lyric_current

    def get_current_lyric_index(self):
        #third term of the lyric
        #o69qODXrbOkf6Tv7fa51 FQYXZaa0aDIrse54YlYO ve52ddYhoAd3Xf27Zxfm
        #ve52ddYhoAd3Xf27Zxfm == lyric already played
        #_gZrl2ExJwyxPy1pEUG2 == lyric currently on
        # no third term == not played yet
        #we need a realtime function to get the current lyric being played (only the line # is needed)
        
        if not self.hasLyrics:
            return None
        
        lyric_index = 0

        for i in range(len(self.lyric_lines)):
            
            try:
                class_atr = self.lyric_lines[i].get_attribute('class')
            except Exception as e:
                return None
            if class_atr is not None and "_gZrl2ExJwyxPy1pEUG2" in class_atr:
                lyric_index = i

                break
        
        return lyric_index


    
    def set_lyrics(self, waitTime=0):
        try:
            #let the webpage load
            if waitTime > 0:
                time.sleep(waitTime)

            try:
                lyrics_organizer = self.driver.find_element(By.CSS_SELECTOR, '.t_dtt9KL1wnNRvRO_y5L')
            except Exception as e:
                #VrI8jP8wkOIpseiHkdBl is the class that shows either lyrics dont exist for this song or cant load lyrics
                #we dont need to explicitly check just return
                self.hasLyrics = False
                return []

            lyrics_bundles = lyrics_organizer.find_elements(By.CSS_SELECTOR, '[data-testid="fullscreen-lyric"]')
            
            #we want this because later we are checking class on this
            self.lyric_lines = []

            trad_lyrics = []
            sim_lyrics = []
            #IMPORTANT: SUBTRACT 1 because the last element throws an exception
            for i in range(len(lyrics_bundles)):

                #lyric holder at index i, 
                try:
                    self.lyric_lines.append(lyrics_bundles[i])

                    current_text_element = lyrics_bundles[i].find_element(By.CSS_SELECTOR, '.MmIREVIj8A2aFVvBZ2Ev')

                    current_lyric_line = current_text_element.text
                    trad_lyrics.append([current_lyric_line, i])

                    translated_text = self.converter_t2s.convert(current_lyric_line)

                    self.driver.execute_script("arguments[0].innerText = arguments[1];", current_text_element, translated_text)

                    sim_lyrics.append([translated_text, i])
                except Exception as e:

                    self.hasLyrics = False
                    return []

            self.hasLyrics = True

            return sim_lyrics
        except (WebDriverException) (KeyboardInterrupt):
            pass
    #already assume browser is open
    def get_playing_state(self):

        if not self.get_tab_state():
            return False

        self.play_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='control-button-playpause']")
        
        state = self.play_button.get_attribute('aria-label')

        #aria label is reversed
        #when it is Play: it means that the audio is paused
        #when it is Pause: it means that the song is playing
        if state == "Pause":
            return True
        else:
            return False

    def get_tab_state(self):
        if self.driver.current_url == "https://open.spotify.com/lyrics":
            return True
        return False


lyric_translator = LyricTranslator()
lyric_translator.run()
