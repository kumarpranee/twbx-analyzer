from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from analyze_twbx import analyze_twbx_file  # You need to implement this function
from generate_pdf import generate_pdf_report  # You need to implement this function

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
    pdf_path = generate_pdf_report(analysis_data)
    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)