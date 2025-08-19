from pymongo import MongoClient
import base64
import pytesseract

from oracle_apis import check_mortality
from weak_classifier import classify
import os
import multiprocessing
import json
import bson
import base64
from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME

pytesseract.pytesseract.tesseract_cmd = 'D:\\Tesseract-OCR\\tesseract.exe'


def get_multi_vector_single_using_te():
    my_client = MongoClient(connect=False)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    df = collection['DOCUMENTS']
    q = df.find({"ocr": None})
    # for i in q:
    #     df.update_one({"ocr": None}, {"$set": {"ocr": ""}})
    for j in q:
        img = j["doc"]
        mongo_id = j["_id"]
        name = str(j["doc_id"]) + ".jpg"
        f = open(name, 'wb')
        f.write(img)
        f.close()
        df.update_one({'_id': mongo_id}, {"$set": {"class": classify(name)}}, upsert=True)
        os.remove(name)
        if j['class'] == "BED SIDE PROCEDURE" or j['class'] == j['class'] == "TRIAGE DOCUMENT" or j[
            'class'] == "Pediatric Early Warning Score" or j['class'] == "NEUROLOGICAL ASSESSMENT" or j[
            'class'] == "INITIAL NURSING ASSESSMENT" or j['class'] == "GRAPHICAL ASSESSMENT" or j[
            'class'] == "GRAPHIC CHART" or j['class'] == "MODIFIED GLASGOW COMA SCALE":
            df.update_one({'_id': mongo_id}, {"$set": {"main_type": "EMERGENCY DOCUMENTS"}}, upsert=True)
        elif j['class'] == "OLD FACE SHEET" or j['class'] == "CONSENT FORM" or j['class'] == "FACE SHEET":
            df.update_one({'_id': mongo_id}, {"$set": {"main_type": "PATIENT INFORMATION AND CONSENT"}}, upsert=True)
        elif j['class'] is None:
            df.update_one({'_id': mongo_id}, {"$set": {"main_type": "NO"}}, upsert=True)
        else:
            df.update_one({'_id': mongo_id}, {"$set": {"main_type": "PATIENT HISTORY"}}, upsert=True)


def initiate_tes_devil():
    tm = multiprocessing.Process(target=get_multi_vector_single_using_te, daemon=True)
    tm.start()


def looper():
    while True:
        get_multi_vector_single_using_te()


