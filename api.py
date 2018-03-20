import jsonify, os, imagehash
from PIL import Image
from uuid import uuid4

from werkzeug.utils import secure_filename

from flask import Flask, request, render_template, jsonify
from blockchain import Blockchain, Block, Message

chain = None
app = Flask(__name__)
app.config['DEBUG'] = True
UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_app():
    global chain
    chain = Blockchain()
    return app

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/addPatient', methods=['POST'])
def add_patient():
    digital_id = request.form['id']  # Make using public and private keys
    age = request.form['age']
    blood_group = request.form['blood_group']
    allergies = request.form['allergies']
    genetic_problems = request.form['genetic_problems']

    block = Block()
    block.add_message(Message(digital_id))
    block.add_message(Message(age))
    block.add_message(Message(blood_group))
    block.add_message(Message(allergies))
    block.add_message(Message(genetic_problems))
    block.seal()

    #chain.add_block(block)

    return jsonify({'status': 'success'})




@app.route('/addRecord', methods=['POST'])
def add_record():
    digital_id = request.form['id']
    record_type = request.form['record_type']
    accessible_by = request.form['accessible_by']
    datacenter = request.form['datacenter']
    image_file = request.files['image_file']
    image_extension = os.path.splitext(secure_filename(image_file.filename))[1]
    unique_filename = uuid4().hex + image_extension
    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
    hash = str(imagehash.average_hash(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))))


    block = Block()
    block.add_message(Message(digital_id))
    block.add_message(Message(record_type))
    block.add_message(Message(hash))
    block.add_message(Message(accessible_by))
    block.add_message(Message(datacenter))
    block.add_message(Message(unique_filename))
    block.seal()
    chain.add_block(block)

    return jsonify({'status': 'success'})


@app.route('/fetchRecord', methods=['POST'])
def fetch_record():
    digital_id = request.form['id']

    records = []

    blocks = chain.get_blocks()
    for block in blocks:
        for message in block.get_messages():
            if message.get() == digital_id:
                records.append(block)

    return jsonify(records)
