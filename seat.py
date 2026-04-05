import mysql.connector
import io
import smtplib
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- Configuration ---
db_config = {
    'user': 'root',
    'password': 'karthik',
    'host': 'localhost',
    'database': 'fleet'
}

# Email Settings (Use a Google App Password)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "karthik.santhanam2007@gmail.com" 
SENDER_PASSWORD = "enunotvnfpfompvj" 

def get_db():
    return mysql.connector.connect(**db_config)

# --- Helper: PDF Generation ---
def generate_boarding_pass(passenger_name, seat_code):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Static Flight Data
    source = "CHENNAI (MAA)"
    destination = "BANGALORE (BLR)"
    gate = "A-12"
    duration = "1h 15m"
    flight_no = "CN-2026"

    # Design the Pass
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, 720, "FLEET TRACKER")
    p.setFont("Helvetica", 12)
    p.drawString(100, 705, "Official Boarding Pass")
    p.line(100, 695, 500, 695)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 660, f"PASSENGER: {passenger_name.upper()}")
    p.drawString(100, 640, f"SEAT: {seat_code}")
    
    p.rect(100, 550, 400, 70) 
    p.setFont("Helvetica", 12)
    p.drawString(110, 595, f"FROM: {source}")
    p.drawString(110, 570, f"TO: {destination}")
    p.drawString(320, 595, f"GATE: {gate}")
    p.drawString(320, 570, f"DURATION: {duration}")

    p.setFont("Helvetica-Oblique", 9)
    p.drawString(100, 520, f"Issued: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- Helper: Send Email ---
def send_email(recipient_email, passenger_name, pdf_buffer, seat_code):
    msg = EmailMessage()
    msg['Subject'] = f"Your Boarding Pass: Seat {seat_code}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email
    msg.set_content(f"Hello {passenger_name},\n\nYour booking is confirmed! Please find your boarding pass attached.\n\nSafe flight!")

    msg.add_attachment(
        pdf_buffer.read(),
        maintype='application',
        subtype='pdf',
        filename=f"BoardingPass_{seat_code}.pdf"
    )

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

# --- Routes ---

@app.route('/')
def index():
    return render_template('seats.html')

@app.route('/api/seats', methods=['GET'])
def get_seats():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("UPDATE reservations SET status='available', hold_expires_at=NULL WHERE status='held' AND hold_expires_at < NOW()")
    conn.commit()
    cursor.execute("SELECT seat_code, status FROM reservations ORDER BY id ASC")
    seats = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(seats)

@app.route('/api/hold', methods=['POST'])
def hold_seat():
    seat_code = request.json.get('seat_code')
    conn = get_db()
    cursor = conn.cursor()
    query = "UPDATE reservations SET status='held', hold_expires_at=DATE_ADD(NOW(), INTERVAL 5 MINUTE) WHERE seat_code=%s AND (status='available' OR (status='held' AND hold_expires_at < NOW()))"
    cursor.execute(query, (seat_code,))
    conn.commit()
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return jsonify({"success": success, "expiry": 300}) if success else (jsonify({"success": False}), 400)

@app.route('/api/book', methods=['POST'])
def book_seat():
    data = request.json
    seat_code, name, email = data.get('seat_code'), data.get('name'), data.get('email')
    
    conn = get_db()
    cursor = conn.cursor()
    query = "UPDATE reservations SET status='booked', passenger_name=%s WHERE seat_code=%s AND status='held' AND hold_expires_at >= NOW()"
    cursor.execute(query, (name, seat_code))
    conn.commit()
    
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()

    if success:
        try:
            pdf = generate_boarding_pass(name, seat_code)
            send_email(email, name, pdf, seat_code)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": True, "error": str(e)}) # Booked but email failed

    return jsonify({"success": False}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)
