import hashlib
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from functools import wraps
import jwt
import pyodbc
from flask import Flask, g, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', "sakshi's_project")

MSSQL_CONNECTION_STRING = os.environ.get(
    'MSSQL_CONNECTION_STRING',
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=localhost;'
    'DATABASE=BookManagement;'
    'UID=sa;'
    'PWD=your_password;'
    'TrustServerCertificate=yes;'
)


def get_db_connection():
    return pyodbc.connect(MSSQL_CONNECTION_STRING)


def serialize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def row_to_dict(cursor, row):
    columns = [column[0] for column in cursor.description]
    return {column: serialize_value(value) for column, value in zip(columns, row)}


def fetchone_dict(cursor):
    row = cursor.fetchone()
    if not row:
        return None
    return row_to_dict(cursor, row)


def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        IF OBJECT_ID('dbo.book', 'U') IS NULL
        CREATE TABLE dbo.book (
            id INT IDENTITY(1,1) PRIMARY KEY,
            publisher NVARCHAR(255) NOT NULL,
            name NVARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            edition NVARCHAR(100) NOT NULL
        )
    ''')
    cursor.execute('''
        IF OBJECT_ID('dbo.users', 'U') IS NULL
        CREATE TABLE dbo.users (
            id INT IDENTITY(1,1) PRIMARY KEY,
            username NVARCHAR(255) UNIQUE NOT NULL,
            password_hash NVARCHAR(255) NOT NULL,
            password_salt NVARCHAR(255) NOT NULL,
            created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()


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
            cursor.execute('SELECT id, username FROM users WHERE username = ?', (username,))
            user = fetchone_dict(cursor)
            cursor.close()
            connection.close()

            if not user:
                return jsonify({'error': 'User not found'}), 401

            g.user = user
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
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({'error': 'User already exists'}), 409

    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt)
    cursor.execute(
        'INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)',
        (username, password_hash, salt)
    )
    connection.commit()
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
    cursor.execute('SELECT password_hash, password_salt FROM users WHERE username = ?', (username,))
    user = fetchone_dict(cursor)
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
    books = [row_to_dict(cursor, row) for row in rows]
    cursor.close()
    connection.close()
    return jsonify(books)


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
