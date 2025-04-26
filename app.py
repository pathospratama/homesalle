from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk semua route

# Path ke file JSON
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), 'helper','produk.json')

@app.route('/api/products', methods=['GET'])
def get_products():
    """Endpoint untuk mendapatkan semua produk"""
    try:
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            products = json.load(f)
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<path:filename>')
def serve_images(filename):
    """Endpoint untuk menyajikan gambar (opsional)"""
    return send_from_directory('images', filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)