#-*- encoding: utf-8 -*-

EID = -1
EID_DOC = 'Executor installation ID'
LOG_FILE = 'executor.log'
LOG_FILE_DOC = 'File to write log to'
LOG_LEVEL = 'DEBUG'
LOG_LEVEL_DOC = 'Log level. Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL'

HOST_NAME = 'localhost'
HOST_NAME_DOC = 'Local host name'
PORT_NUMBER = 8042
PORT_NUMBER_DOC = 'Port number to listen on'
CERTFILE = 'test_cert.pem'
CERTFILE_DOC = 'File with SSL certificate to use'

SERVER_HOST = 'localhost'
SERVER_HOST_DOC = 'Heartbeat server'
SERVER_PORT = 8013
SERVER_PORT_DOC = 'Heartbeat server port'
CONNECTION_TIMEOUT = 5 # Seconds
CONNECTION_TIMEOUT_DOC = 'Timeout on connection to heartbeat server'
HEARTBEAT_INTERVAL = 60 # Seconds
HEARTBEAT_INTERVAL_DOC = 'How often to send heartbeats'

DATABASE_FILE = 'executor.sqlite'
DATABASE_FILE_DOC = 'File with processes database'

