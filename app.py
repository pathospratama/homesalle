from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# Inisialisasi Firebase
firebase_config = json.loads(os.environ.get("FIREBASE_ADMIN_CONFIG"))
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Helper: Konversi Firestore Document ke Dictionary
def doc_to_dict(doc):
    data = doc.to_dict()
    data['id'] = doc.id
    return data

# ------------------- API Routes -------------------

@app.route('/api/products', methods=['GET'])
def get_all_products():
    try:
        docs = db.collection('products').stream()
        products = [doc_to_dict(doc) for doc in docs]
        return jsonify({"status": "success", "data": products}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        doc_ref = db.collection('products').document(product_id)
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({"status": "success", "data": doc_to_dict(doc)}), 200
        else:
            return jsonify({"status": "error", "message": "Product not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.get_json()

        # Validasi field wajib
        required_fields = ['id', 'name', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Field '{field}' is required"}), 400

        product_id = str(data['id'])  # Gunakan id yang diberikan user
        doc_ref = db.collection('products').document(product_id)

        # Cek apakah ID sudah digunakan
        if doc_ref.get().exists:
            return jsonify({"status": "error", "message": f"Product with ID '{product_id}' already exists"}), 409

        doc_ref.set(data)

        return jsonify({
            "status": "success",
            "message": "Product added with custom ID",
            "id": product_id,
            "data": data
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products/<string:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        doc_ref = db.collection('products').document(product_id)

        if not doc_ref.get().exists:
            return jsonify({"status": "error", "message": "Product not found"}), 404

        doc_ref.update(data)
        updated_data = doc_ref.get().to_dict()
        updated_data['id'] = product_id

        return jsonify({
            "status": "success",
            "message": "Product updated",
            "data": updated_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/products/<string:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        doc_ref = db.collection('products').document(product_id)

        if not doc_ref.get().exists:
            return jsonify({"status": "error", "message": "Product not found"}), 404

        doc_ref.delete()
        return jsonify({"status": "success", "message": "Product deleted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
