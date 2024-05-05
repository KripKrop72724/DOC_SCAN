from flask_compress import Compress
from driver_helper import main_scanner_driver
from flask_cors import CORS
from flask_restful import Api
from flask import Flask

compress = Compress()
app = Flask(__name__)
cors = CORS(app)
compress.init_app(app)

api = Api(app)


@app.route("/scan_base64")
def route_function_base():
    route_object = main_scanner_driver()
    return route_object


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Access-Control-Allow-Origin')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


@app.route("/home")
def welcs():
    return "<h1>WELCOME API'S ARE NOW RUNNING :)<h1>"


if __name__ == "__main__":
    context = ('local.crt', 'local.key')
    app.run(debug=True, host='0.0.0.0', threaded=True, port=7000, ssl_context=context)
