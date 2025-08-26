import json
import base64
from flask import send_file, Flask, request, make_response, jsonify
from flask_compress import Compress
import Mongo_APIS
from driver_helper import main_scanner_driver, clear_crap
from zipfile import ZipFile
from os.path import basename
from flask_cors import CORS, cross_origin
import time
import jpg_compress_mechanisms
import oracle_apis
from flask_restx import Api, Resource
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient, ReturnDocument
import bcrypt as bc
import clone_server
import doc_id_from_mongo
from PIL import Image
import io
import glob
import os
from weak_classifier import give_classes_data as gd
from Mongo_APIS import get_by_mr as gmr
from pesonal_dash import stats_calculator
from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME
import multiprocessing

compress = Compress()
app = Flask(__name__)
cors = CORS(app)
compress.init_app(app)

api = Api(
    app,
    version='1.0',
    title='DOC_SCAN API',
    description='Interactive documentation for DOC_SCAN service',
    doc='/docs'
)

# Namespaces for grouping endpoints
docscan_ns = api.namespace('docscan', path='/docscan', description='DocScan operations')
ipd_ns = api.namespace('ipd', path='/ipd', description='In-patient operations')
opd_ns = api.namespace('opd', path='/opd', description='Out-patient operations')
bulk_ns = api.namespace('bulk', path='/bulk', description='Bulk upload operations')
mortality_ns = api.namespace('mortality', path='/mortality', description='Mortality bulk operations')
mrd_ns = api.namespace('mrd', path='/mrd', description='MRD operations')
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'zb$@ic^Jg#aywFO1u9%shY7E66Z1cZnO&EK@9e$nwqTrLF#ph1'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)


def login():
    login_details = request.get_json()
    print(login_details)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['AUTH']
    user_from_db = doc_id.find_one({'USERNAME': str(login_details['USERNAME']).upper()})  # search for user in database
    print(user_from_db)
    if user_from_db:
        print("-------------------------------------------------------------------------")
        encrpted_password = login_details['PASSWORD'].encode("utf-8")
        print(encrpted_password)
        print(user_from_db['PASSWORD'])
        if bc.checkpw(encrpted_password, user_from_db['PASSWORD'].encode("utf-8")):
            access_token = create_access_token(identity=user_from_db['USERNAME'])  # create jwt token
            return {
                "access_token": access_token,
                "status": True,
            }, 200, {"Access-Control-Allow-Origin": '*'}

    return {
        'msg': 'The username or password is incorrect',
        "status": False,
    }, 401


def login_rolebase():
    login_details = request.get_json()
    print(login_details)

    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']

    # Retrieve the user document
    user_from_db = doc_id.find_one({'USERNAME': str(login_details['USERNAME']).upper()})
    print(user_from_db)

    # Check if the user exists
    if not user_from_db:
        return {
            'msg': 'Username or password is incorrect',
            "status": False,
        }, 401

    print("-------------------------------------------------------------------------")
    encrypted_password = login_details['PASSWORD'].encode("utf-8")
    print(encrypted_password)
    print(user_from_db['PASSWORD'])

    # Verify the password
    if bc.checkpw(encrypted_password, user_from_db['PASSWORD'].encode("utf-8")):
        # Check if the account is active
        if user_from_db['is_active'] is True:
            access_token = create_access_token(identity=user_from_db['USERNAME'])
            doc_id.update_one(
                {'USERNAME': str(login_details['USERNAME']).upper()},
                {"$set": {"last_login": str(datetime.datetime.now())}}
            )
            return {
                "access_token": access_token,
                "name": user_from_db['name'],
                "is_admin": user_from_db['is_admin'],
                "is_active": user_from_db['is_active'],
                "is_scanner": user_from_db['is_scanner'],
                "is_viewer": user_from_db['is_viewer'],
                "is_ot_scanner": user_from_db.get('is_ot_scanner', False),
                "is_ot_viewer": user_from_db.get('is_ot_viewer', False),
                "last_login": user_from_db['last_login'],
                "last_logout": user_from_db['last_logout'],
                "password_changed": user_from_db['password_changed'],
                "emp_id": user_from_db['emp_id'],
                "email": user_from_db['email'],
                "total_images_scanned": user_from_db['total_images_scanned'],
                "image": user_from_db['image'],
                "status": True,
            }, 200, {"Access-Control-Allow-Origin": '*'}
        else:
            return {
                'msg': 'You have been deactivated by the admin',
                "status": False,
            }, 401
    else:
        return {
            'msg': 'Username or password is incorrect',
            "status": False,
        }, 401


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Access-Control-Allow-Origin')
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def is_anesthesia_user():
    """Check if the current JWT user has anesthesia scanner privileges."""
    try:
        username = get_jwt_identity()
        if not username:
            return False
        client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        user_coll = client["DOC_SCAN"]["VIEWER_AUTH"]
        user_doc = user_coll.find_one({"USERNAME": username})
        return bool(user_doc and user_doc.get("is_anesthesia_scanner"))
    except Exception:
        return False


