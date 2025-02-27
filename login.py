from flask import Flask, jsonify, request
import pyodbc
from flask_cors import CORS  # Import CORS from flask_cors module
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for your Flask app

# Database connection parameters
server = 'USER-PC\\SQLEXPRESS'
database = 'PFA'
username = 'sa'
password = '12345'
driver = '{ODBC Driver 17 for SQL Server}'

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        logging.debug("Establishing database connection")
        connection = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        logging.debug("Database connection established")
        return connection
    except Exception as e:
        logging.error(f"Error establishing database connection: {e}")
        raise

@app.route('/data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM [user]')
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        logging.debug(f"Fetched data: {results}")
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return jsonify({"error": "Error fetching data", "message": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()  # Get JSON payload
        username = data.get('username')
        password = data.get('password')

        logging.debug(f"Received login request for username: {username}")

        if not username or not password:
            logging.error("Missing username or password")
            return jsonify({"error": "Missing username or password"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM [user] WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user:
            logging.error(f"User {username} not found")
            return jsonify({"error": "User not found"}), 404

        db_password = user.password

        if password != db_password:
            logging.error("Incorrect password")
            return jsonify({"error": "Incorrect password"}), 401

        columns = [column[0] for column in cursor.description]
        user_dict = dict(zip(columns, user))
        cursor.close()
        conn.close()

        logging.debug(f"Login successful for username: {username}")
        return jsonify({"message": "Login successful", "user": user_dict}), 200
    except Exception as e:
        logging.error(f"Error during login process: {e}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
