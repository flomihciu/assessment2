from flask import Flask, jsonify, abort, request, make_response, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Allow requests from all origins (adjust this for production)
CORS(app, resources={r"/*": {"origins": "*"}})

# Hardcoded PostgreSQL database configuration
DATABASE_CONFIG = {
    'dbname': 'mydatabase',  # Hardcoded database name
    'user': 'flo',  # Hardcoded username
    'password': 'password123',  # Hardcoded password
    'host': 'terraform-20250127232957834800000001.cvyw6igek2bp.us-east-1.rds.amazonaws.com',  # RDS endpoint
    'port': 5432  # Default PostgreSQL port
}

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        abort(500)

def init_user_db():
    """Initialize the user database (run only once, not in production)."""
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
    """Serve the HTML front-end."""
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all users."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
    except Exception as e:
        print(f"Error executing query: {e}")
        abort(500)
    finally:
        cursor.close()
        conn.close()
    return jsonify({'users': users})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Fetch a user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
        user = cursor.fetchone()
    except Exception as e:
        print(f"Error executing query: {e}")
        abort(500)
    finally:
        cursor.close()
        conn.close()

    if user is None:
        abort(404)
    return jsonify({'user': user})

@app.route('/users', methods=['POST'])
def add_user():
    """Add a new user."""
    if not request.json or 'name' not in request.json or 'email' not in request.json:
        abort(400)

    name = request.json['name']
    email = request.json['email']
    age = request.json.get('age')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (%s, %s, %s) RETURNING *;",
            (name, email, age)
        )
        new_user = cursor.fetchone()
        conn.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
        abort(500)
    finally:
        cursor.close()
        conn.close()

    return jsonify({'user': new_user}), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
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
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
        abort(500)
    finally:
        cursor.close()
        conn.close()

    return jsonify({'user': updated_user})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id;", (user_id,))
        deleted_user = cursor.fetchone()
        conn.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback()
        abort(500)
    finally:
        cursor.close()
        conn.close()

    if deleted_user is None:
        abort(404)
    return jsonify({'result': True})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return make_response(jsonify({'error': 'Bad request'}), 400)

if __name__ == '__main__':
    # Remove init_user_db() from here for production
    # init_user_db()  # You should only run this once for initial setup
    app.run(host="0.0.0.0", port=8000)

