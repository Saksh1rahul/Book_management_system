import hashlib
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
from flask import Flask, g, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', "sakshi's_project")

DB_PATH = os.path.join(os.path.dirname(__file__), 'books.db')


def get_db_connection():
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA busy_timeout = 30000')
    connection.execute('PRAGMA journal_mode = WAL')
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()


def hash_password(password, salt):
    salt_text = str(salt)
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_text.encode('utf-8'), 100000).hex()


def verify_password(password, password_hash, salt):
    return hash_password(password, salt) == password_hash


def create_access_token(username):
    payload = {
        'sub': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = None
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = payload.get('sub')
            if not username:
                raise jwt.InvalidTokenError('Missing subject')

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT id, username FROM user WHERE username = ?', (username,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if not user:
                return jsonify({'error': 'User not found'}), 401

            g.user = dict(user)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return func(*args, **kwargs)

    return decorated


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id FROM user WHERE username = ?', (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({'error': 'User already exists'}), 409

    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt)
    try:
        cursor.execute(
            'INSERT INTO user (username, password_hash, password_salt) VALUES (?, ?, ?)',
            (username, password_hash, salt)
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': 'User already exists'}), 409

    cursor.close()
    connection.close()
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT password_hash, password_salt FROM user WHERE username = ?', (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not verify_password(password, user['password_hash'], user['password_salt']):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_access_token(username)
    return jsonify({'token': token, 'username': username}), 200


@app.route('/me', methods=['GET'])
@token_required
def current_user():
    return jsonify({'username': g.user['username']}), 200


@app.errorhandler(404)
def handle_404(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.route('/', methods=['GET'])
def get_books():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM book')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify([dict(row) for row in rows])


@app.route('/create', methods=['POST'])
@token_required
def create_books():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    new_book = request.get_json(silent=True)
    if not new_book:
        return jsonify({'error': 'Request must be JSON'}), 400

    required_fields = ['publisher', 'name', 'date', 'cost']
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

    edition_value = new_book.get('edition', '')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO book (publisher, name, date, cost, edition) VALUES (?, ?, ?, ?, ?)',
        (new_book['publisher'], new_book['name'], new_book['date'], cost_value, edition_value)
    )
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'data': {
        'publisher': new_book['publisher'],
        'name': new_book['name'],
        'date': new_book['date'],
        'cost': cost_value,
        'edition': edition_value
    }}), 201


@app.route('/update/<int:id>', methods=['PUT'])
@token_required
def update_book(id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    updated_book = request.get_json(silent=True)
    if not updated_book:
        return jsonify({'error': 'Request must be JSON'}), 400

    required_fields = ['publisher', 'name', 'date', 'cost']
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

    edition_value = updated_book.get('edition', '')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        'UPDATE book SET publisher=?, name=?, date=?, cost=?, edition=? WHERE id=?',
        (updated_book['publisher'], updated_book['name'], updated_book['date'], cost_value, edition_value, id)
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
        'edition': edition_value
    }})


@app.route('/delete/<int:id>', methods=['DELETE'])
@token_required
def delete_book(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('DELETE FROM book WHERE id=?', (id,))
    connection.commit()
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Book not found'}), 404

    cursor.close()
    connection.close()
    return jsonify({'message': 'deleted successfully'})


init_db()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
