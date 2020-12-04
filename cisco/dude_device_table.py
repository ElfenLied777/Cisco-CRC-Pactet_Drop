#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime
import csv

USERNAME = os.environ.get('TELNET_USER')
PASSWORD = os.environ.get('TELNET_PASSWORD')

data=[]
cisco_devices=[]
dlink_devices=[]

regex_cisco = re.compile('^cs.*$')
regex_dlink = re.compile('^(DES|DGS).*$')
#to get list 'data' of all devices in dude
try:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome('/usr/lib64/python3.6/site-packages/chromedriver', options=options)
    browser.get('http://10.10.10.10/webfig/#Dude:Devices')
    username = browser.find_element_by_id("name")
    password = browser.find_element_by_id("password")
    time.sleep(5)
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    browser.find_element_by_id("dologin").click()
    time.sleep(10)
    generated_html = browser.page_source
    browser.quit()
    soup=BeautifulSoup(generated_html)
    table = soup.find("table", { "class" : "table" })

    for row in table.findAll("tr"):
        cells = row.findAll("td")
        cells = [element.text.strip() for element in cells]
        data.append([element for element in cells])
except:
    with open('./crc_log/crc_log_{}.txt'.format(datetime.date.today().strftime('%Y_%m_%d')),'a') as f:
        f.write('! Problem of getting table_device from web dude'+'\n')

#to make lists of cisco and dlink devices
for item in data:
    if item and item[3] and re.search(regex_cisco,item[4]): # ip_address !=0 and model cisco
        cisco_devices.append([item[2],item[3],item[4]])
    elif item and item[3] and re.search(regex_dlink,item[4]): # ip_address !=0 and model dlink
        dlink_devices.append([item[2],item[3],item[4]])
    else:
        continue
#to make csv files of all cisco devices and dlink devices 
with open('cisco_devices.csv', 'w') as f:
    writer = csv.writer(f)
    for row in  cisco_devices:
        writer.writerow(row)

with open('../dlink/dlink_devices.csv', 'w') as f:
    writer = csv.writer(f)
    for row in dlink_devices:
        writer.writerow(row)