def get_by_mr(mrno, type):
    return_obj = []
    my_client = MongoClient(connect=False)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    df = collection['DOCUMENTS']
    return_obj = []
    if type == "XXQ01":
        q = df.find({"class": "BED SIDE PROCEDURE", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ02":
        q = df.find({"class": "MODIFIED GLASGOW COMA SCALE", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ03":
        q = df.find({"class": "INITIAL NURSING ASSESSMENT", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ04":
        q = df.find({"class": "PEWS", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ05":
        q = df.find({"class": "GRAPHICAL ASSESSMENT", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ06":
        q = df.find({"class": "GRAPHICAL CHART", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ07":
        q = df.find({"class": "NEUROLOGICAL ASSESSMENT", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ08":
        q = df.find({"class": "TRIAGE DOCUMENT", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ09":
        q = df.find({"class": "AUTHORIZATION AND CONSENT FORM", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ10":
        q = df.find({"class": "FACE SHEET", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ11":
        q = df.find({"class": "PATIENT MEDICAL RECORD", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ12":
        q = df.find({"class": "PATIENT REGISTRATION FORM", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ13":
        q = df.find({"class": "HISTORY AND PHYSICAL", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ14":
        q = df.find({"class": "NURSING ASSESSMENT", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj
    elif type == "XXQ15":
        q = df.find({"class": "PHYSICIAN PROGRESS RECORD", "mrno": str(mrno)})
        for j in q:
            img = j["doc"]
            return_obj.append({"base64": img})
            return return_obj


def get_images_viewer_op(mr, date, doc_id):
    bsp = []
    tds = []
    pewss = []
    nas = []
    inas = []
    gas = []
    gcs = []
    mgcss = []

    ofcs = []
    cfs = []
    fcs = []
    my_client = MongoClient(connect=False)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    df = collection['DOCUMENTS']
    bp = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id, "class": "BED SIDE PROCEDURE"})
    for i in bp:
        bsp.append({"base64": str(bp["doc"])})
    td = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "TRIAGE DOCUMENT"})
    for i in td:
        tds.append({"base64": str(bp["doc"])})
    pews = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                    "class": "Pediatric Early Warning Score"})
    for i in pews:
        pewss.append({"base64": str(bp["doc"])})
    na = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "NEUROLOGICAL ASSESSMENT"})
    for i in na:
        nas.append({"base64": str(bp["doc"])})
    ina = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                   "class": "INITIAL NURSING ASSESSMENT"})
    for i in ina:
        inas.append({"base64": str(bp["doc"])})
    ga = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "GRAPHICAL ASSESSMENT"})
    for i in ga:
        gas.append({"base64": str(bp["doc"])})
    gc = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "GRAPHIC CHART"})
    for i in gc:
        gcs.append({"base64": str(bp["doc"])})
    mgcs = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                    "class": "MODIFIED GLASGOW COMA SCALE"})
    for i in mgcs:
        mgcss.append({"base64": str(bp["doc"])})
    ofc = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                   "class": "OLD FACE SHEET"})
    for i in ofc:
        ofcs.append({"base64": str(bp["doc"])})
    cf = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "CONSENT FORM"})
    for i in cf:
        cfs.append({"base64": str(bp["doc"])})
    fc = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "FACE SHEET"})
    for i in fc:
        fcs.append({"base64": str(bp["doc"])})
    fc = df.find({"mrno": mr, "visit_date_op": date, "doctor_id_ip": doc_id,
                  "class": "FACE SHEET"})
    for i in fc:
        fcs.append({"base64": str(bp["doc"])})

    returning_object = {
        {
            "name": "EMERGENCY DOCUMENTS",
            "id": "XXXQ01",
            "TRIAGE DOCUMENT": tds,
            "Pediatric Early Warning Score": pewss,
            "NEUROLOGICAL ASSESSMENT": nas,
            "INITIAL NURSING ASSESSMENT": inas,
            "GRAPHICAL ASSESSMENT": gas,
            "GRAPHIC CHART": gcs,
            "MODIFIED GLASGOW COMA SCALE": mgcss,
        },
        {
            "name": "EMERGENCY DOCUMENTS",
            "id": "XXXQ02",
            "OLD FACE SHEET": ofcs,
            "CONSENT FORM": cfs,
            "FACE SHEET": fcs
        }
    }
    return returning_object


def bring_users_data():
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']
    cursor = doc_id.find({}, {
        '_id': False,
        'PASSWORD': False,
        'password_changed': False,
        'total_images_scanned': False,
    })
    data = []
    for document in cursor:
        # Ensure that both keys exist, defaulting to False if missing.
        if 'is_ot_scanner' not in document:
            document['is_ot_scanner'] = False
        if 'is_ot_viewer' not in document:
            document['is_ot_viewer'] = False
        data.append(document)
    res = {
        "data": data,
        "status": 1,
        "msg": "Success"
    }
    return res


# def bulk_viewer(mr_no):
#     mr = mr_no
#     my_client = MongoClient()
#     my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD),
#                             unicode_decode_error_handler='ignore')
#     collection = my_client["DOC_SCAN"]
#     doc_id = collection['AUTH']
#     doc = collection['DOCUMENTS']
#     cur = doc.find({"mrno": mr})
#     a0 = []
#     a1 = []
#     a2 = []
#     a3 = []
#     a4 = []
#     a5 = []
#     a6 = []
#     a7 = []
#     a8 = []
#     a9 = []
#     a10 = []
#     a11 = []
#     a12 = []
#     a14 = []
#     a15 = []
#     a16 = []
#     obj = {
#         "data": [],
#         "status": 200,
#         "message": "Success"
#     }
#     for document in cur:
#         if not document['is_del']:
#             if document['class'] == '1':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a0.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '2':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a1.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '3':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a2.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '4':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a3.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '5':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a4.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '6':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a5.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '7':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a6.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '8':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a7.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '9':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a8.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '10':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a9.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '11':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a10.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '12':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a11.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '13':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a12.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '0':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a14.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '14':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a15.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#             elif document['class'] == '15':
#                 img = document['doc']
#                 f = open("tmp.jpg", "wb")
#                 f.write(img)
#                 f.close()
#                 with open("tmp.jpg", "rb") as image_file:
#                     encoded_string = base64.b64encode(image_file.read())
#                 a16.append({'base64': encoded_string.decode('utf-8'), 'id': document['doc_id']})
#                 os.remove('tmp.jpg')
#         obj = {
#             "data": [{
#                 "id": 1,
#                 "image": a0
#             },
#                 {
#                     "id": 2,
#                     "image": a1
#                 },
#                 {
#                     "id": 3,
#                     "image": a2
#                 },
#                 {
#                     "id": 4,
#                     "image": a3
#                 },
#                 {
#                     "id": 5,
#                     "image": a4
#                 },
#                 {
#                     "id": 6,
#                     "image": a5
#                 },
#                 {
#                     "id": 7,
#                     "image": a6
#                 },
#                 {
#                     "id": 8,
#                     "image": a7
#                 },
#                 {
#                     "id": 9,
#                     "image": a8
#                 },
#                 {
#                     "id": 10,
#                     "image": a9
#                 },
#                 {
#                     "id": 11,
#                     "image": a10
#                 },
#                 {
#                     "id": 12,
#                     "image": a11
#                 },
#                 {
#                     "id": 13,
#                     "image": a12
#                 },
#                 {
#                     "id": 0,
#                     "image": a14
#                 },
#                 {
#                     "id": 14,
#                     "image": a15
#                 }
#             ],
#             "status": 200,
#             "message": "Success"
#         }
#     return obj

def bulk_viewer(mr_no):
    my_client = MongoClient()
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD),
                            unicode_decode_error_handler='ignore')
    collection = my_client["DOC_SCAN"]
    doc = collection['DOCUMENTS']
    cur = doc.find({"mrno": mr_no}, {"doc_id": 1, "class": 1, "thumb": 1, "is_del": 1})

    class_images = {str(i): [] for i in range(16)}  # Initialize lists for each class

    for document in cur:
        if not document['is_del']:
            class_key = str(document['class'])
            thumb_data = document['thumb']
            if isinstance(thumb_data, bytes):
                thumb_data = base64.b64encode(thumb_data).decode('utf-8')
            class_images[class_key].append({'base64': thumb_data, 'id': document['doc_id']})

    obj = {
        "data": [{"id": int(key), "image": value} for key, value in class_images.items()],
        "status": 200,
        "message": "Success"
    }
    return obj


# def image_count_with_class_names(mr_no):
#     # Establish MongoDB connection
#     my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD),
#                             unicode_decode_error_handler='ignore')
#     collection = my_client["DOC_SCAN"]
#     doc = collection['DOCUMENTS']
#
#     # Query the database for the MRNO and count the documents
#     image_count = doc.count_documents({"mrno": mr_no, "is_del": False})
#
#     # The object you want to update with the image count
#     output_object = {
#         "image_count": image_count,
#         "classes": [
#             {"name": "Admission Orders", "id": 1},
#             {"name": "Face Sheet", "id": 13},
#             {"name": "Authorization And Consent", "id": 2},
#             {"name": "History and Physical Examination", "id": 7},
#             {"name": "Natal", "id": 9},
#             {"name": "Operative Notes", "id": 3},
#             {"name": "Orthopedic Notes", "id": 11},
#             {"name": "Ophthalmologic Assessment", "id": 10},
#             {"name": "Discharge Summary", "id": 4},
#             {"name": "Physician Progress Record", "id": 5},
#             {"name": "Emergency Room", "id": 6},
#             {"name": "Maternity Notes", "id": 8},
#             {"name": "PEADS History", "id": 12},
#             {"name": "Personalized Document", "id": 14},
#             {"name": "Unclassified", "id": 0}
#         ]
#     }
#
#     return output_object
def image_count_with_class_names(filter_criteria):
    """
    Fetch image count and class details based on filter criteria.
    Documents with class "0" (as a string) are remapped to class 15 ("Unclassified").
    Optimized with MongoDB indexing for faster query execution.
    Detailed print statements are added for debugging.
    """
    try:
        print("Establishing MongoDB connection...")
        my_client = MongoClient(
            DB_URL % (DB_USERNAME, DB_PASSWORD),
            unicode_decode_error_handler='ignore'
        )
        collection = my_client["DOC_SCAN"]
        doc = collection['DOCUMENTS']

        # Prepare the query filter
        print("Preparing query filter based on provided filter_criteria...")
        print(f"Input filter_criteria: {filter_criteria}")
        has_mrt = False
        query_filter = {"is_del": False}
        if filter_criteria.get("mrno"):
            query_filter["mrno"] = filter_criteria["mrno"]
            print(f"Adding mrno filter: {filter_criteria['mrno']}")
            has_mrt = check_mortality(query_filter["mrno"])
            print(f"Mortality check for mrno {filter_criteria['mrno']} returned: {has_mrt}")
        if filter_criteria.get("admission_id"):
            query_filter["admission_id"] = filter_criteria["admission_id"]
            print(f"Adding admission_id filter: {filter_criteria['admission_id']}")
        if filter_criteria.get("visit_id_op"):
            query_filter["visit_id_op"] = filter_criteria["visit_id_op"]
            print(f"Adding visit_id_op filter: {filter_criteria['visit_id_op']}")

        print("Final query filter to be used in MongoDB query:")
        print(query_filter)

        # Count total images based on the filter
        image_count = doc.count_documents(query_filter)
        print(f"Total image count for the given filter: {image_count}")

        # Aggregate to count images per class, remapping class "0" to 15 (Unclassified)
        print("Starting aggregation to count images per class, remapping class '0' to 15 (Unclassified)...")
        pipeline = [
            {"$match": query_filter},
            {"$project": {
                "class": {
                    "$cond": {
                        "if": {"$eq": ["$class", "0"]},  # check if class equals string "0"
                        "then": 15,
                        "else": "$class"
                    }
                }
            }},
            {"$group": {"_id": "$class", "count": {"$sum": 1}}}
        ]
        class_counts = list(doc.aggregate(pipeline))
        print("Aggregation complete. Raw class counts:")
        print(class_counts)

        # Create a dictionary for quick class ID to count mapping
        class_count_dict = {str(item['_id']): item['count'] for item in class_counts}
        print("Constructed class_count_dict from aggregation:")
        print(class_count_dict)

        # Define class details (make sure the default "Unclassified" id is 15)
        classes = [
            {"name": "Admission Orders", "id": 1},
            {"name": "Face Sheet", "id": 13},
            {"name": "Authorization And Consent", "id": 2},
            {"name": "History and Physical Examination", "id": 7},
            {"name": "Natal", "id": 9},
            {"name": "Operative Notes", "id": 3},
            {"name": "Orthopedic Notes", "id": 11},
            {"name": "Ophthalmologic Assessment", "id": 10},
            {"name": "Discharge Summary", "id": 4},
            {"name": "Physician Progress Record", "id": 5},
            {"name": "Emergency Room", "id": 6},
            {"name": "Maternity Notes", "id": 8},
            {"name": "PEADS History", "id": 12},
            {"name": "Personalized Document", "id": 14},
            {"name": "Anesthesia Documents", "id": 16},
            {"name": "Unclassified", "id": 15}
        ]
        print("Defined class details (expected class IDs and names):")
        for cls in classes:
            print(f"  Class: {cls['name']} (ID: {cls['id']})")

        # Add image counts to each class based on the mapping
        print("Mapping aggregated counts to predefined classes...")
        for cls in classes:
            cls_id_str = str(cls['id'])
            cls['image_count'] = class_count_dict.get(cls_id_str, 0)
            print(f"  Class {cls['name']} (ID: {cls['id']}) has image_count: {cls['image_count']}")

        # Prepare the output object
        output_object = {
            "image_count": image_count,
            "mrt": has_mrt,
            "classes": classes
        }
        print("Final output object prepared:")
        print(output_object)

        return output_object

    except Exception as e:
        # Log the error for debugging
        print(f"Error in image_count_with_class_names: {e}")
        return {
            "error": "An error occurred while processing the request",
            "details": str(e)
        }


def get_images_by_class_doc(mr_no=None, class_filter=None, admission_id=None, visit_id_op=None):
    """
    Retrieve images filtered by mrno, admission_id, visit_id_op, and class.
    If class_filter is 15, include documents with class "15" or class "0".
    Additionally, when mr_no is provided, the query will only return documents
    where is_bulk is True.
    Optimized with MongoDB indexing for faster query execution.
    """
    try:
        # Connect to MongoDB
        my_client = MongoClient(
            DB_URL % (DB_USERNAME, DB_PASSWORD),
            unicode_decode_error_handler='ignore'
        )
        collection = my_client["DOC_SCAN"]
        doc = collection['DOCUMENTS']

        # Construct query filter dynamically
        query_filter = {"is_del": False}
        if mr_no:
            query_filter["mrno"] = mr_no
            query_filter["is_bulk"] = True  # Apply is_bulk filter when mr_no is provided
        if admission_id:
            query_filter["admission_id"] = admission_id
        if visit_id_op:
            query_filter["visit_id_op"] = visit_id_op

        if class_filter:
            # If the class filter is 15, include documents where class is either "15" or "0"
            if str(class_filter) == "15":
                query_filter["$or"] = [{"class": "15"}, {"class": "0"}]
            else:
                query_filter["class"] = class_filter

        # Use MongoDB cursor with projection
        cur = doc.find(query_filter, {"doc_id": 1, "doc": 1}).batch_size(100)

        # Process results
        images = []
        for document in cur:
            img_data = document['doc']
            if isinstance(img_data, bytes):
                img_data = base64.b64encode(img_data).decode('utf-8')
            images.append({'base64': img_data, 'id': document['doc_id']})

        return {
            "data": [{"id": class_filter or "all", "image": images}],
            "status": 200,
            "message": "Success"
        }

    except Exception as e:
        # Log and return error response
        print(f"Error in get_images_by_class_doc: {e}")
        return {
            "data": [],
            "status": 500,
            "message": "An error occurred while processing the request.",
            "error": str(e)
        }



# def get_images_by_class_thumb(mr_no, class_filter):
#     my_client = MongoClient()
#     my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD),
#                             unicode_decode_error_handler='ignore')
#     collection = my_client["DOC_SCAN"]
#     doc = collection['DOCUMENTS']
#     cur = doc.find({"mrno": mr_no, "class": class_filter, "is_del": False}, {"doc_id": 1, "thumb": 1})
#
#     images = []
#     for document in cur:
#         thumb_data = document['thumb']
#         if isinstance(thumb_data, bytes):
#             thumb_data = base64.b64encode(thumb_data).decode('utf-8')
#         images.append({'base64': thumb_data, 'id': document['doc_id']})
#
#     return {
#         "data": [{"id": class_filter, "image": images}],
#         "status": 200,
#         "message": "Success"
#     }
def get_images_by_class_thumb_with_count(mr_no):
    # MongoDB connection
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD), unicode_decode_error_handler='ignore')
    collection = my_client["DOC_SCAN"]
    doc = collection['DOCUMENTS']

    # Aggregate to group by class and count the documents
    pipeline = [
        {"$match": {"mrno": mr_no, "is_del": False}},  # Filter by mrno and is_del
        {"$group": {"_id": "$class", "count": {"$sum": 1}, "thumbs": {"$push": "$thumb"}}},
        # Group by class and count, also collect thumbs
    ]
    aggregate_result = doc.aggregate(pipeline)

    # Formatting the result
    result = []
    for item in aggregate_result:
        images = []
        for thumb_data in item['thumbs']:
            if isinstance(thumb_data, bytes):
                thumb_data = base64.b64encode(thumb_data).decode('utf-8')
            images.append({'base64': thumb_data})

        result.append({
            "id": item['_id'],
            "count": item['count'],
            "images": images
        })

    return {
        "data": result,
        "status": 200,
        "message": "Success"
    }


def soft_del(doc_idd, eid):
    my_client = MongoClient()
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))

    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    doc_to_del = collection.update_one({"doc_id": doc_idd}, {"$set": {"is_del": True,
                                                                      "del_by": str(eid)
                                                                      }})


