#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

html_1 = '''Content-type: text/html; charset=utf-8

    <head>
    <link href="../style.css" rel="stylesheet">
    <link rel="icon" href="../favicon.ico" type="image/x-icon">
    <title>CRC</title>
    </head>
    <body>
        <h1><img width="90" src="../logo_rsvo.png" alt="home page" border="0"></a>CRC & Output/Input dropped packets</h1>
        <p>Чтобы посмотреть статистику за определенное количество дней для определенного порта оборудования, воспользуйтесь следующей формой:</p>
        <br>
        <form action="crc_statistic_port.py" method="get" class="Form">
        <table>
        <tr>
            <td><b>ip address:</b></td>
            <td><input type="text" name="address" required></td>
        </tr>
        <tr>
            <td><b>port:</b></td>
            <td><select name="port_type">
                <option value="Gi">Gi</option>
                <option value="Fa">Fa</option>
                <option value="Te">Te</option>
                </select>
            <input type="text" name="port_number" value="0/1" required</td>
        </tr>
        <tr>
            <td><b>количество дней:</b></td>
            <td><input type="text" name="days" value="10" required></td>
        </tr>
        </table>
        <input type="submit" value="Получить статистику" class="button-link">
        </form>
        <br><br>
        '''
html_2 = '''
    <p>Чтобы посмотреть значения CRC/Output dropped packets/Input dropped packets на портах всех устройств cisco за последние 24 часа с 00:00 часов предыдущего дня до 00:00 часов сегодняшнего дня, нажмите на кнопку ниже:</p>
    <br>
    <a class="button-link" href="crc_statistic_all_24h.py"
    target="_parent">Получить статистику</a>
    <br><br><hr>
    '''
html_end = '''
    </body>
        '''

