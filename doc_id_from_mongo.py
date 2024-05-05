from pymongo import MongoClient
from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME

my_client = MongoClient()
my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))


def doc_id_dispatcher():
    collection = my_client["DOC_SCAN"]
    doc_id = collection['DOCUMENT_ID']
    t = doc_id.find_one()
    ret = t["doc_id"]

    doc_id.update_one({'doc_id': ret}, {'$set': {'doc_id': ret + 1}})
    return ret







