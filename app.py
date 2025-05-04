from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

# Path ke file JSON tunggal
DATA_FILE = os.path.join(os.path.dirname(__file__), 'helper', 'produk.json')

# ------------------- Helper Functions -------------------
def load_data() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(data: List[Dict[str, Any]]) -> None:
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def validate_product_id(product_id: int) -> bool:
    return isinstance(product_id, int) and product_id > 0

def is_duplicate_id(product_id: int, data: List[Dict[str, Any]]) -> bool:
    return any(p.get('id') == product_id for p in data)

def is_duplicate_number(number: int, data: List[Dict[str, Any]]) -> bool:
    return any(p.get('number') == number for p in data)

# ------------------- API Routes -------------------
@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(load_data())

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    data = load_data()
    product = next((p for p in data if p.get('id') == product_id), None)
    return jsonify(product) if product else (jsonify({"status": "error", "message": "Product not found"}), 404)

@app.route('/api/products/add', methods=['POST'])
def add_product():
    data = load_data()
    form_data = request.form

    try:
        product_id = int(form_data.get('id', 0))
        number = int(form_data.get('number', 0))

        if not validate_product_id(product_id):
            return jsonify({"status": "error", "message": "Invalid product ID"}), 400

        if is_duplicate_id(product_id, data):
            return jsonify({"status": "error", "message": f"ID {product_id} already exists"}), 400

        if is_duplicate_number(number, data):
            return jsonify({"status": "error", "message": f"Number {number} already exists"}), 400

        new_product = {
            "id": product_id,
            "number": number,
            "name": form_data.get('name', '').strip(),
            "category": form_data.get('category', '').strip(),
            "price": int(form_data.get('price', 0)),
            "originalPrice": int(form_data.get('originalPrice', 0)),
            "image": form_data.get('image', '').strip(),
            "images": [img for img in request.form.getlist('images[]') if img.strip()],
            "link": form_data.get('link', '').strip(),
            "rating": float(form_data.get('rating', 0)),
            "reviews": int(form_data.get('reviews', 0)),
            "ribuan": form_data.get('ribuan', '').strip(),
            "stock": int(form_data.get('stock', 0)),
            "description": form_data.get('description', '').strip(),
            "specifications": form_data.get('specifications', '').strip(),
            "features": [ft for ft in request.form.getlist('features[]') if ft.strip()]
        }

        data.append(new_product)
        save_data(data)
        return jsonify({"status": "success", "message": "Product added successfully", "product": new_product})

    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/api/products/update', methods=['POST'])
def update_product():
    data = load_data()
    form_data = request.form

    try:
        product_id = int(form_data.get('id', 0))
        if not validate_product_id(product_id):
            return jsonify({"status": "error", "message": "Invalid product ID"}), 400

        product = next((p for p in data if p.get('id') == product_id), None)
        if not product:
            return jsonify({"status": "error", "message": "Product not found"}), 404

        if 'number' in form_data:
            new_number = int(form_data['number'])
            if new_number != product.get('number') and is_duplicate_number(new_number, data):
                return jsonify({"status": "error", "message": f"Number {new_number} already exists"}), 400

        update_fields = [
            "number", "name", "category", "price", "originalPrice",
            "image", "link", "rating", "reviews", "ribuan",
            "stock", "description", "specifications"
        ]

        for field in update_fields:
            if field in form_data:
                if form_data[field] == '':
                    product[field] = 0 if field in ["price", "originalPrice", "reviews", "stock", "number"] else 0.0 if field == "rating" else ''
                else:
                    product[field] = int(form_data[field]) if field in ["price", "originalPrice", "reviews", "stock", "number"] else float(form_data[field]) if field == "rating" else form_data[field].strip()

        if 'images[]' in form_data:
            product['images'] = [img for img in request.form.getlist('images[]') if img.strip()]
        if 'features[]' in form_data:
            product['features'] = [ft for ft in request.form.getlist('features[]') if ft.strip()]

        save_data(data)
        return jsonify({"status": "success", "message": "Product updated successfully", "product": product})

    except ValueError as e:
        return jsonify({"status": "error", "message": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id: int):
    data = load_data()
    new_data = [p for p in data if p.get('id') != product_id]
    if len(new_data) == len(data):
        return jsonify({"status": "error", "message": "Product not found"}), 404

    save_data(new_data)
    return jsonify({"status": "success", "message": "Product deleted successfully"})

@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('images', filename)

# ------------------- Main Entry -------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