def soft_del_rev(doc_idd):
    my_client = MongoClient()
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))

    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    doc_to_del = collection.update_one({"doc_id": doc_idd}, {"$set": {"is_del": False,
                                                                      "del_by": ''
                                                                      }})


def mrn_checker(mrn):
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    print(mrn)
    if collection.count_documents({"mrno": mrn, "is_del": False}) > 0:
        return True
    else:
        return False


def class_changer_dumb(img_id, class_num):
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    cur = collection.find({"doc_id": int(img_id)})
    # for document in cur:
    #     print(document)
    #     document["class"] = {}
    collection.update_one({"doc_id": {"$gte": int(img_id)}}, {"$set": {"class": str(class_num)}})


def class_changer_dumb_bulk(img_id_lis, class_num, changed_by_id):
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    for each in img_id_lis:
        collection.update_one({"doc_id": {"$gte": int(each)}},
                              {"$set": {"class": str(class_num), "rc_by_id": str(changed_by_id)}})
    # for document in cur:
    #     print(document)
    #     document["class"] = {}


def get_all_unclassified():
    ret = []
    cnt = 0
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    cur = collection.find({"class": {"$eq": "0"}})
    for each in cur:
        cnt = cnt + 1
        img = each['doc']
        f = open("tmp.jpg", "wb")
        f.write(img)
        f.close()
        with open("tmp.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        obj = {
            "id": each['doc_id'],
            "mr": each['mrno'],
            "image": encoded_string.decode('utf-8')
        }
        os.remove("tmp.jpg")
        ret.append(obj)
        if cnt == 100:
            break
    return ret


def get_all_recycled(show, page):
    ret = []
    skipper = (page - 1) * show
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    cur = collection.find({"class": {"$eq": "15"}}).skip(skipper).limit(show)
    for each in cur:
        img = each['doc']
        f = open("tmp.jpg", "wb")
        f.write(img)
        f.close()
        with open("tmp.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
        obj = {
            "id": each['doc_id'],
            "mr": each['mrno'],
            "image": encoded_string.decode('utf-8')
        }
        os.remove("tmp.jpg")
        ret.append(obj)
    return ret


def get_recycled_count():
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    cur = collection.count_documents({"class": {"$eq": "15"}})
    return int(cur)


def get_unclassified_count():
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    db = my_client["DOC_SCAN"]
    collection = db['DOCUMENTS']
    cur = collection.count_documents({"class": {"$eq": "0"}})
    return int(cur)


if __name__ == '__main__':
    print(bulk_viewer("730611"))