def route_function_zip():
    os.system("CmdTwain -q C:\\DocScan\\Doc_Scan_Test_Document.jpg")
    time.sleep(0.5)
    jpg_compress_mechanisms.resize_without_loosing_quality()
    with ZipFile('scan_result.zip', 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk("C:\\DocScan"):
            for filename in filenames:
                # create complete filepath of file in directory
                filePath = os.path.join(folderName, filename)
                print(filePath)
                # Add file to zip
                zipObj.write(filePath, basename(filePath))
    clear_crap('C:\\DocScan')
    return send_file("scan_result.zip", as_attachment=True, download_name="scan_result.zip")


def route_function_base():
    route_object = main_scanner_driver()
    return route_object


def welcs():
    return "<h1>WELCOME API'S ARE NOW RUNNING :)<h1>"


@jwt_required()
def Route_Function_Ipd():
    mr = str(request.args.get('mr'))
    route_object = oracle_apis.ipd_patient_details_without_complain(mr)
    return route_object


@jwt_required()
def Route_Function_Ipd_with_date():
    mr = str(request.args.get('mr'))
    date = str(request.args.get('date'))
    route_object = oracle_apis.ipd_patient_details_with_date(date, mr)
    return route_object


@jwt_required()
def Route_Function_Ipd_all_dates():
    mr = request.args.get('mr')
    route_object = oracle_apis.ipd_patient_details_dates_only(mr)
    return route_object


@jwt_required()
def Route_Function_Opd():
    mr = request.args.get('mr')
    route_object = oracle_apis.opd_patient_details(mr)
    return route_object


@jwt_required()
def Route_Function_Opd_all_dates():
    mr = request.args.get('mr')
    route_object = oracle_apis.opd_patient_details_dates_only(mr)
    return route_object


@jwt_required()
def Route_Function_Opd_with_date():
    mr = str(request.args.get('mr'))
    date = str(request.args.get('date'))
    route_object = oracle_apis.opd_patient_details_with_date(date, mr)
    return route_object


@jwt_required()
def Route_Function_Patient_Demographics():
    mr = str(request.args.get('mrno'))
    route_object = oracle_apis.demo(mr)
    return route_object


@jwt_required()
def route_function_upload():
    print("line 1")
    anesthesia = is_anesthesia_user()
    data_to_be_saved = request.get_json()
    # print(data_to_be_saved)
    d = json.dumps(data_to_be_saved)
    print("line 2")
    loaded = json.loads(d)
    print("line 3")
    # print(loaded)
    for i in (loaded["scannedImages"]["scannerImages"]):
        print("line 4")
        # print(i["baseX64"][1:])
        imgdata = base64.b64decode('/' + (i["base64"])[1:])
        print("line 5")
        filename = str(doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)
        im = Image.open(filename)

        image_bytes = io.BytesIO()
        print("original image captured...")
        im.save(image_bytes, format='JPEG')

        doc_value = image_bytes.getvalue()

        jpg_compress_mechanisms.resize_on_the_go(filename)
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            thumb = encoded_string
            # print(thumb)
        print('MAKING THE OBJECT')
        image = {
            'doc_id': int(str(filename).split('.')[0]),
            'doc': image_bytes.getvalue(),
            'mrno': loaded["mrno"],
            'type': loaded["type"],
            'visit_id_op': loaded["visit_id_op"],
            'doctor_id_op': loaded["doctor_id_op"],
            'doctor_speciality_op': loaded.get("doctor_speciality_op"),
            'visit_date_op': loaded["visit_date_op"],
            'admission_id': loaded["admission_id"],
            'admission_date_ip': loaded["admission_date_ip"],
            'complain_ip': loaded["complain_ip"],
            'doctor_id_ip': loaded["doctor_id_ip"],
            'doctor_speciality_ip': loaded["doctor_speciality_ip"],
            'class': 16 if anesthesia else None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,  # this will be an array
            'main_type': None,
            'is_bulk': False,
            'uploaded': True,
            'is_del': False,
            'del_by': '',
            'rc_by_id': None
        }
        # print(image)
        print("Connecting to db")
        my_client = MongoClient()
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc_id = collection['AUTH']
        doc = collection['DOCUMENTS']
        image_id = doc.insert_one(image).inserted_id
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)
    return "saved"


