import time
import os
import logging
import calendar
import urllib.request

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER
import mutagen
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TRCK, APIC, TDRC


# ID3 info:
#   APIC: picture
#   TIT2: title
#   TPE1: artist
#   TRCK: track number
#   TALB: album
#   TDRC: year


def valid_name(name: str):
    """Replace bad characters in filenames with an underscore."""
    deletechars = r'\/:*?\"<>|'
    for i in deletechars:
        if i in name:
            name = name.replace(i, ' ')
    return name


# preparing the options for the chrome driver
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--mute-audio')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


def download_album(link: str):
    browser.get(link)
    time.sleep(1.5)

    # Play and pause the first song to initialize the player.
    play_button = browser.find_element_by_class_name('playbutton')
    play_button.click()
    play_button.click()

    # Extract song numbers and titles.
    print('Downloading album info')
    description = browser.find_element_by_css_selector("[name='description']").get_attribute('content').strip()
    description = description.split('\n\n')

    # Seperate numbers from titles.
    numbers_and_titles_together = description[1].split('\n')
    numbers_and_titles =[]
    for elem in numbers_and_titles_together:
        
        num = elem.split('. ')[0]
        title = ''

        for idx, el in enumerate(elem.split('. ')):
            if idx > 1:
                title += '. '
            if idx > 0:
                title += el
        try:
            if title[2] == '.' and title[3] == ' ':
                title=title[4:]
        except IndexError:
            pass

        numbers_and_titles.append([num, title])

    # Repair bad symbols.
    for i in range(len(numbers_and_titles)):
        numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace('&#39;', '\'')
        numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace('&amp;', '&')
        numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace('&lt;', '<')
        numbers_and_titles[i][1] = str(numbers_and_titles[i][1]).replace('&gt;', '>')

    # Find the album release date on Bandcamp.
    date = browser.find_element_by_css_selector("[class='tralbumData tralbum-credits']").text.strip().split('\n')[0]
    date = date[9:]

    date_year = date.split(', ')[1]
    date_month = str(list(calendar.month_name).index(date.split(' ')[0]))
    date_days = date.split(', ')[0].split(' ')[1]
    if len(date_days) == 1:
        date_days = '0' + date_days
    
    date = date_year + '.' + date_month + '.' + date_days

    # Make a new directory with the album's name.
    album_name = browser.find_element_by_css_selector("[id='name-section'] [class='trackTitle']").text.strip()
    album_folder_name = valid_name(f'[{date}] - {album_name} [128K]')
    print(f'Making new directory: {album_folder_name}')
    try:
        os.mkdir(album_folder_name)
    except OSError:
        pass
    os.chdir(album_folder_name)

    # Extract year and artist.
    year = description[0][-4:]
    artist = browser.find_element_by_css_selector("[property='og:site_name']").text

    # Download and save album cover.
    print('Downloading album cover')
    album_cover_link = browser.find_element_by_css_selector("[rel='image_src']").get_attribute('href')
    urllib.request.urlretrieve(album_cover_link, 'cover.jpg')
    pic_file = os.getcwd() + '\\' + 'cover.jpg'
    imagedata = open(pic_file, 'rb').read()

    def add_leading_zeros(num: int):
        """Return a prettified string with a space at the end."""
        return str(num).zfill(len(str(len(numbers_and_titles)))) + ' '

    # Needed to get all of the album's mp3s.
    next_track = browser.find_element_by_css_selector("[aria-label='Next track']")

    for i in range(len(numbers_and_titles)):
        track_num = add_leading_zeros(i+1)
        title = valid_name(numbers_and_titles[i][1])
        artist = browser.find_element_by_css_selector("[class='title']").text.split(' - ')[0]

        try:
            artist = artist + ' feat. ' + title.split(' feat. ')[1]
            title = title.split(' feat. ')[0]
        except IndexError:
            pass

        # Download and name the mp3 file.
        full_track_filename = track_num + valid_name(artist) + ' - ' + valid_name(title) + '.mp3'
        print(f'Downloading {full_track_filename} (Artist: {artist})')
        fallbacks = ['19', '18', '17']
        for z in range(len(fallbacks)):
            try:
                mp3 = browser.find_element_by_css_selector('body > audio:nth-child(' + fallbacks[z] + ')').get_attribute('src')
                urllib.request.urlretrieve(mp3, full_track_filename)
                break
            except ValueError:
                continue

        # Add tags.
        print(f'Adding tags and cover to {full_track_filename}')
        try:
            tags = ID3(os.getcwd() + '\\' + full_track_filename)
        except mutagen.id3.ID3NoHeaderError:
            tags = ID3()

        # Those tags are different in each iteration.
        tags['TRCK'] = TRCK(encoding=3, text=numbers_and_titles[i][0])
        try:
            tags['TIT2'] = TIT2(encoding=3, text=numbers_and_titles[i][1].split(' - ')[1])
        except IndexError:
            tags['TIT2'] = TIT2(encoding=3, text=title)

        # Those tags are constant in each iteration.
        tags['TALB'] = TALB(encoding=3, text=album_name)
        tags['TPE1'] = TPE1(encoding=3, text=artist)
        tags['TDRC'] = TDRC(encoding=3, text=year)
        tags['APIC'] = APIC(3, 'image/jpeg', 3, 'Cover', imagedata)

        # Save tags.
        tags.save(os.getcwd() + '\\' + full_track_filename, v2_version=3)

        # Change the track so the mp3 variable holds a different link.
        if i+1 < len(numbers_and_titles):
            next_track.click()
    
    print(f'Finished downloading {album_name}')
    print()
    os.chdir('..')


if __name__ == '__main__':
    browser = webdriver.Chrome(r'./resources/chromedriver.exe', options=options)
    LOGGER.setLevel(logging.WARNING)
    os.chdir('downloads')

    while True:
        link = input('Paste Bandcamp artist/label link here: ')
        while 'bandcamp.com' not in link:
            link = input('This is not a bandcamp link, try again:  ')
        
        browser.get(link)
        time.sleep(1.5)

        if 'album' in link:
            download_album(link)

        else:
            tags = browser.find_elements_by_xpath('//*[@id=\"pgBd\"]/div[2]/ol/li/a')
            album_links = []
            for link in tags:
                album_links.append(link.get_attribute('href'))
                print(link.get_attribute('href'))

            print(f'Downloading {len(album_links)} albums')

            for actual_link in album_links:
                download_album(actual_link)

        browser.quit()