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
from flask_restful import Api, Resource
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
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

api = Api(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'zb$@ic^Jg#aywFO1u9%shY7E66Z1cZnO&EK@9e$nwqTrLF#ph1'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=8)


@app.route("/docscan/login", methods=["POST"])
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
            return jsonify({"access_token": access_token,
                            "status": True
                            }), 200, {"Access-Control-Allow-Origin": '*'}

    return jsonify({'msg': 'The username or password is incorrect',
                    "status": False
                    }), 401


@app.route("/docscan/scanner/login", methods=["POST"])
def login_rolebase():
    login_details = request.get_json()
    print(login_details)
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']
    user_from_db = doc_id.find_one({'USERNAME': str(login_details['USERNAME']).upper()})  # search for user in database
    print(user_from_db)
    if user_from_db:
        print("-------------------------------------------------------------------------")
        encrpted_password = login_details['PASSWORD'].encode("utf-8")
        print(encrpted_password)
        print(user_from_db['PASSWORD'])
        if bc.checkpw(encrpted_password, user_from_db['PASSWORD'].encode("utf-8")) and user_from_db[
            'is_active'] is True:
            access_token = create_access_token(identity=user_from_db['USERNAME'])  # create jwt token
            doc_id.update_one({'USERNAME': str(login_details['USERNAME']).upper()},
                              {"$set": {"last_login": str(datetime.datetime.now())}})
            return jsonify({"access_token": access_token,
                            "name": user_from_db['name'],
                            "is_admin": user_from_db['is_admin'],
                            "is_active": user_from_db['is_active'],
                            "is_scanner": user_from_db['is_scanner'],
                            "is_viewer": user_from_db['is_viewer'],
                            "last_login": user_from_db['last_login'],
                            "last_logout": user_from_db['last_logout'],
                            "password_changed": user_from_db['password_changed'],
                            "emp_id": user_from_db['emp_id'],
                            "email": user_from_db['email'],
                            "total_images_scanned": user_from_db['total_images_scanned'],
                            "image": user_from_db['image'],
                            "status": True
                            }), 200, {"Access-Control-Allow-Origin": '*'}

    if user_from_db['is_active'] is False:
        return jsonify({'msg': 'you have been deactivated by the admin',
                        "status": False
                        }), 401
    else:
        return jsonify({'msg': 'Username of password is incorrect',
                        "status": False
                        }), 401


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Access-Control-Allow-Origin')
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route("/scan_zip_file")
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


@app.route("/scan_base64")
def route_function_base():
    route_object = main_scanner_driver()
    return route_object


@app.route("/home")
def welcs():
    return "<h1>WELCOME API'S ARE NOW RUNNING :)<h1>"


@app.route("/ipd/all_details")
@jwt_required()
def Route_Function_Ipd():
    mr = str(request.args.get('mr'))
    route_object = oracle_apis.ipd_patient_details(mr)
    return route_object


@app.route("/ipd/with_date")
@jwt_required()
def Route_Function_Ipd_with_date():
    mr = str(request.args.get('mr'))
    date = str(request.args.get('date'))
    route_object = oracle_apis.ipd_patient_details_with_date(date, mr)
    return route_object


@app.route("/ipd/all_dates")
@jwt_required()
def Route_Function_Ipd_all_dates():
    mr = request.args.get('mr')
    route_object = oracle_apis.ipd_patient_details_dates_only(mr)
    return route_object


@app.route("/opd/all_details")
@jwt_required()
def Route_Function_Opd():
    mr = request.args.get('mr')
    route_object = oracle_apis.opd_patient_details(mr)
    return route_object


@app.route("/opd/all_dates")
@jwt_required()
def Route_Function_Opd_all_dates():
    mr = request.args.get('mr')
    route_object = oracle_apis.opd_patient_details_dates_only(mr)
    return route_object


