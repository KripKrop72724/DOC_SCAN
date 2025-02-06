import cx_Oracle

DB_URL = 'mongodb://%s:%s@172.29.97.25:27017'
DB_USERNAME = 'docscantest'
DB_PASSWORD = 'mechanism_123'


dsn_tns = cx_Oracle.connect('ASAD_25510/asad#123@prodhims.shifa.com.pk:1521/himsdb.shifa.com.pk')