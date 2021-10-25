from selenium.common.exceptions import InvalidArgumentException
from selenium import webdriver
import urllib
browser = webdriver.Chrome('./resources/chromedriver.exe')
full_track_filename="adasdfasd"
fallbacks=[12, 123]
browser.get("https://www.google.com")
for z in range(len(fallbacks)):
            
            mp3 = browser.find_element_by_css_selector("body > audio:nth-child(" + fallbacks[z] + ")").get_attribute("src")
            urllib.request.urlretrieve(mp3, full_track_filename)
            break


print("EEND")