from functions import (handle_compress, handle_decompress)
from flask import Flask, jsonify, request, send_file, send_from_directory
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/compress", methods=["POST"])
def compress_img():
    name = request.args.get("name")
    codebook_size = int(request.args.get("codebookSize"))
    vector_size = int(request.args.get("vectorSize"))
    print(name)

    if 'file' not in request.files:
        return {'error' : 'Không có file nào được gửi lên'}, 400

    file = request.files['file']
    file.save(f'./image/origin/{name}')

    results = handle_compress(name, codebook_size, vector_size)
    if 'error' in results:
        return results, 400

    return jsonify(results)

@app.route("/api/decompress", methods=["POST"])
def decompress_file():
    name = request.args.get("name")
    print(name)

    if 'file' not in request.files:
        return 'No file found', 400

    file = request.files['file']
    file.save(f'./compress/upload/{name}')

    results = handle_decompress(name)

    return jsonify(results)

@app.route('/api/download', methods=['GET'])
def download_file():
    # Lấy params
    name = request.args.get("name")
    operation = request.args.get("operation")

    if operation == "compress":
        file_path = f'./compress/download/{name[0:-4]}.npz'
    else: 
        if operation == "decompress":
            file_path = f'./image/request/{name}'
        else: return 'Unknown operation', 400
    
    # Gửi file về client
    return send_file(file_path, as_attachment=True)

# Đường dẫn đến thư mục chứa ảnh
image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'image')

# Endpoint để truy cập ảnh
@app.route('/image/<path:path>')
def get_image(path):
    return send_from_directory(image_folder, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
