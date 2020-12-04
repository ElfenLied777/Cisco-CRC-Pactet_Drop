#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error
from datetime import date, timedelta, datetime, time
from  crc_functions import create_connection, get_data_today, get_difference_all_1day
from crc_home import html_1, html_2, html_end
import os

path = os.path.expanduser('~/OOS/cisco')
print(html_1)
print(html_2)
db_file = path+'/oos.db' # название базы sqlite3
try:
    conn = create_connection(db_file) #  подключиться к базе sqlite3
    data_today = get_data_today(conn) # список кортежей с данными сетевых элементов, для которых crc или dropped packets >0. Данные берутся из самой последней созданной таблице 
    result = get_difference_all_1day(conn,1,data_today)
    conn.close()
except:
    print('<b>Ooops... Что-то пошло не так(((')
print('<p>Значения CRC и Output_dropped_packets на портах оборудования cisco опорной сети ШПД за последние сутки:</p>')
print('<pre>')
print(result)
print("</pre>")
print(html_end)
