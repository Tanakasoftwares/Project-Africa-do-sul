from flask import Flask, request, jsonify
import pyodbc
import uuid
import datetime
import smtplib

app = Flask(__name__)

# Database connection parameters
server = 'USER-PC\\SQLEXPRESS'
database = 'PFA'
username = 'sa'
password = '12345'
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

def send_email(to_email, subject, body):
    # This is a mock function. Replace with your actual email sending logic.
    print(f"Sending email to {to_email}: {subject}\n{body}")

def get_user_by_email(email):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE email = ?", email)
    user = cursor.fetchone()
    conn.close()
    return user

def save_reset_token(user_id, token, expiry):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)", user_id, token, expiry)
    conn.commit()
    conn.close()

def get_reset_token(token):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, expires_at FROM password_resets WHERE token = ?", token)
    reset_info = cursor.fetchone()
    conn.close()
    return reset_info

def update_user_password(user_id, new_password):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", new_password, user_id)
    conn.commit()
    conn.close()

@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    email = request.json.get("email")
    if email:
        user = get_user_by_email(email)
        if user:
            token = str(uuid.uuid4() )
            expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
            save_reset_token(user.id, token, expiry)
            reset_link = f"http://yourdomain.com/reset-password?token={token}"
            send_email(user.email, "Password Reset Request", f"Click the link to reset your password: {reset_link}")
            return jsonify({"message": "Password reset email sent"})
        else:
            return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "Invalid request"}), 400

@app.route("/reset-password", methods=["POST"])
def reset_password():
    token = request.json.get("token")
    new_password = request.json.get("new_password")
    if token and new_password:
        reset_info = get_reset_token(token)
        if reset_info:
            if reset_info.expires_at > datetime.datetime.utcnow():
                update_user_password(reset_info.user_id, new_password)
                return jsonify({"message": "Password has been reset"})
            else:
                return jsonify({"error": "Token has expired"}), 400
        else: 
            return jsonify({"error": "Invalid token"}), 400
    else:
        return jsonify({"error": "Invalid request"}), 400

if __name__ == "__main__":
    app.run(debug=True)
