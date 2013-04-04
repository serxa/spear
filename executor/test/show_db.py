#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from sys import argv, exit
import sqlite3

conn = sqlite3.connect('../executor.sqlite')
c = conn.cursor()

rows = c.execute('''SELECT * FROM processes;''')
for r in rows:
    print r

conn.close()

