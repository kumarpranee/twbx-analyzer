from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from analyze_twbx import analyze_twbx_file
from load_to_db import load_data_to_db

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify(success=False, message='No file part')
    file = request.files['file']
    if file.filename == '':
        return jsonify(success=False, message='No selected file')
    if file and file.filename.endswith('.twbx'):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify(success=True)
    return jsonify(success=False, message='Invalid file type')

@app.route('/analyze', methods=['POST'])
def analyze_file():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.listdir(app.config['UPLOAD_FOLDER'])[0])
    analysis_data = analyze_twbx_file(file_path)
    
    db_config = {
        'dbname': 'your_db_name',
        'user': 'your_db_user',
        'password': 'your_db_password',
        'host': 'your_db_host',
        'port': 'your_db_port'
    }

    load_data_to_db(analysis_data, db_config)
    return jsonify(success=True, message='Data loaded into the database successfully')

if __name__ == '__main__':
    app.run(debug=True)