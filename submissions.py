from flask import Flask, request, jsonify
import pyodbc
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Database connection parameters
server = 'USER-PC\\SQLEXPRESS'
database = 'PFA'
username = 'sa'
password = '12345'
driver = '{ODBC Driver 17 for SQL Server}'

def get_db_connection():
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}')
    return conn

def send_email(to_email, subject, message):
    from_email = "tanakasoftwares@gmail.com"
    from_password = "wuyd vfwq ejqi wbxj1"  # Use the app-specific password generated from Google
    
    # Create the email headers and content
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    # Connect to the email server and send the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, from_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

@app.route('/submit', methods=['POST'])
def submit():   
    data = request.form
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('Email')
    country = data.get('country')
    subject = data.get('subject')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO form_submissions (id, firstname, lastname, email, country, subject, created_at)
        VALUES (NEWID(), ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (firstname, lastname, email, country, subject))
    
    conn.commit()
    cursor.close()
    conn.close()

    # Send confirmation email
    email_subject = "Form Submission Confirmation"
    email_message = f"Dear {firstname},\n\nThank you for your submission.\n\nBest regards,\nYour Company"
    send_email(email, email_subject, email_message)
    
    return jsonify({'status': 'success', 'message': 'Data inserted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
