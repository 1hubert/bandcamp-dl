import os
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import mutagen
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TDRC, TRCK, APIC
import time
import urllib.request


# ID3 info:
# APIC: picture
# TIT2: title
# TPE1: artist
# TRCK: track number
# TALB: album
# TDRC: year


# function validating file names
def valid_name(name):
    deletechars = r"\/:*?\"<>|"
    for i in deletechars:
        if i in name:
            name = name.replace(i, "_")
    return name


# preparing the options for the chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--mute-audio")
options.add_argument("headless")
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--ignore-certificate-errors")
options.add_argument("log-level=3")
options.add_experimental_option('excludeSwitches', ['enable-logging'])


class BandcampDownloader:
    def __init__(self):
        #self.browser = webdriver.Chrome(r'C:\Users\Hubert\AppData\Local\Programs\Python\Python39\chromedriver.exe', options=options)
        self.browser = webdriver.Chrome(r'./resources/chromedriver', options=options)
    
    def download_album(self):
        browser = self.browser
        LOGGER.setLevel(logging.WARNING)

        while True:
            link = input("Paste your Bandcamp album link there: ")

            try:
                browser.get(link)

                time.sleep(1.5)

                # starting and stoping the first song to initialize the player
                play_button = browser.find_element_by_class_name("playbutton")
                play_button.click()
                play_button.click()
                break

            except (InvalidArgumentException, NoSuchElementException):
                print("Ivalid link")
                continue

        # making new directory with the album name
        album_name = browser.find_element_by_css_selector("[id='name-section'] [class='trackTitle']").text.strip()
        print("Making new directory: " + album_name)
        try:
            os.mkdir(valid_name(album_name + " [128K]"))
        except OSError:
            pass
        os.chdir(valid_name(album_name + " [128K]"))

        # extracting song titles and numbers
        print("Downloading album info")
        description = browser.find_element_by_css_selector("[name='description'").get_attribute("content").strip()
        description = description.split("\n\n")

        # seperating numbers from titles
        numbers_and_titles_together = description[1].split("\n")
        numbers_and_titles =[]
        for elem in numbers_and_titles_together:
            
            num = elem.split(". ")[0]
            title = ""

            for idx, el in enumerate(elem.split(". ")):
                if idx > 1:
                    title += '. '
                if idx > 0:
                    title += el

            numbers_and_titles.append([num, title])

        # repairing bad symbols in numbers_and_titles
        for i in range(len(numbers_and_titles)):
            numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace("&#39;", "\'")
            numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace("&amp;", "&")
            numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace("&lt;", "<")
            numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace("&gt;", ">")

        # extracting year and artist
        year = description[0][-4:]
        #artist = browser.find_element_by_css_selector("[id='band-name-location'] [class='title']").text
        artist = browser.find_element_by_css_selector("[property='og:site_name']").text

        # album cover
        print("Downloading album cover")
        album_cover_link = browser.find_element_by_css_selector("[rel='image_src']").get_attribute("href")
        urllib.request.urlretrieve(album_cover_link, "cover.jpg")
        pic_file = os.getcwd() + "\\" + "cover.jpg"
        imagedata = open(pic_file, 'rb').read()

        # that function will be helfpful to prettify the file names
        def add_zeros(num):
            max_num = len(numbers_and_titles)

            if max_num > 99:
                return str(num).zfill(3) + " "

            elif max_num > 9:
                return str(num).zfill(2) + " "

            elif max_num < 10:
                return str(num) + " "

        # "Next Track" button will be used to gain all the player links from the album
        next_track = browser.find_element_by_css_selector("[aria-label='Next track']")

        for i in range(len(numbers_and_titles)):

            # preparing better title and track number
            title = valid_name(numbers_and_titles[i][1])
            track_num = add_zeros(numbers_and_titles[i][0])

            # downloading and naming mp3 file
            print("Downloading " + track_num + title + ".mp3")

            fallbacks = ['19', '18', '17']
            for z in range(len(fallbacks)):
                try:
                    mp3 = browser.find_element_by_css_selector("body > audio:nth-child(" + fallbacks[z] + ")").get_attribute("src")
                    urllib.request.urlretrieve(mp3, track_num + title + ".mp3")
                    break
                except Exception:
                    continue

            # adding tags
            print("Adding tags and cover to " + track_num + title + ".mp3")
            try:
                tags = ID3(os.getcwd() + "\\" + track_num + title + ".mp3")
            except mutagen.id3.ID3NoHeaderError:
                tags = ID3()

            # those tags are different in each iteration    
            tags["TRCK"] = TRCK(encoding=3, text=numbers_and_titles[i][0])
            tags["TIT2"] = TIT2(encoding=3, text=numbers_and_titles[i][1])

            # those tags are constant
            tags["TALB"] = TALB(encoding=3, text=album_name)
            tags["TPE1"] = TPE1(encoding=3, text=artist)
            tags["TDRC"] = TDRC(encoding=3, text=year)
            tags["APIC"] = APIC(3, 'image/jpeg', 3, 'Cover', imagedata)

            # saving tags
            tags.save(os.getcwd() + "\\" + track_num + title + ".mp3", v2_version=3)

            # changing the track
            # now the mp3 variable is holding different link
            if i+1 < len(numbers_and_titles):
                next_track.click()

        
        print("Finished downloading " + album_name)
        print()

        os.chdir("..")


if __name__ == "__main__":
    while True:
        BandcampDownloader().download_album()