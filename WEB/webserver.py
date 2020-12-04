#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Реализует веб-сервер на языке Python, способный обслуживать
страницы HTML и запускать серверные CGI-сценарии на языке Python;
этот сервер непригоден для промышленной эксплуатации (например, он
не поддерживает протокол HTTPS, медленно запускает/выполняет сценарии
на некоторых платформах).
GI-сценарии на языке Python должны сохраняться в подкаталоге cgi-bin;
на одном и том же компьютере может быть запущено несколько
серверов для обслуживания различных каталогов при условии, что они
прослушивают разные порты;
"""
import os, sys
from http.server import HTTPServer, CGIHTTPRequestHandler

webdir = '/home/semenova/OOS/WEB' # каталог с файлами HTML и подкаталогом cgi-bin для сценариев
port = 8080 # http://servername/ если 8080, иначе http://servername:xxxx/

if len(sys.argv) > 1: webdir = sys.argv[1] # аргументы командной строки
if len(sys.argv) > 2: port = int(sys.argv[2]) # иначе по умолчанию ., 8080
print('webdir "%s", port %s' % (webdir, port))
os.chdir(webdir) # перейти в корневой веб-каталог
srvraddr = ('', port) # имя хоста, номер порта
srvrobj = HTTPServer(srvraddr, CGIHTTPRequestHandler)
srvrobj.serve_forever() # обслуживать клиентов до завершения
