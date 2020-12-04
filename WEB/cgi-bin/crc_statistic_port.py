#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import cgi
import sys
import sqlite3
from sqlite3 import Error
from datetime import date, timedelta, time, datetime
from crc_functions import create_connection, get_name_description, get_difference_1device
from crc_home import html_1, html_2, html_end
import os

sys.stderr = sys.stdout # для вывода сообщений об ошибках в браузере

form = cgi.FieldStorage() # извлечь данные из формы из заполненной формы. Тип - словарь.    
address = form['address'].value
port = form['port_type'].value+form['port_number'].value
days = form['days'].value
#address = '172.16.213.1'
#port = 'Te3/3'
#days = '10'
path = os.path.expanduser('~/OOS/cisco')
print(html_1)
db_file = path+'/oos.db' # название базы sqlite3
try:
    conn = create_connection(db_file) # подключиться к базе sqlite3

    device_info = get_name_description(conn,address,port) # получить из таблицы в БД название устройства и description порта - tuple
    name=device_info[0]
    port_description=device_info[1]

    if not port_description:
        port_description = 'None'

    print('<p>Статистика для <b>{}</b> (ip_address=<b>{}</b>) порт <b>{}</b> (description=<b>{}</b>) за <b>{}</b> дня(дней):</p>'.format(name, address, port, port_description, days))
    total_crc = 0
    total_drop_out = 0
    total_drop_in = 0

except:
    print('<b>Ooops... Данных нет. Проверьте введенные параметры запроса (ip_address и port).</b><br><br>')

print('''
    <table class="Table">
    <thead>
        <tr>
            <td><b>Period of Time (Year-Month-Day)</b></td>
            <td><b>CRC</b></td>
            <td><b>Output Dropped Packets</b></td>
            <td><b>Input Dropped Packets</b></td>
        </tr>
    </thead>
    <tbody>
    ''')
for day in range(int(days),0,-1):
    try:
        results = get_difference_1device(conn,day,address,port) #tuple(date_old, date_new, crc, drop_out, drop_in)
        date_old = results[0]
        date_new = results[1]
        crc = results[2]
        drop_out = results[3]
        drop_in = results[4]
        total_crc = total_crc+results[2]
        total_drop_out = total_drop_out+results[3]
        total_drop_in = total_drop_in+results[4]
        print('''
                <tr>
                <td>{}--{}</td>
                <td>{}</td>
                <td>{}</td>
                <td>{}</td>
                </tr>
                '''.format(date_old, date_new, crc, drop_out, drop_in))
    except:
        break
try:
    print('''
            <tr>
                <td><b>Total CRC for {days} days:</b> {total_crc}</td>
            </tr>
            <tr>
                <td><b>Total Output Dropped Packets for {days} days:</b> {total_drop_out}</td>
            </tr>
            <tr>
                <td><b>Total Input Dropped Packets for {days} days:</b> {total_drop_in}</td>
            </tr>
            </tbody>
            </table>

            '''.format(days=days, total_crc=total_crc, total_drop_out=total_drop_out, total_drop_in=total_drop_in))
except:
    print('<b>Ooops... Данных за указанный период времени еще нет. Уменьшите количество дней, за которые требуется вывести статистику.</b><br><br>')
print(html_2)
print(html_end)
conn.close()
