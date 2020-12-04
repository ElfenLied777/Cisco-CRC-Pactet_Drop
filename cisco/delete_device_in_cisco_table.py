#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from get_current_data_cisco import create_connection
import sqlite3
from sqlite3 import Error

ip_address = input('input ip address of the device you want to delete from the table:')

db_file = '/home/vika/oos/oos.db'
conn = create_connection(db_file)
query = 'DELETE FROM cisco_oos where ip_address = {}'.format(ip_address)
try:
    conn.execute(query)
except Error as e:
    print(e)
conn.commit()