def bulk_saving_function_for_multi_threaded_saving(data_to_be_saved, d, mrt, anesthesia):
    print("line 1")
    # data_to_be_saved = request.get_json()
    # print(data_to_be_saved)
    # d = json.dumps(data_to_be_saved)
    print("line 2")
    loaded = json.loads(d)
    print("line 3")
    # print(loaded)
    for i in (loaded["scannedImages"]["data"]):
        print("line 4")
        # print(i["baseX64"][1:])
        imgdata = base64.b64decode('/' + (i["base64"])[1:])
        print("line 5")
        filename = str(
            doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)
        im = Image.open(filename)

        image_bytes = io.BytesIO()
        print("original image captured...")
        im.save(image_bytes, format='JPEG')

        doc_value = image_bytes.getvalue()
        print(filename)
        print(filename[:-4])
        jpg_compress_mechanisms.resize_on_the_go(filename)
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            thumb = encoded_string
            # print(thumb)
        print('MAKING THE OBJECT')
        image = {
            'doc_id': int(str(filename).split('.')[0]),
            'doc': image_bytes.getvalue(),
            'mrno': loaded["mrno"],
            'class': 16 if anesthesia else None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,  # this will be an array
            'main_type': None,
            'is_bulk': True,
            'uploaded': True,
            'is_del': False,
            'del_by': '',
            'rc_by_id': None,
            'thumb': thumb,
            'mrt': mrt
        }
        # print(image)
        print("Connecting to db")
        my_client = MongoClient()
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc_id = collection['AUTH']
        doc = collection['DOCUMENTS']
        image_id = doc.insert_one(image).inserted_id
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)


@jwt_required()
def route_function_upload_bulk():
    data_to_be_saved = request.get_json()
    d = json.dumps(data_to_be_saved)
    anesthesia = is_anesthesia_user()
    multiprocessing.Process(target=bulk_saving_function_for_multi_threaded_saving,
                            args=(data_to_be_saved, d, False, anesthesia)).start()
    return "saved"


@jwt_required()
def route_function_mrt_upload_bulk():
    data_to_be_saved = request.get_json()
    d = json.dumps(data_to_be_saved)
    anesthesia = is_anesthesia_user()
    multiprocessing.Process(target=bulk_saving_function_for_multi_threaded_saving,
                            args=(data_to_be_saved, d, True, anesthesia)).start()
    return "saved"


