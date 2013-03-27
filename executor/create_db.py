#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from sys import argv, exit
import sqlite3

import settings

def table_exists(cursor, table_name):
    return cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?;
            ''', (table_name, ))

conn = sqlite3.connect(settings.DATABASE_FILE)
c = conn.cursor()

if table_exists(c, 'processes') and not '-f' in argv:
    print 'Table "processes" already exists. Add "-f" flag to drop and recreate it.'
else:
    c.execute('''DROP TABLE IF EXISTS processes;''')
    c.execute('''
            CREATE TABLE processes (
                tid         INTEGER,
                status      INTEGER,
                queue_type  TEXT   ,
                pid         INTEGER,
                pgid        INTEGER,
                exitstatus  INTEGER,
                workdir     TEXT   ,
                executable  TEXT   ,
                args        TEXT   ,
                queue_conf  TEXT   ,
                stdin       TEXT   , /* maybe BLOB? */
                stdout      TEXT   ,
                lversion    INTEGER,
                gversion    INTEGER
            );
            ''')
    conn.commit()

conn.close()

