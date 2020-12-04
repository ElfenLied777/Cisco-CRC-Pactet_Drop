#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import os
import pexpect
import sqlite3
from sqlite3 import Error
import datetime
#import time
import re
#from concurrent.futures import ThreadPoolExecutor
import csv

USERNAME = os.environ.get('TELNET_USER')
PASSWORD = os.environ.get('TELNET_PASSWORD')

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
        with open('crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(datetime.date.today().strftime('%Y_%m_%d'),e))
    return None

def create_table_current_date(conn, device_type='cisco'):
    """ create a table with current data of all network devices on current date
    :param conn: Connection object
    :param device_type: cisco (default). Can be another type (for example D-Link)
    :return: the name of empty new table
    """
    table_name = '_{}_{}'.format(datetime.date.today().strftime('%Y_%m_%d'), device_type)
    create_table = 'create table IF NOT EXISTS {} (name text not NULL, address text not NULL, model text not NULL, port text not NULL, description text, status text not NULL, crc text, drop_out text, drop_in text, PRIMARY KEY (name, address, port))'.format(table_name)
    try:
        conn.execute(create_table)
    except Error as e:
        with open('crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(datetime.date.today().strftime('%Y_%m_%d'),e))
    return table_name

def insert_data_into_current_table(conn, table_name, data):
    """ insert in table data information about all network devices on current date
    :param conn: Connection object
    :param table_name: the name of current new table
    :return:
    """
    query = 'INSERT into {} (name, address, model, port, description, status, crc, drop_out, drop_in) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'.format(table_name)
    try:
        conn.execute(query, data)
    except Error as e:
        with open('crc_log/log_db_conn.txt', 'a') as f:
            f.write('{}:{}\n'.format(datetime.date.today().strftime('%Y_%m_%d'),e))
    conn.commit()

def get_current_data_cisco(device):
    """ get data from every network device
    :param device: ip address of the network device
    :return: list of tuples with data
    """
    try:
        with pexpect.spawn('telnet {}'.format(device[1])) as telnet:
            telnet.expect('[Uu]sername:')
            telnet.sendline(USERNAME)
            telnet.expect('[Pp]assword:')
            telnet.sendline(PASSWORD)
            telnet.expect('\S+#')
            telnet.sendline('terminal length 0')
            telnet.expect('\S+#')
            telnet.sendline('sh interfaces status')
            telnet.expect('\S+#')
            show_output = telnet.before.decode('utf-8')
            if '% Invalid' in show_output: # if the device is a router, need to use another command
                telnet.sendline('sh interfaces description')
                telnet.expect('\S+#')
                show_output = telnet.before.decode('utf-8')
                regex = regex_port_router # регулярное выражение для вычисления портов на роуете
            else:
                regex = regex_port # регулярное выражение для вычисления портов на L3 свитче
            for line in show_output.split('\n'):
                match = re.search(regex, line)
                if match:
                    if match.group('status') == 'connected' or match.group('status') == 'up':
                        telnet.sendline('sh interfaces {}'.format(match.group('port')))
                        telnet.expect('\S+#')
                        show_output_int = telnet.before.decode('utf-8')
                        match_crc = re.search(regex_crc, show_output_int)
                        match_drop_out = re.search(regex_drop_out, show_output_int)
                        match_drop_in = re.search(regex_drop_in, show_output_int)
                        if match_drop_out:
                            drop_out = match_drop_out.groups()
                        else:
                            drop_out = ('0',)
                        if match_drop_in:
                            drop_in = match_drop_in.groups()
                        else:
                            drop_in = ('0',)
                        if match_crc:
                            crc = match_crc.groups()
                        else:
                            crc = ('0',)
                        data_device.append(tuple(device)+match.groups()+crc+drop_out+drop_in)
                    else:
                        crc = drop_out = drop_in =  ('0',)
                        data_device.append(tuple(device)+match.groups()+crc+drop_out+drop_in)
    except pexpect.TIMEOUT:
        with open('crc_log/log{}.txt'.format(table_name), 'a') as f:
            f.write('{} does not respond\n'.format(device))
    except pexpect.EOF:
        with open('crc_log/log{}.txt'.format(table_name), 'a') as f:
            f.write('{} login fail: username or password is incorrect\n'.format(device))
    except:
        return None
    return data_device

'''def threads_conn(function, devices, limit=10):
    with ThreadPoolExecutor(max_workers=limit) as executor:
        futures = list(executor.map(function, devices, timeout=60))
    return futures
'''
if __name__ == '__main__':
    import dude_device_table

    db_file = 'oos.db'
    conn = create_connection(db_file)
    table_name = create_table_current_date(conn)

    devices = [] #list of lists [name,ipaddress,model]
    with open('cisco_devices.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            devices.append(row)
    regex_port_router = re.compile('(?P<port>Fa[\d/]+|Gi[\d/]+|Te[\d/]+)[\. ] +(?P<status>up|down|admin down) +\S+ +(?P<name>\S*)')
    regex_port = re.compile('(?P<port>Fa[\d/]+|Gi[\d/]+|Te[\d/]+) +(?P<name>\S*) +(?P<status>connected|notconnect|disabled)')
    regex_crc = re.compile(r'^.* (?P<crc>\d+) CRC,.*$', re.MULTILINE)
    regex_drop_in = re.compile(r'^.*Input queue: \d+/\d+/(?P<drop_in>\d+)/\d+ .*$',re.MULTILINE)
    regex_drop_out = re.compile(r'^.*Total output drops: (?P<drop_out>\d+).*$',re.MULTILINE)
    #futures = threads_conn(get_current_data_cisco, devices)
    data_device = [] # list of tuples with data

    for device in devices: # device it's the list
        get_current_data_cisco(device)

    for data in data_device:
        insert_data_into_current_table(conn, table_name, data)

    #data - список кортежей с данными по каждому порту, формируется из списков кортежей, соответствующим каждому устройству
    #data = [item for future in futures for item in future]
    #for data in data:
     #   insert_data_into_current_table(conn, table_name, data)

    conn.close()