@jwt_required()
def route_function_save():
    # Get JSON data directly from the request
    data_to_be_saved = request.get_json()
    loaded = data_to_be_saved  # No need for dumping and loading again
    anesthesia = is_anesthesia_user()
    print(loaded)

    for i in loaded["scannedImages"]["scannerImages"]:
        # Extract the base64 string
        base64_str = i["base64"]
        # Check if it's a data URL and extract the base64 part if so
        if base64_str.startswith("data:"):
            base64_str = base64_str.split(",", 1)[1]
        # Decode the base64 string
        imgdata = base64.b64decode(base64_str)

        # Save the image to a file
        filename = str(doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)

        # Open and process the image
        im = Image.open(filename)
        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

        # Prepare the image document for MongoDB
        image = {
            'doc_id': int(str(filename).split('.')[0]),
            'doc': image_bytes.getvalue(),
            'mrno': loaded["mrno"],
            'type': loaded["type"],
            'visit_id_op': loaded["visit_id_op"],
            'doctor_id_op': loaded["doctor_id_op"],
            'doctor_speciality_op': loaded["doctor_speciality_op"],
            'visit_date_op': loaded["visit_date_op"],
            'admission_id': loaded["admission_id"],
            'admission_date_ip': loaded["admission_date_ip"],
            'complain_ip': loaded["complain_ip"],
            'doctor_id_ip': loaded["doctor_id_ip"],
            'doctor_speciality_ip': loaded["doctor_speciality_ip"],
            'class': 16 if anesthesia else None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,  # this will be an array
            'main_type': None,
            'is_bulk': False,
            'uploaded': False,
            'del_by': '',
            'is_del': False,
            'rc_by_id': None
        }

        # Connect to MongoDB and insert the document
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc = collection['DOCUMENTS']
        image_id = doc.insert_one(image).inserted_id

    # Clean up temporary image files
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)

    return "saved"


def get_mongo_client():
    # Initialize MongoClient only when needed
    return MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD), serverSelectionTimeoutMS=50000)


def doc_id_dispatcher():
    my_client = get_mongo_client()
    collection = my_client["DOC_SCAN"]
    doc_id_collection = collection['DOCUMENT_ID']
    t = doc_id_collection.find_one()
    ret = t["doc_id"]
    doc_id_collection.update_one({'doc_id': ret}, {'$set': {'doc_id': ret + 1}})
    return ret


@jwt_required()
def route_function_bulk_save():
    data_to_be_saved = request.get_json()
    loaded = json.loads(json.dumps(data_to_be_saved))
    anesthesia = is_anesthesia_user()

    for i in loaded["scannedImages"]["scannerImages"]:
        # Remove the prefix before decoding
        base64_data = i["base64"].split(",")[-1]
        imgdata = base64.b64decode(base64_data)
        filename = str(doc_id_dispatcher()) + '.jpg'

        with open(filename, 'wb') as f:
            f.write(imgdata)

        try:
            im = Image.open(filename)
        except IOError:
            print(f"Error: Cannot identify image file {filename}")
            continue  # Skip this image and continue with the next

        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

        image = {
            'doc_id': int(filename.split('.')[0]),
            'doc': image_bytes.getvalue(),
            'mrno': loaded["mrno"],
            'class': 16 if anesthesia else None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,
            'main_type': None,
            'is_bulk': True,
            'del_by': '',
            'is_del': False,
            'rc_by_id': None,
            'mrt': False
        }

        try:
            my_client = get_mongo_client()
            doc_collection = my_client["DOC_SCAN"]['DOCUMENTS']
            image_id = doc_collection.insert_one(image).inserted_id
        except Exception as e:
            print(f"Error inserting document: {e}")
            continue  # Skip this document and continue with the next

    # Remove all jpg files after processing
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)

    return jsonify({"status": "saved"}), 200


@jwt_required()
def route_function_bulk_save_for_mortality():
    data_to_be_saved = request.get_json()
    loaded = json.loads(json.dumps(data_to_be_saved))
    anesthesia = is_anesthesia_user()

    for i in loaded["scannedImages"]["scannerImages"]:
        # Remove the prefix before decoding
        base64_data = i["base64"].split(",")[-1]
        imgdata = base64.b64decode(base64_data)
        filename = str(doc_id_dispatcher()) + '.jpg'

        with open(filename, 'wb') as f:
            f.write(imgdata)

        try:
            im = Image.open(filename)
        except IOError:
            print(f"Error: Cannot identify image file {filename}")
            continue  # Skip this image and continue with the next

        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

        image = {
            'doc_id': int(filename.split('.')[0]),
            'doc': image_bytes.getvalue(),
            'mrno': loaded["mrno"],
            'class': 16 if anesthesia else None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,
            'main_type': None,
            'is_bulk': True,
            'del_by': '',
            'is_del': False,
            'rc_by_id': None,
            'mrt': True
        }

        try:
            my_client = get_mongo_client()
            doc_collection = my_client["DOC_SCAN"]['DOCUMENTS']
            image_id = doc_collection.insert_one(image).inserted_id
        except Exception as e:
            print(f"Error inserting document: {e}")
            continue  # Skip this document and continue with the next

    # Remove all jpg files after processing
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)

    return jsonify({"status": "saved"}), 200


