import cx_Oracle
import pandas as pd
from pymongo import MongoClient
import multiprocessing
import time
from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME, dsn_tns


def clone_mongo():
    while True:
        time.sleep(3)
        my_client = MongoClient(connect=False)
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc_id = collection['AUTH']
        doc_id.drop()
        time.sleep(1.5)
        cursor = dsn_tns.cursor()

        query = "select cdr.api_users.username , cdr.api_users.password  from cdr.api_users"

        for row in cursor.execute(query):
            df = pd.DataFrame(row, index=["USERNAME", "PASSWORD"], )
            # print(df)
            result = {
                "USERNAME": df.iloc[0][0],
                "PASSWORD": df.iloc[1][0]
            }
            doc_id.insert_one(result)


def initiate_mongo_devil():
    cm = multiprocessing.Process(target=clone_mongo, daemon=True)
    cm.start()
