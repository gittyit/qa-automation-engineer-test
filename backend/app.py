'''  QA Automation Engineer Test:
- Index page --> Creates DB tables and populates it (async)
- Result page --> Retrieves the data from DB tables in JSON (async)
'''
import os
import asyncio

from get_db import dbManager

from flask import Flask, flash, get_flashed_messages
from flask import request, render_template as Render
from flask import jsonify, send_file, send_from_directory

from werkzeug.utils import secure_filename

app = Flask(__name__)
dbm = dbManager()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/result')
async def result_page():
    ''' Result page method.

    - Queries all data from the tables concurrently and sort it by ID.
    - If no data is found, returns an error page with error details
    - In case of success, returns data in JSON format
    '''
    try:
        data = []
        # Create coroutines list with data queries from 3 tables
        coros = [dbm.retrieve_data(i, data) for i in range(1, 4)]
        # Run coroutines concurrently and get data within timeout of 2 seconds
        for co in asyncio.as_completed(coros, timeout=2):
            await co
        # Sort data by id
        d = sorted(data, key=lambda x: x['id'])
        # print(d)
    except BaseException as ex:
        return Render("error.html", error_msg=str(ex))
    return jsonify(d)


@app.route('/')
async def index_page():
    ''' Index page method.

    - Asyncronicaly creates 3 data tables in DB.
    - Populates the tables with a following data:
        - Table data_1: IDs 1-10, 31-40;
        - Table data_2: IDs 11-20, 41-50;
        - Table data_3: IDs 21-30, 51-60;
    - In case of:
        - errors, returns an error page with details
        - success, returns success message
    '''
    return Render("index.html")

@app.route("/execute_test")
async def execute_test():
    try:
        await dbm.create_and_populate_tables()
    except BaseException as ex:
        return Render("error.html", error_msg=str(ex))
    return Render("test_executed.html")


@app.route("/download/<name>")
def download_file(name):
    return send_from_directory("uploads", name)
        # app.config['UPLOAD_FOLDER']
        # , as_attachment=True

@app.route("/upload_data", methods=['POST'])
async def upload_data():
    if 'file' not in request.files:
        flash('No file part')
        print('No file part')
        msgs = ""
        [ msgs.join(msg) for msg in get_flashed_messages()]
        print(f"msgs={msgs}")
        return Render("error.html", error_msg=str(msgs))
    file = request.files["file"]
    if file.filename == '':
        print('No selected file')
        msg = 'No selected file'
        return Render("error.html", error_msg=str(msg))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(f"Uploading.. {filename}")
        file_path = "/".join([os.getcwd(), app.config['UPLOAD_FOLDER'], filename])
        print(f"cwd={os.getcwd()}")
        print(f"path={file_path}")
        file.save(file_path)
        return 'File uploaded successfully', 200

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route("/download_data")
# async def download_data():
#     await dbm.create_and_populate_all_tables()
#     return Render("test_executed.html")