if __name__ == "_main_":
    app.run(debug=True)

if __name__ == "_main_":
    app.run(debug=True)


@jwt_required()
def route_function_bulk_view():
    mr = request.args.get("mrno")
    return Mongo_APIS.bulk_viewer(mr)


@jwt_required()
def route_function_bulk_view_class_doc():
    mr_no = request.args.get("mrno")
    class_filter = request.args.get("class")
    admission_id = request.args.get("admission_id")
    visit_id_op = request.args.get("visit_id_op")

    return Mongo_APIS.get_images_by_class_doc(mr_no, class_filter, admission_id, visit_id_op)


@jwt_required()
def route_function_bulk_view_class_count_based():
    mr = request.args.get("mrno")
    admission_id = request.args.get("admission_id")
    visit_id_op = request.args.get("visit_id_op")

    filter_criteria = {
        "mrno": mr,
        "admission_id": admission_id,
        "visit_id_op": visit_id_op
    }

    # Pass filter_criteria to the function
    return Mongo_APIS.image_count_with_class_names(filter_criteria)

# # @jwt_required()
# def route_function_bulk_view_class_thumb():
#     mr = request.args.get("mrno")
#     class_filter = request.args.get("class")
#     return Mongo_APIS.get_images_by_class_thumb(mr, class_filter)


@jwt_required()
def get_emp_data():
    route_object = oracle_apis.mrd_emp_data()
    return route_object


@jwt_required()
def get_classes():
    route_object = gd()
    return route_object


@jwt_required()
def get_images():
    mrno = str(request.args.get('mr'))
    id = str(request.args.get('id'))
    route_obj = gmr(mrno, id)
    return route_obj


@jwt_required()
def get_mrd_employees():
    route_obj = oracle_apis.mrd_emp_data()
    return route_obj


@jwt_required()
def bring_all_users():
    route_obj = Mongo_APIS.bring_users_data()
    return route_obj


@jwt_required()
def create_scanners():
    # Get the JSON payload
    data_to_be_saved = request.get_json()
    print(data_to_be_saved)

    # Directly use the received JSON data
    loaded = data_to_be_saved

    def parse_bool(value):
        if isinstance(value, bool):
            return value
        return str(value).lower() in ("true", "1", "t", "yes")

    # Extract and convert fields from the input
    name = str(loaded["name"])
    password = "$2a$10$TEYwksLM72v9pgqicMbVuegAMdPrLpD8c0bexVjww/nwyfsyS5krC"  # shifa123 by default
    emp_id = str(loaded["emp_id"])
    is_scanner = parse_bool(loaded.get("is_scanner", False))
    is_viewer = parse_bool(loaded.get("is_viewer", False))
    is_ot_scanner = parse_bool(loaded.get("is_ot_scanner", False))
    is_ot_viewer = parse_bool(loaded.get("is_ot_viewer", False))
    # Optional anesthesia roles
    is_anesthesia_scanner = parse_bool(loaded.get("is_anesthesia_scanner", False))
    is_anesthesia_viewer = parse_bool(loaded.get("is_anesthesia_viewer", False))
    is_admin = False
    email = str(loaded['email'])
    is_active = True
    last_login = ''
    last_logout = ''
    pass_changed = False
    total_images_scanned = 0
    image = str(loaded['image'])

    # Create the document to insert/update in the DB
    ob = {
        'name': name,
        'USERNAME': emp_id,
        'PASSWORD': password,
        'is_admin': is_admin,
        "is_active": is_active,
        "is_scanner": is_scanner,
        "is_viewer": is_viewer,
        "is_ot_scanner": is_ot_scanner,
        "is_ot_viewer": is_ot_viewer,
        "is_anesthesia_scanner": is_anesthesia_scanner,
        "is_anesthesia_viewer": is_anesthesia_viewer,
        "last_login": last_login,
        "last_logout": last_logout,
        "password_changed": pass_changed,
        "emp_id": emp_id,
        "email": email,
        "total_images_scanned": {"$numberLong": "0"},
        "image": image
    }

    # Connect to the MongoDB collection
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']

    # Normalize anesthesia role fields for existing users
    doc_id.update_many(
        {"is_anesthesia_scanner": {"$exists": False}},
        {"$set": {"is_anesthesia_scanner": False}}
    )
    doc_id.update_many(
        {"is_anesthesia_viewer": {"$exists": False}},
        {"$set": {"is_anesthesia_viewer": False}}
    )

    # Check if the user already exists using emp_id
    existing_user = doc_id.find_one({"emp_id": emp_id})
    if existing_user is None:
        # Insert a new document if no existing user is found
        doc_id.insert_one(ob)
        return {'msg': "User created successfully", 'status': 200}
    else:
        # Update the existing document with the new data
        doc_id.update_one({"emp_id": emp_id}, {"$set": ob})
        return {'msg': "User updated successfully", 'status': 200}


