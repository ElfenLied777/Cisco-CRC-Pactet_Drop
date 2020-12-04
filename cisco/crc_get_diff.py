#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
from sqlite3 import Error
from datetime import date, timedelta
from crc_get_current_data_cisco import create_connection
import smtplib
from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText                # Текст/HTML
from email.header import Header

def get_data_today(conn, date_today, device_type='cisco'):
    """ get data from sqlite3 db table created today
    :param conn: Connection object
    :param device type: the producer of network devices
    :return: list of tuples with data received on current day where crc>0
    """
    table_name_today = '_{}_{}'.format(date_today, device_type)
    query = '''SELECT * FROM {} where status = 'connected' and crc>0'''.format(table_name_today)
    try:
        data_today=[row for row in conn.execute(query)]
    except Error as e:
        with open('crc_log/log_db_oos.txt', 'a') as f:
            f.write('{}:{}\n'.format(date_today, e))
    return data_today

def get_difference(conn,some_days_ago,device_type='cisco'):
    """ insert in table data information about all network devices on current date
    :param conn: Connection object
    :param some_days_ago: the count of days when interesting data was received before current date
    :return: string result with differential value of crc and dropped packets in output and input
    """
    table_name_some_days_ago = '_{}_{}'.format((date.today()-timedelta(some_days_ago)).strftime('%Y_%m_%d'), device_type)
    result = ''
    total = 0
    for line in data_today: # (name,address,model,port,description,status,crc,drop_out,drop_in)
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
            if (int(crc) < 10) or (line[1]=='172.16.0.202' and (line[3]=='Gi1/0/45' or line[3]=='Gi1/0/46')) or (line[1]=='172.16.130.130' and line[3]=='Fa0/7') or (line[1]=='172.16.229.1' and line[3]=='Gi2/8'): # убрать из оповещения порты, которые никак не починить или ошибки на которых не влияют на работу
                continue # если нет значительного прироста ошибок crc за последние сутки на определенном порту определенного оборудования, то переходим к проверке следующего порта
            else:
                result = result + '''{:<20} {:<15} {:<10} {:<30} {:<10} {:<10} {:<10}\n'''.format(line[0], line[1], line[3], line[4], crc, drop_out, drop_in)
                total += 1
        except Error as e:
            with open('crc_log/log_db_oos.txt', 'a') as f:
                f.write('{}:{}\n'.format(date_today, e))

    return result,total

def mail_old(result):
    HOST = "spb-mail.spb.rsvo.local"
    SUBJECT = "CRC/Output dropped packets/Input dropped packets for last 24h"
    TO = "vsemenova@spb.rsvo.ru"
    FROM = "admin@spb.rsvo.ru"
    text = result
    BODY = "\r\n".join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT ,
        "",
        text))
    server = smtplib.SMTP(HOST)
    try:
        server.sendmail(FROM, [TO], BODY)
    finally:
        server.quit()

def mail(result):
    msg = MIMEMultipart()                               # Создаем сообщение
    msg['From']    = "admin@spb.rsvo.ru"
    msg['To']      = "admin@spb.rsvo.ru"
    msg['Subject'] = Header('CRC/Output dropped packets/Input dropped packets for last 24h', 'utf-8')
    msg.attach(MIMEText(result, 'plain','utf-8'))
    server = smtplib.SMTP('192.168.21.209')           # Создаем объект SMTP
    server.send_message(msg)                            # Отправляем сообщение
    server.quit()

if __name__ == '__main__':
    db_file = 'oos.db'
    date_today = date.today().strftime('%Y_%m_%d')
    conn = create_connection(db_file)
    data_today = get_data_today(conn, date_today)
    difference_24h = get_difference(conn,1) # tuple(result,total) разница между текущим и предыдущим днем, чтобы определить растут crc/drop
    conn.close()

    if difference_24h[1] > 0: # присутствует хотя бы 1 запись о приросте ошибок за последние сутки 
        start = '''Прирост ошибок CRC/Output dropped packets/Input dropped packets на портах оборудования Cisco за последние 24 часа, если количество ошибок crc увеличилось более, чем на 10:\n\n{:<15} {:<15} {:<10} {:<30} {:<10} {:<10} {:<10}\n{}\n'''.format('name', 'ip_address', 'port', 'port_description', 'crc', 'drop_out', 'drop_in','-'*100)
        end = '-'*100 + '\n' + 'Total:{}'.format(difference_24h[1])
        result = start+difference_24h[0]+end
        mail(result)
    else:
        result='За последние 24 часа ошибок CRC не наблюдалось'
        mail(result)
