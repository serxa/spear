#-*- encoding: utf-8 -*-

"""Very simple ORM wrapper on top of sqlite3"""

import logging
import sqlite3

class Process(object):
    STATUS_STARTING = 1
    STATUS_WAITING  = 2
    STATUS_RUNNING  = 3
    STATUS_ENDING   = 4
    STATUS_STOPPED  = 5
    _table = None
    def to_array(self):
        return self._table._r2a(self)
    def to_dict(self):
        return self._table._r2d(self)

class ProcessesTable(object):
    """A class representing a table within database"""

    # Name of database table
    TABLE = 'processes'
    # Name of primary key field
    PK = 'tid'
    # Name of class representing row
    ROWCLASS = Process

    def __init__(self, dbfile):
        self.log = logging.getLogger('db')
        self.log.debug('Initializing database connection to file %s', dbfile)
        self.database = sqlite3.connect(dbfile)
        self._create_table_if_not_exists()
        self._dbversion = self.execute('''PRAGMA user_version;''').fetchone()[0]
        self._fields = [i[1] for i in self.execute('''PRAGMA table_info(@table);''')]
        self.commit()
        self.log.debug('Database succesfully connected, user_version = %d', self._dbversion)

    def _create_table_if_not_exists(self):
        """Initialize database structure"""
        c = self.execute('''
                CREATE TABLE IF NOT EXISTS @table (
                    tid         INTEGER UNIQUE NOT NULL,
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
                    stderr      TEXT   ,
                    lversion    INTEGER,
                    gversion    INTEGER
                );
                ''')
        self.execute('''PRAGMA user_version = 1;''')

    def _a2r(self, data):
        """Array to row"""
        row = self.ROWCLASS()
        row._table = self
        for (f,v) in zip(self._fields, data):
            setattr(row, f, v)
        return row
    def _n2r(self):
        """None to row"""
        row = self.ROWCLASS()
        row._table = self
        for f in self._fields:
            setattr(row, f, None)
        return row
    def _r2a(self, row):
        """Row to array"""
        return [getattr(row, f) for f in self._fields]
    def _a2d(self, data):
        """Array to dict"""
        d = dict()
        for (f,v) in zip(self._fields, data):
            d[f] = v
        return d
    def _r2d(self, row):
        """Row to dict"""
        d = dict()
        for f in self._fields:
            d[f] = getattr(row, f)
        return d

    def new_row(self):
        return self._n2r()
    def insert(self, row):
        query = '''INSERT INTO @table VALUES ( {0} );'''.format(
                ' , '.join('?'*len(self._fields)),
                )
        self.execute(query, self._r2a(row))
        self.commit()
    def update(self, row):
        query = '''UPDATE @table SET {0} WHERE @pk = ?;'''.format(
                ' , '.join('{0} = ?'.format(i) for i in self._fields if i != self.PK),
                )
        self.execute(query, self._r2a(row)[1:] + [getattr(row,self.PK)])
        self.commit()
    def get(self, key):
        query = '''SELECT * FROM @table WHERE @pk = ?;'''
        data = self.execute(query, (key,)).fetchone()
        if data is None:
            raise KeyError('TID not found')
        return self._a2r(data)
    def execute(self, query, args = []):
        q = query.replace('@table', self.TABLE).replace('@pk', self.PK)
        self.log.info('Executing %s with %s', q, str(args))
        return self.database.execute(q, args)
    def commit(self):
        self.log.info('Comitting')
        self.database.commit()