@app.route("/opd/with_date")
@jwt_required()
def Route_Function_Opd_with_date():
    mr = str(request.args.get('mr'))
    date = str(request.args.get('date'))
    route_object = oracle_apis.opd_patient_details_with_date(date, mr)
    return route_object


@app.route("/docscan/patient_demographics")
@jwt_required()
def Route_Function_Patient_Demographics():
    mr = str(request.args.get('mrno'))
    route_object = oracle_apis.demo(mr)
    return route_object


@app.route("/docscan/upload", methods=["POST"])
@jwt_required()
def route_function_upload():
    print("line 1")
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
        filename = str(
            doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
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
            'doctor_speciality_op': loaded["doctor_speciality_op"],
            'visit_date_op': loaded["visit_date_op"],
            'admission_id': loaded["admission_id"],
            'admission_date_ip': loaded["admission_date_ip"],
            'complain_ip': loaded["complain_ip"],
            'doctor_id_ip': loaded["doctor_id_ip"],
            'doctor_speciality_ip': loaded["doctor_speciality_ip"],
            'class': None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,  # this will be an array
            'main_type': None,
            'is_bulk': False,
            'uploaded': True,
            'is_del': False,
            'del_by': '',
            'rc_by_id': None,
            'mrt': False
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


@app.route("/docscan/mortality/upload/", methods=["POST"])
@jwt_required()
def route_function_mortality_upload():
    print("line 1")
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
        filename = str(
            doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
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
            'doctor_speciality_op': loaded["doctor_speciality_op"],
            'visit_date_op': loaded["visit_date_op"],
            'admission_id': loaded["admission_id"],
            'admission_date_ip': loaded["admission_date_ip"],
            'complain_ip': loaded["complain_ip"],
            'doctor_id_ip': loaded["doctor_id_ip"],
            'doctor_speciality_ip': loaded["doctor_speciality_ip"],
            'class': None,
            'ocr': None,
            'notes': None,
            'misclassified': False,
            'marked_as_fav_by_user': None,  # this will be an array
            'main_type': None,
            'is_bulk': False,
            'uploaded': True,
            'is_del': False,
            'del_by': '',
            'rc_by_id': None,
            'mrt': True
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


def bulk_saving_function_for_multi_threaded_saving_mortality(data_to_be_saved, d):
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
            'class': None,
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
            'mrt': True
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


def bulk_saving_function_for_multi_threaded_saving(data_to_be_saved, d):
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
            'class': None,
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
            'mrt': False
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


@app.route("/docscan/upload/bulk", methods=["POST"])
@jwt_required()
def route_function_upload_bulk():
    data_to_be_saved = request.get_json()
    d = json.dumps(data_to_be_saved)
    multiprocessing.Process(target=bulk_saving_function_for_multi_threaded_saving, args=(data_to_be_saved, d,)).start()
    return "saved"


@app.route("/docscan/mortality/upload/bulk", methods=["POST"])
@jwt_required()
def route_function_mortality_upload_bulk():
    data_to_be_saved = request.get_json()
    d = json.dumps(data_to_be_saved)
    multiprocessing.Process(target=bulk_saving_function_for_multi_threaded_saving_mortality,
                            args=(data_to_be_saved, d,)).start()
    return "saved"


@app.route("/save", methods=["POST"])
@jwt_required()
def route_function_save():
    data_to_be_saved = request.get_json()
    # print(data_to_be_saved)
    d = json.dumps(data_to_be_saved)
    loaded = json.loads(d)
    print(loaded)
    for i in (loaded["scannedImages"]["scannerImages"]):
        imgdata = base64.b64decode((i["base64"])[1:])
        filename = str(
            doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata)
        im = Image.open(filename)

        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

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
            'class': None,
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


@app.route("/bulk/save", methods=["POST"])
def route_function_bulk_save():
    data_to_be_saved = request.get_json()
    loaded = json.loads(json.dumps(data_to_be_saved))

    for i in loaded["scannedImages"]["scannerImages"]:
        # Remove the prefix before decoding
        base64_data = i["base64"].split(",")[-1]
        imgdata = base64.b64decode(base64_data)
        filename = str(doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'

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
            'class': None,
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

        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc = collection['DOCUMENTS']
        image_id = doc.insert_one(image).inserted_id

    # Remove all jpg files after processing
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)

    return "saved"


@app.route("mortality/bulk/save", methods=["POST"])
def route_function_bulk_save():
    data_to_be_saved = request.get_json()
    loaded = json.loads(json.dumps(data_to_be_saved))

    for i in loaded["scannedImages"]["scannerImages"]:
        # Remove the prefix before decoding
        base64_data = i["base64"].split(",")[-1]
        imgdata = base64.b64decode(base64_data)
        filename = str(doc_id_from_mongo.doc_id_dispatcher()) + '.jpg'

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
            'class': None,
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

        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc = collection['DOCUMENTS']
        image_id = doc.insert_one(image).inserted_id

    # Remove all jpg files after processing
    for img in glob.glob("*.jpg"):
        print("removing " + img)
        os.remove(img)

    return "saved"


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/bulk/view", methods=["GET"])
@jwt_required()
def route_function_bulk_view():
    mr = request.args.get("mrno")
    return Mongo_APIS.bulk_viewer(mr)


@app.route("/bulk/view/class", methods=["GET"])
@jwt_required()
def route_function_bulk_view_class_doc():
    mr = request.args.get("mrno")
    class_filter = request.args.get("class")
    return Mongo_APIS.get_images_by_class_doc(mr, class_filter)


@app.route("/bulk/view/class/compressed", methods=["GET"])
@jwt_required()
def route_function_bulk_view_class_thumb():
    mr = request.args.get("mrno")
    class_filter = request.args.get("class")
    return Mongo_APIS.get_images_by_class_thumb(mr, class_filter)


@app.route("/bulk/view/class/count_based", methods=["GET"])
@jwt_required()
def route_function_bulk_view_class_count_based():
    mr = request.args.get("mrno")
    class_filter = request.args.get("class")
    return Mongo_APIS.image_count_with_class_names(mr)


@app.route("/employee_data", methods=["GET"])
@jwt_required()
def get_emp_data():
    route_object = oracle_apis.mrd_emp_data()
    return route_object


@app.route("/get_classes", methods=["GET"])
@jwt_required()
def get_classes():
    route_object = gd()
    return route_object


@app.route("/get_class_images", methods=["GET"])
@jwt_required()
def get_images():
    mrno = str(request.args.get('mr'))
    id = str(request.args.get('id'))
    route_obj = gmr(mrno, id)
    return route_obj


@app.route("/mrd/get_emp_details", methods=["GET"])
@jwt_required()
def get_mrd_employees():
    route_obj = oracle_apis.mrd_emp_data()
    return route_obj


@app.route("/mrd/get_all_users", methods=["GET"])
@jwt_required()
def bring_all_users():
    route_obj = Mongo_APIS.bring_users_data()
    return route_obj


@app.route("/mrd/create_scanner_user", methods=["POST"])
@jwt_required()
def create_scanners():
    data_to_be_saved = request.get_json()
    # print(data_to_be_saved)
    d = json.dumps(data_to_be_saved)
    loaded = json.loads(d)
    print(loaded)

    name = str(loaded['name'])
    password = "$2b$10$eZXqe1XtndtvuOFdYqKHneX5XY6bIX7.88Jx8VzowVciB4Y.3ssTu"
    emp_id = str(loaded['emp_id'])
    is_scanner = bool(loaded['is_scanner'])
    is_viewer = bool(loaded['is_viewer'])
    is_admin = False
    email = str(loaded['email'])
    is_active = True
    last_login = str('')
    last_logout = str('')
    pass_changed = False
    total_images_scanned = 0
    image = str(loaded['image'])
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']
    ob = {
        'name': name,
        'USERNAME': emp_id,
        'PASSWORD': password,
        'is_admin': is_admin,
        "is_active": is_active,
        "is_scanner": is_scanner,
        "is_viewer": is_viewer,
        "last_login": '',
        "last_logout": '',
        "password_changed": pass_changed,
        "emp_id": emp_id,
        "email": email,
        "total_images_scanned": {
            "$numberLong": "0"
        },
        "image": image
    }

    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['VIEWER_AUTH']
    if doc_id.find_one({"emp_id": emp_id}) is None:
        doc_id.insert_one(ob)
        return {'msg': "Success", 'status': 200}
    else:
        return {'msg': "Either the user is disabled or already created", 'status': 0}


@app.route("/mrd/reset_pass", methods=["POST"])
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


@app.route("/docscan/scanner/logout", methods=["POST"])
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


@app.route("/docscan/scanner/deactivate", methods=["POST"])
@jwt_required()
def deactivate():
    emp = str(request.args.get('emp_id'))
    print(emp)
    print("Connecting to db")
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    print("connection successful")
    collection = my_client["DOC_SCAN"]
    doc = collection['VIEWER_AUTH']
    print(doc.find_one({'emp_id': emp}))
    d = doc.find_one({'emp_id': emp})
    msg = not (d["is_active"])
    doc.update_one({'emp_id': emp}, {'$set': {"is_active": not (d["is_active"])}})
    if doc.update_one({'emp_id': emp}, {'$set': {"is_active": not (d["is_active"])}}):
        return {
            "message": "Successfully Changed to " + str(msg),
            "status": 200
        }
    else:
        return {
            "message": "Unable to change status",
            "status": 304
        }


@app.route("/docscan/stats", methods=["GET"])
@jwt_required()
def stats():
    return stats_calculator()


@app.route("/docscan/delete", methods=["POST"])
@jwt_required()
def dell():
    r = request.get_json()
    img_id = str(r['id'])
    emp_id = str(r['emp_id'])
    img_id = int(img_id)
    print(img_id)
    Mongo_APIS.soft_del(img_id, emp_id)
    return {'msg': "Success", 'status': 200}


@app.route("/docscan/undo_delete", methods=["POST"])
@jwt_required()
def undo_dell():
    r = request.get_json()
    img_id = str(r['id'])
    img_id = int(img_id)
    print(img_id)
    Mongo_APIS.soft_del_rev(img_id)
    return {'msg': "Success", 'status': 200}


@app.route("/docscan/check_existence", methods=["GET"])
@jwt_required()
def check_existence():
    r = request.args.get('mrno')
    return {'msg': Mongo_APIS.mrn_checker(r), 'status': 200}


@app.route("/docscan/dumb_classifier", methods=["POST"])
@jwt_required()
def dumb_classifier():
    r = request.get_json()
    img_id = int(r['id'])
    class_num = str(r['class'])
    print("converting", str(img_id), "to", "class", class_num)
    Mongo_APIS.class_changer_dumb(img_id, class_num)
    return {'msg': True, 'status': 200}


@app.route("/docscan/verify_pass", methods=["POST"])
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


@app.route("/docscan/get_all_unclassified", methods=["GET"])
@jwt_required()
def unclassified_getter():
    ret = {
        "data": Mongo_APIS.get_all_unclassified(),
        "count": Mongo_APIS.get_unclassified_count(),
        "status": 200
    }
    return ret


@app.route("/docscan/get_all_recycled", methods=["GET"])
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


@app.route("/docscan/bulk_dumb_classify", methods=["POST"])
@jwt_required()
def bulk_dumb_classify():
    r = request.get_json()
    image_list = list(r['ids'])
    cls = r['class']
    changed_by = r['changed_by']
    Mongo_APIS.class_changer_dumb_bulk(image_list, cls, changed_by)
    return {"status": 200}


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == "__main__":
    # clone_server.initiate_mongo_devil()
    app.run(debug=True, host='0.0.0.0', threaded=True, port=5000)
    # waitress.serve(app, host='0.0.0.0', port=5000)