@jwt_required()
def reset_pass():
    obj = request.get_json()
    pas = str(obj['pass'])
    user = str(obj['user']).upper()
    change = str(obj['changed_pass'])
    print("Connecting to db")
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    print("connection successful")
    collection = my_client["DOC_SCAN"]
    doc = collection['VIEWER_AUTH']
    if doc.find_one({"USERNAME": user, "is_admin": False}):
        d = doc.find_one({"USERNAME": user, "is_admin": False})
        user_password_from_db = d["PASSWORD"]
        if bc.checkpw(pas.encode('utf-8'), user_password_from_db.encode('utf-8')):
            if bc.checkpw(change.encode('utf-8'), user_password_from_db.encode('utf-8')):
                return {"msg": "Old password can't be set as new password.",
                        "status": 0
                        }
            chan = {"$set": {'PASSWORD': (bc.hashpw(change.encode('utf-8'), bc.gensalt(10))).decode('utf-8')}}
            fil = {"USERNAME": user}
            doc.update_one(fil, chan)
            return {"msg": "SUCCESS",
                    "status": 1
                    }
        else:
            return {"msg": "FAILED",
                    "status": 0
                    }
    else:
        return {"msg": "FAILED",
                "status": 0
                }


def logout_time_stamp():
    emp = str(request.args.get('emp_id'))
    print(emp)
    print("Connecting to db")
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    print("connection successful")
    collection = my_client["DOC_SCAN"]
    doc = collection['VIEWER_AUTH']
    print(doc.find_one({'emp_id': emp}))
    doc.update_one({'emp_id': emp}, {'$set': {"last_logout": str(datetime.datetime.now())}})
    return {
        "msg": "Successfully Added Timestamp",
        "status": 1
    }


@jwt_required()
def deactivate():
    emp = request.args.get("emp_id")
    if not emp:
        data = request.get_json(silent=True) or {}
        emp = data.get("emp_id")
    if not emp:
        return jsonify({"message": "Missing emp_id"}), 400

    client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    coll   = client["DOC_SCAN"]["VIEWER_AUTH"]

    updated = coll.find_one_and_update(
        {"emp_id": str(emp)},
        [
            {"$set": {"is_active": {"$not": ["$is_active"]}}}
        ],
        return_document=ReturnDocument.AFTER
    )

    if not updated:
        return jsonify({"message": "Employee not found"}), 404

    return jsonify({
        "message": f"Successfully changed is_active → {updated['is_active']}",
        "status": 200
    }), 200



@jwt_required()
def stats():
    return stats_calculator()


