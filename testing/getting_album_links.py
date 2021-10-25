import os
import requests
from selenium import webdriver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import mutagen
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, COMM, TCOM, TCON, TDRC, TRCK, APIC
import time
import urllib.request



# ID3 info:
# APIC: picture
# TIT2: title
# TPE1: artist
# TRCK: track number
# TALB: album
# TDRC: year


# function used to making directories
def makedir(newpath):
    try:
        os.makedirs(newpath)
    except Exception:
        pass
    
    #cd into the specified dir
    os.chdir(newpath)


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


#link = "https://midwestcollective.us/"
link = "https://wavforme.bandcamp.com/"
#link = "https://tobyfox.bandcamp.com/music"
browser = webdriver.Chrome(r'./resources/chromedriver', options=options)
LOGGER.setLevel(logging.WARNING)
browser.get(link)
time.sleep(1.5)

#collections
# // /
#tags = browser.find_elements_by_xpath("//*[@id=\"pgBd\"]/div[2]/ol[2]/li/a")

#discography
# last characters /music
tags = browser.find_elements_by_xpath("//*[@id=\"pgBd\"]/div[2]/ol/li/a")

album_links = []
for link in tags:
    album_links.append(link.get_attribute("href"))
    print(link.get_attribute("href"))


print(album_links)
print(len(album_links))


