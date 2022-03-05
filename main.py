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
import yaml

TOKEN = "2042203937:AAFW-0twD64bSAo4CU-EZ0XtfMcmsY7LiIg"
tb = telebot.TeleBot(TOKEN)  # create a new Telegram Bot object
telegram_user = 630924196


def set_driver(verbose = False):
    CHROMEDRIVER_PATH = 'C:\\Users\lab7\Desktop\chromedriver_win32\chromedriver.exe'
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    if not verbose:
        chrome_options.add_argument("--headless")
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

def login(d):
    # find login window and switch to its iframe
    frame = d.find_elements_by_id("ctl00_ctl00_ifrmLogin")
    d.switch_to.frame(frame[0])
    try:
        butt = d.find_elements_by_id("btnClose")
        butt[0].click()
    except:
        5
    # Personal Info
    # =======
    c = d.find_elements_by_id("tbUserId")
    c[0].send_keys('304820996')

    c = d.find_elements_by_id("tbUserName")
    c[0].send_keys('DK42967')

    c = d.find_elements_by_id("tbPassword")
    c[0].send_keys('Bardugo23')
    # ===================

    send_butt = d.find_element_by_id('ctl00_cphBody_btnSend')
    send_butt.click()
    pass

def select_physician_and_area(d):
    spec = d.find_element_by_id('SelectedSpecializationCode')
    spec = Select(spec)
    spec.select_by_visible_text('שיננית')

    spec = d.find_element_by_id('SelectedAreaId')
    spec = Select(spec)
    spec.select_by_visible_text('מרכז')

    search_button = d.find_element_by_xpath(
        '//*[@id="searchAmDiary"]/form/table/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/input')
    search_button.click()
    pass

def get_dates_df(d):
    # downlaod data table
    button_list = []
    time.sleep(1.5)
    results = d.find_element_by_id('am_diaries')
    results = results.find_elements_by_tag_name('li')
    df = pd.DataFrame()
    time.sleep(1.5)
    results = d.find_element_by_id('am_diaries')
    results_button_we = results.find_elements_by_id('CreateVisitButton')
    results_dets = results.find_elements_by_tag_name('li')
    page_num = 1
    row_ind = 0
    for ind, i in enumerate(results_dets):
        dets = i.find_elements_by_class_name('clinicDetails')
        if len(dets) > 0:
            distance = re.findall("\d+\.\d+", dets[3].text)
            if len(distance) > 0:
                distance = float(distance[0])
            else:
                distance = None
                continue

            closest_app_string = dets[5].text
            closest_date = dparser.parse(closest_app_string, dayfirst=True, fuzzy=True)

            city = dets[2].text
            city = city[city.index(',') + 2:]

            clinic_city_code = results_button_we[ind].get_attribute('data-cliniccitycode')

            df = df.append(
                pd.DataFrame(index=[row_ind], data=[[distance, closest_date, city, clinic_city_code, page_num]],
                             columns=['distance', 'closest_dat', 'city', 'clinic_city_code', 'page']))
            row_ind = row_ind + 1
            button_list.append(results_button_we[ind])

    # try to see if there is another page
    next_button = d.find_elements_by_partial_link_text('הבא')
    while len(next_button) > 0:
        next_button[0].click()
        page_num = page_num + 1
        time.sleep(1.5)
        results = d.find_element_by_id('am_diaries')
        results_button_we = results.find_elements_by_id('CreateVisitButton')
        results_dets = results.find_elements_by_tag_name('li')
        for ind, i in enumerate(results_dets):
            dets = i.find_elements_by_class_name('clinicDetails')
            if len(dets) > 0:
                distance = re.findall("\d+\.\d+", dets[3].text)
                if len(distance) > 0:
                    distance = float(distance[0])
                else:
                    distance = None
                    continue

                closest_app_string = dets[5].text
                closest_date = dparser.parse(closest_app_string, dayfirst=True, fuzzy=True)

                city = dets[2].text
                city = city[city.index(',') + 2:]

                clinic_city_code = results_button_we[ind].get_attribute('data-cliniccitycode')

                df = df.append(
                    pd.DataFrame(index=[row_ind], data=[[distance, closest_date, city, clinic_city_code, page_num]],
                                 columns=['distance', 'closest_dat', 'city', 'clinic_city_code', 'page']))

                row_ind = row_ind + 1
                button_list.append(results_button_we[ind])
        # look again for a next button
        next_button = d.find_elements_by_partial_link_text('הבא')

    return df

def go_to_page(driver, page_num):
    success = True
    try:
        a = driver.find_elements_by_link_text(str(page_num))
        a[0].click()
    except:
        success = False
    return success

def go_to_selected_clinic(d, ind, df):
    go_to_page(d, df['page'][ind])
    # delay
    time.sleep(1.5)

    # refind buttom
    results = d.find_element_by_id('am_diaries')
    results_button_we = results.find_elements_by_id('CreateVisitButton')
    for i in results_button_we:
        clinic_city_code = i.get_attribute('data-cliniccitycode')
        if clinic_city_code != df['clinic_city_code'][ind]:
            continue
        i.click()
        #delay
        break

