import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import Select
import re
import dateutil.parser as dparser
import datetime
import numpy as np
import telebot


TOKEN = "2042203937:AAFW-0twD64bSAo4CU-EZ0XtfMcmsY7LiIg"
tb = telebot.TeleBot(TOKEN)  # create a new Telegram Bot object





def set_driver():
    # CHROMEDRIVER_PATH = 'C:\\Users\lab7\Downloads\chromedriver_win32_2\chromedriver.exe'
    CHROMEDRIVER_PATH = 'C:\\Users\lab7\Desktop\chromedriver_win32\chromedriver.exe'
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    # if ubuntu
    if sys.platform=='linux':
        # sudo apt-get install chromium-chromedriver
        d = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver",
                             chrome_options=chrome_options)
    else: # windows
        d = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                             chrome_options=chrome_options)
    return d



base_url = 'https://maccabi-dent.com/%d7%aa%d7%95%d7%a8-%d7%9c%d7%9c%d7%90-%d7%a1%d7%99%d7%a1%d7%9e%d7%90/'

d = set_driver()


d.get(base_url)
sel =  d.find_elements_by_xpath("//span[.='סוג התור המבוקש']")
sel[0].click()
# sel = Select(sel[0])
# press on שיננית
d.find_elements_by_xpath("//*[@for='requested_service4']")[0].click()
# enter bday
# date = d.find_elements_by_xpath("//*[@name ='bdate']")[0]
date = d.find_elements_by_xpath("//*[@type ='text']")[0]
date.click()
date.send_keys('24/05/1991')
time.sleep(1)

loc = d.find_elements_by_xpath("//*[@type ='text']")[1]
loc.click()
loc.send_keys('גבעתיים')


# loc = d.find_elements_by_xpath("//*[@class='search_results']")[0]
# loc.click()
time.sleep(5)

autocomplete = d.find_element_by_xpath('//*[@class="ui-menu-item"]')
autocomplete.click()

submit =d.find_element_by_xpath('//*[@type="submit"]')
submit.click()

time.sleep(20)


# choose specific dentist
doc = d.find_elements_by_xpath("//*[@class ='doctor_select']")[0]
doc.click()
el = d.find_elements_by_xpath("//*[contains(text(),'לילך אלפי')]")
el[0].click()

time.sleep(20)
# scrape data
date = d.find_elements_by_xpath("//*[@class ='td date']")
dates = []
pageFlag = True
while pageFlag:
    for i in range(1, len(date)):
        dates.append(datetime.datetime.strptime(date[i].text, '%d/%m/%Y'))
    try:
        next_page_butt = d.find_elements_by_xpath("//*[@class ='page-link next']")[0].click()
    except:
        break
    date = d.find_elements_by_xpath("//*[@class ='td date']")
# % next page
dates_giv = dates

#TODO same for other clinic
time.sleep(15)
d.get(base_url)
sel =  d.find_elements_by_xpath("//span[.='סוג התור המבוקש']")
sel[0].click()
# sel = Select(sel[0])
# press on שיננית
d.find_elements_by_xpath("//*[@for='requested_service4']")[0].click()
# enter bday
# date = d.find_elements_by_xpath("//*[@name ='bdate']")[0]
date = d.find_elements_by_xpath("//*[@type ='text']")[0]
date.click()
date.send_keys('24/05/1991')
time.sleep(1)

loc = d.find_elements_by_xpath("//*[@type ='text']")[1]
loc.click()
loc.send_keys('הוד השרון')


# loc = d.find_elements_by_xpath("//*[@class='search_results']")[0]
# loc.click()
time.sleep(5)

autocomplete = d.find_element_by_xpath('//*[@class="ui-menu-item"]')
autocomplete.click()

submit =d.find_element_by_xpath('//*[@type="submit"]')
submit.click()

time.sleep(20)


# choose specific dentist
doc = d.find_elements_by_xpath("//*[@class ='doctor_select']")[0]
doc.click()
el = d.find_elements_by_xpath("//*[contains(text(),'לילך אלפי')]")
el[0].click()

time.sleep(20)
# scrape data
date = d.find_elements_by_xpath("//*[@class ='td date']")
dates = []
pageFlag = True
while pageFlag:
    for i in range(1, len(date)):
        dates.append(datetime.datetime.strptime(date[i].text, '%d/%m/%Y'))
    try:
        next_page_butt = d.find_elements_by_xpath("//*[@class ='page-link next']")[0].click()
    except:
        break
    date = d.find_elements_by_xpath("//*[@class ='td date']")
# % next page
dates_hod = dates


if np.min(dates_hod)<np.min(dates_giv):
    dates = dates_hod
    clinic = 'הוד השרון'
else:
    dates = dates_giv
    clinic = 'גבעתיים'

#closest date
nofar_id = 5025110019
if np.min(dates)<datetime.datetime.strptime('01-04-2022','%d-%m-%Y'):
    mess = 'נמצא תור קרוב. התור הקרוב הוא בתאריך: '
    mess = mess + datetime.datetime.strftime(np.min(dates),'%d-%m-%Y')
    mess = mess+ ' במרפאה ב'
    mess = mess + clinic
    mess = mess+ '. סורי זריז לאתר להזמין למה לא הזמנתי'
    tb.send_message(nofar_id, 'mess')




