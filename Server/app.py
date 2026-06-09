from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            publisher TEXT NOT NULL,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            cost REAL NOT NULL,
            edition TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.errorhandler(404)
def handle_404(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.route('/', methods=['GET'])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM book")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([dict(row) for row in rows])

@app.route('/create', methods=['POST'])
def create_books():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    new_book = request.get_json(silent=True)
    if not new_book:
        return jsonify({'error': 'Request must be JSON'}), 400

    required_fields = ['publisher', 'name', 'date', 'cost', 'edition']
    if not all(field in new_book for field in required_fields):
        return jsonify({'error': 'Missing field'}), 400

    try:
        cost_value = float(new_book['cost'])
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid cost'}), 400

    try:
        datetime.strptime(new_book['date'], '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
    "INSERT INTO book (publisher, name, date, cost, edition) VALUES (?, ?, ?, ?, ?)",
    (new_book['publisher'], new_book['name'], new_book['date'], cost_value, new_book['edition'])
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'data': {
        'publisher': new_book['publisher'],
        'name': new_book['name'],
        'date': new_book['date'],
        'cost': cost_value,
        'edition': new_book['edition']
    }}), 201

@app.route('/update/<int:id>', methods=['PUT'])
def update_book(id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    updated_book = request.get_json(silent=True)
    if not updated_book:
        return jsonify({'error': 'Request must be JSON'}), 400

    required_fields = ['publisher', 'name', 'date', 'cost', 'edition']
    if not all(field in updated_book for field in required_fields):
        return jsonify({'error': 'Missing field'}), 400

    try:
        cost_value = float(updated_book['cost'])
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid cost'}), 400

    try:
        datetime.strptime(updated_book['date'], '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
    "UPDATE book SET publisher=?, name=?, date=?, cost=?, edition=? WHERE id=?",
    (updated_book['publisher'], updated_book['name'], updated_book['date'], cost_value, updated_book['edition'], id)
    )
    connection.commit()
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Book not found'}), 404

    cursor.close()
    connection.close()
    return jsonify({'data': {
        'id': id,
        'publisher': updated_book['publisher'],
        'name': updated_book['name'],
        'date': updated_book['date'],
        'cost': cost_value,
        'edition': updated_book['edition']
    }})

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id=?", (id,))
    connection.commit()
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Book not found'}), 404

    cursor.close()
    connection.close()
    return jsonify({'message': 'deleted successfully'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
