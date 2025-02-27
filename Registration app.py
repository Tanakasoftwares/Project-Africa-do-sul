from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import urllib

app = Flask(__name__)

# Database connection parameters
server = 'USER-PC\\SQLEXPRESS'  # e.g., 'localhost'
database = 'PFA'
username = 'sa'
password = '12345'
driver = '{ODBC Driver 17 for SQL Server}'

# Configure the SQLAlchemy part of the app instance
params = urllib.parse.quote_plus(
    f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc:///?odbc_connect={params}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=False)

# Create the database and the db table
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    fullname = data.get('fullname')
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    gender = data.get('gender')

    # Check for missing fields
    if not fullname or not username or not email or not phone or not password or not gender:
        return jsonify({"error": "Missing data"}), 400

    # Check for existing username or email
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Username or Email already exists"}), 400

    # Create a new user record
    new_user = User(fullname=fullname, username=username, email=email, phone=phone, password=password, gender=gender)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201



if __name__ == '__main__':
    app.run(debug=True)
