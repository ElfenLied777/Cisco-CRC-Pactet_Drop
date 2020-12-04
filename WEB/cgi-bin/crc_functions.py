#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import sys
import sqlite3
from sqlite3 import Error
from datetime import date, timedelta, time, datetime
import os


path = os.path.expanduser('~/OOS/cisco')

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        with open(path+'/crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(date.today().strftime('%Y_%m_%d'),e))
        print('Не могу подключиться к базе данных для получения запрошенной информации')
    return None

'''def get_date():
    """ Return date_today: if current time=00:00-08:15 then date_today = yesterday date; if current time!=00:00-08:15 then date_today = today date"""
    if time(0,0,0) <= current_time <= time(8,15,0):
        date_today = date.today()-timedelta(1)
    else:
        date_today = date.today()
    return date_today
'''

def get_name_description(conn,address,port,device_type='cisco'):
    """ get name of the network device and port description from sqlite table. Checking presence of the device's data in the table.
    :param conn: Connection object
    :date_taday: today date
    :return: device_data - tuple: name of the device and port description
    """
    table_name = '_{}_{}'.format(date.today().strftime('%Y_%m_%d'), device_type)
    try:
        select = conn.execute("select name, description from {} where address='{}' and port='{}'".format(table_name, address, port))
        device_info = select.fetchone() #tuple
    except Error as e:
        with open(path+'/crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(date.today().strftime('%Y_%m_%d'),e))
        print('<b>Ooops... Данных нет. Проверьте введенные параметры запроса (ip_address и port).</b><br><br>')
    return device_info

def get_difference_1device(conn,some_days_ago,address,port,device_type='cisco'):
    """ get difference value of crc and dropped packets between 2 next days. It's used in the cycle.
    :param conn: Connection object
    :param some_days_ago: is changeable argument of the cycle
    :return: tuple (date_old, date_new, crc, drop_out, drop_in) or Error
    """
    date_old = (date.today()-timedelta(some_days_ago)).strftime('%Y_%m_%d')
    date_new = (date.today()-timedelta(some_days_ago-1)).strftime('%Y_%m_%d')
    table_name_old = '_{}_{}'.format(date_old, device_type)
    table_name_new = '_{}_{}'.format(date_new, device_type)
    try:
        data_old = conn.execute("select crc,drop_out,drop_in from {} where address='{}' and port='{}'".format(table_name_old, address, port))
        result_old = data_old.fetchone() #tuple of crc and dropped packets on previous date
        data_new = conn.execute("select crc,drop_out,drop_in from {} where address='{}' and port='{}'".format(table_name_new, address, port))
        result_new = data_new.fetchone() #tuple of crc and dropped packets on current date
        difference_crc = int(result_new[0])-int(result_old[0])
        difference_drop_out = int(result_new[1])-int(result_old[1])
        difference_drop_in = int(result_new[2])-int(result_old[2])
        if difference_crc > 0:
            crc = difference_crc
        elif difference_crc < 0:
            crc = int(result_new[0])
        else:
            crc = 0
        if difference_drop_out > 0:
            drop_out = difference_drop_out
        elif difference_drop_out < 0:
            drop_out = int(result_new[1])
        else:
            drop_out = 0
        if difference_drop_in > 0:
            drop_in = difference_drop_in
        elif difference_drop_in < 0:
            drop_out = int(result_new[2])
        else:
            drop_in = 0
    except Error as e:
        with open(path+'/crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(date.today().strftime('%Y_%m_%d'),e))
        print( '<b>Ooops... Данных за указанный период времени еще нет. Уменьшите количество дней, за которые требуется вывести статистику.</b><br><br>')
    return date_old, date_new, crc, drop_out, drop_in

def get_data_today(conn, device_type='cisco'):
    """ get data from sqlite3 db table created today
    :param conn: Connection object
    :param device type: the producer of network devices
    :return: list of tuples with data received on current day where crc>0
    """
    table_name_today = '_{}_{}'.format(date.today().strftime('%Y_%m_%d'), device_type)
    query = '''SELECT * FROM {} where status = 'connected' and crc>0'''.format(table_name_today)
    try:
        data_today=[row for row in conn.execute(query)]
    except Error as e:
        with open(path+'/crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(date_today.strftime('%Y_%m_%d'), e))
    return data_today

def get_difference_all_1day(conn,some_days_ago,data_today,device_type='cisco'):
    """ insert in table data information about all network devices on current date
    :param conn: Connection object
    :param some_days_ago: the count of days when interesting data was received before current date 
    :return: string result with differential value of crc and dropped packets in output
    """
    table_name_some_days_ago = '_{}_{}'.format((date.today()-timedelta(some_days_ago)).strftime('%Y_%m_%d'), device_type)
    result = ''
    total = 0
    for line in data_today:
        try:
            data_old = conn.execute("select crc,drop_out,drop_in from {} where address='{}' and port='{}'".format(table_name_some_days_ago, line[1], line[3]))
            result_old = data_old.fetchone() #tuple of crc and dropped out/in packets on previous date
            if not result_old: # there is not the device in previous table
                crc = line[6]
                drop_out = line[7]
                drop_in = line[8]
            else:
                crc_old = result_old[0]
                drop_out_old = result_old[1]
                drop_in_old = result_old[2]

                difference_crc = int(line[6])-int(crc_old)
                difference_drop_out = int(line[7])-int(drop_out_old)
                difference_drop_in = int(line[8])-int(drop_in_old)

                if difference_crc > 0:
                    crc = difference_crc
                elif difference_crc < 0:
                    crc = line[6]
                else:
                    crc = 0

                if difference_drop_out > 0:
                    drop_out = difference_drop_out
                elif difference_drop_out < 0:
                    drop_out = line[7]
                else:
                    drop_out = 0

                if difference_drop_in > 0:
                    drop_in = difference_drop_in
                elif difference_drop_in < 0:
                    drop_in = line[8]
                else:
                    drop_in = 0

            if int(crc) == 0:
                continue
            else:
                result = result + '''{:<15} {:<15} {:<10} {:<30} {:<10} {:<10} {:<10}\n'''.format(line[0], line[1], line[3], line[4], crc, drop_out, drop_in)
                total += 1
        except Error as e:
            with open(path+'/crc_log/log_db_conn.txt', 'a') as f:
                f.write('{}:{}\n'.format(date_today.strftime('%Y_%m_%d'), e))
    start = '''{:<15} {:<15} {:<10} {:<30} {:<10} {:<10} {:<10}\n{}\n'''.format('name', 'ip_address', 'port', 'port_description', 'crc', 'drop_out', 'drop_in', '-'*100)
    end = '-'*100 + '\n' + 'Total:{}'.format(total)
    result = start + result + end
    return result