@jwt_required()
def dell():
    r = request.get_json()
    img_id = str(r['id'])
    emp_id = str(r['emp_id'])
    img_id = int(img_id)
    print(img_id)
    Mongo_APIS.soft_del(img_id, emp_id)
    return {'msg': "Success", 'status': 200}


@jwt_required()
def undo_dell():
    r = request.get_json()
    img_id = str(r['id'])
    img_id = int(img_id)
    print(img_id)
    Mongo_APIS.soft_del_rev(img_id)
    return {'msg': "Success", 'status': 200}


@jwt_required()
def check_existence():
    r = request.args.get('mrno')
    return {'msg': Mongo_APIS.mrn_checker(r), 'status': 200}


@jwt_required()
def dumb_classifier():
    r = request.get_json()
    img_id = int(r['id'])
    class_num = str(r['class'])
    print("converting", str(img_id), "to", "class", class_num)
    Mongo_APIS.class_changer_dumb(img_id, class_num)
    return {'msg': True, 'status': 200}


def verify_pass():
    login_details = request.get_json()
    print(login_details)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']
    user_from_db = doc_id.find_one({'emp_id': login_details['emp_id']})  # search for user in database
    print(user_from_db)
    if user_from_db:
        print("-------------------------------------------------------------------------")
        encrpted_password = login_details['pass'].encode("utf-8")
        print(encrpted_password)
        print(user_from_db['PASSWORD'])
        if bc.checkpw(encrpted_password, user_from_db['PASSWORD'].encode("utf-8")) and user_from_db[
            'is_active'] is True:
            return {'msg': True, 'status': 200}
        else:
            return {'msg': False, 'status': 200}


@jwt_required()
def unclassified_getter():
    ret = {
        "data": Mongo_APIS.get_all_unclassified(),
        "count": Mongo_APIS.get_unclassified_count(),
        "status": 200
    }
    return ret


@jwt_required()
def recycled_getter():
    show = int(request.args.get("documents_per_page"))
    page = int(request.args.get("page_number"))
    ret = {
        "data": Mongo_APIS.get_all_recycled(show, page),
        "count": Mongo_APIS.get_recycled_count(),
        "status": 200
    }
    return ret


@jwt_required()
def bulk_dumb_classify():
    r = request.get_json()
    image_list = list(r['ids'])
    cls = r['class']
    changed_by = r['changed_by']
    Mongo_APIS.class_changer_dumb_bulk(image_list, cls, changed_by)
    return {"status": 200}


