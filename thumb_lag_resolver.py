# use this to autonomously resolve thumb gap

import base64
import jpg_compress_mechanisms
from PIL import Image
from pymongo import MongoClient
import shutil

my_client = MongoClient()
my_client = MongoClient('mongodb://%s:%s@10.168.250.250:27017' % ('docscantest', 'mechanism_123'))
collection = my_client["DOC_SCAN"]
doc_id = collection['AUTH']
doc = collection['DOCUMENTS']

cursor = doc.find({"thumb": ""})

for count, document in enumerate(cursor):
    st = "Updating " + str(document['doc_id']) + " which is the " + str(count) + " document."
    print(st)
    img_to_classify = document['doc']
    id_to_classify = document["doc_id"]
    print(id_to_classify)
    f = open(str(id_to_classify) + ".jpg", "wb")
    f.write(img_to_classify)
    f.close()
    try:
        jpg_compress_mechanisms.resize_on_the_go(str(id_to_classify) + ".jpg")
        with open(str(id_to_classify) + ".jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            thumb = encoded_string.decode('utf-8')  # Convert base64 bytes to string
        result = doc.update_one({"doc_id": {"$eq": id_to_classify}}, {"$set": {"thumb": thumb}})
        print(f"Update result: {result.matched_count} matched, {result.modified_count} modified.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    pass

