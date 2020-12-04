#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from get_current_data_cisco import create_connection
import sqlite3
from sqlite3 import Error

name = input('input name of the device:')
ip_address = input('input ip address of the device:')
mac = input('input MAC of the device (for example C4:0A:CB:99:C3:C1):')
model = input('input type of the device (for example cs-C2960_OOS):')
data = (name, ip_address, mac, model)

db_file = '/home/vika/oos/oos.db'
conn = create_connection(db_file)
query = 'INSERT into cisco_oos (name, ip_address, mac, type) VALUES (?, ?, ?, ?)'
try:
    conn.execute(query, data)
except Error as e:
    print(e)
conn.commit()

