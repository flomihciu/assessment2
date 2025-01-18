from flask import Flask, jsonify, abort, request, make_response, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)

# Configuring PostgreSQL database
DATABASE_CONFIG = {
    'dbname': 'flask_user_db',
    'user': 'jdcb',
    'host': 'localhost',
    'port': 5432
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)

def init_user_db():
    """Initialize the user database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("""
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def serve_index():
    """Serve the HTML front-end"""
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'users': users})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user is None:
        abort(404)
    return jsonify({'user': user})

@app.route('/users', methods=['POST'])
def add_user():
    if not request.json or 'name' not in request.json or 'email' not in request.json:
        abort(400)

    name = request.json['name']
    email = request.json['email']
    age = request.json.get('age')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (%s, %s, %s) RETURNING *;",
        (name, email, age)
    )
    new_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'user': new_user}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
    user = cursor.fetchone()
    if user is None:
        abort(404)

    name = request.json.get('name', user['name'])
    email = request.json.get('email', user['email'])
    age = request.json.get('age', user['age'])

    cursor.execute(
        "UPDATE users SET name = %s, email = %s, age = %s WHERE user_id = %s RETURNING *;",
        (name, email, age, user_id)
    )
    updated_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'user': updated_user})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id;", (user_id,))
    deleted_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if deleted_user is None:
        abort(404)
    return jsonify({'result': True})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

if __name__ == '__main__':
    init_user_db()
    app.run(host='127.0.0.1', port=5000)