def get_hours_and_buttons(d):

    hours = []

    morning = d.find_element_by_id('morning')
    butt = morning.find_elements_by_partial_link_text('הזמן תור')
    hour = morning.text # \n speperates
    for s in hour.split():
        try:
            hours.append(dparser.parse(s,fuzzy = True))
        except:
            5
    noon = d.find_element_by_id('noon')
    butt = butt+ noon.find_elements_by_partial_link_text('הזמן תור')
    hour = noon.text # \n speperates
    for s in hour.split():
        try:
            hours.append(dparser.parse(s,fuzzy = True))
        except:
            5
    evening = d.find_element_by_id('evening')
    butt = butt+evening.find_elements_by_partial_link_text('הזמן תור')
    hour = evening.text # \n speperates
    for s in hour.split():
        try:
            hours.append(dparser.parse(s,fuzzy = True))
        except:
            5

    return hours, butt

def main():

    d = set_driver(verbose = False)
    url = 'https://www.clalit.co.il/he/Pages/default.aspx'
    d.get(url)
    time.sleep(0.5)
    login(d)
    time.sleep(2.5)


    # Go to zimun torim
    d.get('https://e-services.clalit.co.il/OnlineWeb/Services/Tamuz/TamuzTransfer.aspx')

    # switch to clalit smile
    frame = d.find_element_by_id('ifrmMainTamuz')
    d.switch_to.frame(frame)
    smile = d.find_element_by_id('ClalitSmileVisitButton')
    smile.click()


    # slect shinanit
    select_physician_and_area(d)


    df = get_dates_df(d)
    # select object from the df and order the eaarlies/latest appointment in this clinic

    maxday = datetime.datetime.today()+datetime.timedelta(days = 14) # replace 7 days with threshold
    minday = datetime.datetime.today()
    max_distance = 3

    ind = df.loc[(df['distance']<max_distance) & (df['closest_dat']>minday) & (df['closest_dat']<maxday)].index
    #ind = df.loc[(df['distance']<100) & (df['closest_dat']>minday) & (df['closest_dat']<maxday)].index
    ind = df.loc[(df['city']=='גבעתיים') & (df['closest_dat']>minday) & (df['closest_dat']<maxday)].index

    # check if appointment already set
    fname = "config.yaml"
    # fname = "C:\\Users\lab7\PycharmProjects\DentistScheduler\config.yaml"
    stream = open(fname, 'r')
    data = yaml.load(stream)
    isReserved = data['isReserved']


    weekday_dict = {0: 'שני', 1: 'שלישי', 2: 'רביעי', 3: 'חמישי', 4: 'שישי', 5: 'שבת', 6: 'ראשון'}

    if len(ind)>0:
        ind = ind[0]
        # order appointment
        go_to_selected_clinic(d, ind, df)

        hour_ind = 1

        # get the relevant hour in day
        hours, butt = get_hours_and_buttons(d)
        hours_m = [x.hour for x in hours]
        hours_m = np.array(hours_m).ravel()
        hour_ind =np.where((hours_m>16) | (hours_m <11))




        if len(hour_ind[0])>0 and not isReserved:




            # this button orders appontment
            butt[hour_ind[0]].click()
            butt[hour_ind].click()

            # update yaml
            data['isReserved'] = True
            with open(fname, 'w') as yaml_file:
                yaml_file.write(yaml.dump(data, default_flow_style=False))

            #send email button
            email_butt = d.find_elements_by_id('btnSendEmailButton')
            email_butt[0].click()

        #notify me by telegram

            mess = 'ברכותיי, נקבע לך תור אצל השיננית. במרפאה ב'
            mess = mess+df['city'][ind]
            mess = mess+ ' ביום '
            mess = mess+weekday_dict[df['closest_dat'][ind].weekday()]
            mess = mess+ ' '
            mess = mess + df['closest_dat'][ind].strftime("%d/%m/%Y")
            mess = mess + ' בשעה '
            mess = mess + hours[hour_ind[0][0]].strftime('%H:%M')
            mess = mess + hours[hour_ind].strftime('%H:%M')

            tb.send_message(telegram_user, mess)
        else:
            mess = 'נמצא תור פנוי ביום לפי בקשתך במרפאה ב'
            mess = mess + df['city'][ind]
            mess = mess + ' ביום '
            mess = mess + weekday_dict[df['closest_dat'][ind].weekday()]
            mess = mess + ' '
            mess = mess + df['closest_dat'][ind].strftime("%d/%m/%Y")
            mess  = mess + ' אך לא בטווח השעות המבוקש. סור לאתר לפרטים נוספים'
            tb.send_message(telegram_user, mess)

    elif not isReserved:
        ind_close = df.loc[(df['distance'] == df['distance'].min())].index
        ind_early = df.loc[(df['closest_dat'] == df['closest_dat'].min())].index

        mess = 'לא נמצא תור מתאים. התור הכי קרוב הוא ב'
        mess = mess + df['city'][ind_close].values[0]
        mess = mess + ' ביום '
        mess = mess + weekday_dict[pd.to_datetime(df['closest_dat'][ind_close].values[0]).weekday()]
        mess = mess + ' '
        mess = mess + pd.to_datetime(df['closest_dat'][ind_close].values[0]).strftime("%d/%m/%Y")

        mess = mess+ '. התור הכי מוקדם הוא ב'
        mess = mess + df['city'][ind_early].values[0]
        mess = mess + ' ביום '
        mess = mess + weekday_dict[pd.to_datetime(df['closest_dat'][ind_early].values[0]).weekday()]
        mess = mess + ' '
        mess = mess + pd.to_datetime(df['closest_dat'][ind_early].values[0]).strftime("%d/%m/%Y")

        tb.send_message(telegram_user, mess)

if __name__ == '__main__':
    main()




