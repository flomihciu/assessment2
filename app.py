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
    'host': 'terraform-20250201154520043300000002.cvyw6igek2bp.us-east-1.rds.amazonaws.com',  # RDS endpoint
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
    """Serve the HTML front-e