@jwt_required()
def get_images_by_visit_id_op(visit_id_op):
    try:
        client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        db = client["DOC_SCAN"]
        collection = db["DOCUMENTS"]

        # Use the indexed query
        images_cursor = collection.find(
            {"visit_id_op": visit_id_op},
            {
                "_id": 0,
                "doc_id": 1,
                "mrno": 1,
                "type": 1,
                "visit_id_op": 1,
                "doc": 1
            }
        ).batch_size(100)

        images_list = []
        for image in images_cursor:
            images_list.append({
                "doc_id": image["doc_id"],
                "mrno": image["mrno"],
                "type": image["type"],
                "visit_id_op": image["visit_id_op"],
                "image": base64.b64encode(image["doc"]).decode('utf-8')
            })

        if not images_list:
            return jsonify({"message": f"No images found for visit_id_op: {visit_id_op}"}), 404

        return jsonify({"images": images_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@jwt_required()
def get_images_by_admission_id(admission_id):
    try:
        client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        db = client["DOC_SCAN"]
        collection = db["DOCUMENTS"]

        # Use the indexed query
        images_cursor = collection.find(
            {"admission_id": admission_id},
            {
                "_id": 0,
                "doc_id": 1,
                "mrno": 1,
                "type": 1,
                "admission_id": 1,
                "doc": 1
            }
        ).batch_size(100)

        images_list = []
        for image in images_cursor:
            images_list.append({
                "doc_id": image["doc_id"],
                "mrno": image["mrno"],
                "type": image["type"],
                "admission_id": image["admission_id"],
                "image": base64.b64encode(image["doc"]).decode('utf-8')
            })

        if not images_list:
            return jsonify({"message": f"No images found for admission_id: {admission_id}"}), 404

        return jsonify({"images": images_list}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


# Register routes with Flask-RESTX
def _register_restx_routes():
    def make_resource(func, methods):
        def wrapper(self, **kwargs):
            return func(**kwargs)
        attrs = {'__doc__': func.__doc__}
        for m in methods:
            attrs[m.lower()] = wrapper
        return type(f"{func.__name__.title()}Resource", (Resource,), attrs)

    routes = [
        (docscan_ns, '/login', ['POST'], login),
        (docscan_ns, '/scanner/login', ['POST'], login_rolebase),
        (api, '/scan_zip_file', ['GET'], route_function_zip),
        (api, '/scan_base64', ['GET'], route_function_base),
        (api, '/home', ['GET'], welcs),
        (ipd_ns, '/all_details', ['GET'], Route_Function_Ipd),
        (ipd_ns, '/with_date', ['GET'], Route_Function_Ipd_with_date),
        (ipd_ns, '/all_dates', ['GET'], Route_Function_Ipd_all_dates),
        (opd_ns, '/all_details', ['GET'], Route_Function_Opd),
        (opd_ns, '/all_dates', ['GET'], Route_Function_Opd_all_dates),
        (opd_ns, '/with_date', ['GET'], Route_Function_Opd_with_date),
        (docscan_ns, '/patient_demographics', ['GET'], Route_Function_Patient_Demographics),
        (docscan_ns, '/upload', ['POST'], route_function_upload),
        (docscan_ns, '/upload/bulk', ['POST'], route_function_upload_bulk),
        (docscan_ns, '/mortality/upload/bulk', ['POST'], route_function_mrt_upload_bulk),
        (api, '/save', ['POST'], route_function_save),
        (bulk_ns, '/save', ['POST'], route_function_bulk_save),
        (mortality_ns, '/bulk/save', ['POST'], route_function_bulk_save_for_mortality),
        (bulk_ns, '/view', ['GET'], route_function_bulk_view),
        (bulk_ns, '/view/class', ['GET'], route_function_bulk_view_class_doc),
        (bulk_ns, '/view/class/count_based', ['GET'], route_function_bulk_view_class_count_based),
        (api, '/employee_data', ['GET'], get_emp_data),
        (api, '/get_classes', ['GET'], get_classes),
        (api, '/get_class_images', ['GET'], get_images),
        (mrd_ns, '/get_emp_details', ['GET'], get_mrd_employees),
        (mrd_ns, '/get_all_users', ['GET'], bring_all_users),
        (mrd_ns, '/create_scanner_user', ['POST'], create_scanners),
        (mrd_ns, '/reset_pass', ['POST'], reset_pass),
        (docscan_ns, '/scanner/logout', ['POST'], logout_time_stamp),
        (docscan_ns, '/scanner/deactivate', ['POST', 'GET'], deactivate),
        (docscan_ns, '/stats', ['GET'], stats),
        (docscan_ns, '/delete', ['POST'], dell),
        (docscan_ns, '/undo_delete', ['POST'], undo_dell),
        (docscan_ns, '/check_existence', ['GET'], check_existence),
        (docscan_ns, '/dumb_classifier', ['POST'], dumb_classifier),
        (docscan_ns, '/verify_pass', ['POST'], verify_pass),
        (docscan_ns, '/get_all_unclassified', ['GET'], unclassified_getter),
        (docscan_ns, '/get_all_recycled', ['GET'], recycled_getter),
        (docscan_ns, '/bulk_dumb_classify', ['POST'], bulk_dumb_classify),
        (docscan_ns, '/images/<visit_id_op>', ['GET'], get_images_by_visit_id_op),
        (docscan_ns, '/images/admission/<admission_id>', ['GET'], get_images_by_admission_id),
    ]
    for ns, route, methods, func in routes:
        ns.add_resource(make_resource(func, methods), route)


_register_restx_routes()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "_main_":
    # clone_server.initiate_mongo_devil()
    app.run(debug=True, host='0.0.0.0', threaded=True, port=5000)
    # waitress.serve(app, host='0.0.0.0', port=5000)
