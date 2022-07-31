import os
import sqlite3
from flask import Flask, g, request, make_response, jsonify, send_from_directory
from flask_cors import CORS
import json
import vision_api

UPLOAD_FOLDER = 'resources/trim'

dbpath = 'test.db'
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
        db.execute('CREATE TABLE IF NOT EXISTS my_profile(id INTEGER PRIMARY KEY AUTOINCREMENT, uid VARCHAR(140) unique, name VARCHAR(140), postalcode VARCHAR(7), address VARCHAR(140), filename VARCHAR(140))')
    return db


@app.route('/api/my_profile', methods=['GET'])
def get_my_profiles():
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('SELECT * FROM my_profile')
    my_profiles = []
    for row in cur.fetchall():
        my_profiles.append(dict(row))

    return json.dumps(my_profiles, indent=2)


@app.route('/api/my_profile/<uid>', methods=['GET'])
def get_my_profile(uid):
    con = get_db()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('SELECT * FROM my_profile WHERE uid = ?', [uid])
    my_profile = dict(cur.fetchall()[0])

    return json.dumps(my_profile, indent=2)


@app.route('/api/my_profile/<uid>', methods=['PUT'])
def put_my_profile(uid):
    con = get_db()
    cur = con.cursor()

    # uid = request.json["uid"]
    name = request.json["name"]
    postalcode = request.json["postalcode"]
    address = request.json["address"]
    filename = request.json["filename"]

    cur.execute('SELECT * FROM my_profile WHERE uid = ?', [uid])
    if len(cur.fetchall()) == 0:
        print('insert')
        cur.execute("INSERT INTO my_profile(uid, name, postalcode, address, filename) values(?,?,?,?,?)",
                    [uid, name, postalcode, address, filename])
    else:
        print('update')
        cur.execute("UPDATE my_profile SET name = ?, postalcode = ?, address = ?, filename = ? WHERE uid = ?",
                    [name, postalcode, address, filename, uid])

    con.commit()

    return 'Success save a profile!\n'


@app.route('/api/my_profile/<uid>', methods=['DELETE'])
def delete_my_profile(uid):
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM my_profile WHERE uid = ?", [uid])
    con.commit()

    return 'Success delete a profile!\n'


@app.route('/api/avatar', methods=['POST'])
def upload_avatar():
    if 'upload_file' not in request.files:
        make_response(jsonify({'result': 'uploadFile is required.'}))

    file = request.files['upload_file']
    filename = file.filename
    if filename == '':
        make_response(jsonify({'result': 'filename must not empty.'}))

    vision_api.upload_file(file, filename, 'resources/original')
    path = os.path.join('resources/original', filename)
    vertices = vision_api.detect_crop_hints(path)
    vision_api.crop_file(path, vertices)

    return request.base_url + '/' + filename


@app.route('/api/avatar/<name>')
def download_avatar(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
