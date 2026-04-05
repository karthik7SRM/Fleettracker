import mysql.connector
import io
import smtplib
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- 1. Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'karthik',
    'host': 'localhost',
    'database': 'fleet'
}

# --- 2. Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "karthik.santhanam2007@gmail.com" 
SENDER_PASSWORD = "enunotvnfpfompvj" 

def get_db():
    return mysql.connector.connect(**db_config)

# --- 3. Helper: PDF Generation ---
def generate_boarding_pass(passenger_name, seat_code, source, destination, flight_no):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Header
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, 720, "FLEET TRACKER AIRWAYS")
    p.setFont("Helvetica", 12)
    p.drawString(100, 705, f"Official Boarding Pass - Flight {flight_no}")
    p.line(100, 695, 500, 695)

    # Passenger Info
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 660, f"PASSENGER: {passenger_name.upper()}")
    p.drawString(100, 640, f"SEAT: {seat_code}")
    
    # Flight Box
    p.rect(100, 550, 400, 70) 
    p.setFont("Helvetica", 12)
    p.drawString(110, 595, f"FROM: {source.upper()}")
    p.drawString(110, 570, f"TO: {destination.upper()}")
    p.drawString(320, 595, "GATE: A-12")
    p.drawString(320, 570, "BOARDING: 45m prior")

    p.setFont("Helvetica-Oblique", 9)
    p.drawString(100, 520, f"Issued: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- 4. Web Routes ---

@app.route('/')
def index():
    return render_template('seats.html')

# Get all flights for the Dashboard
@app.route('/api/flights', methods=['GET'])
def get_flights():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM passenger_flights")
    flights = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(flights)

# Get seats for a specific Flight ID with sorting
@app.route('/api/seats/<int:flight_id>', methods=['GET'])
def get_seats(flight_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Automatically release expired holds (older than 5 mins)
    cursor.execute("""
        UPDATE reservations 
        SET status='available', hold_expires_at=NULL 
        WHERE status='held' AND hold_expires_at < NOW()
    """)
    conn.commit()
    
    # Sort so 1A comes before 10A
    query = """
        SELECT seat_code, status 
        FROM reservations 
        WHERE flight_id = %s 
        ORDER BY LENGTH(seat_code) ASC, seat_code ASC
    """
    cursor.execute(query, (flight_id,))
    seats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(seats)

# Hold a seat
@app.route('/api/hold', methods=['POST'])
def hold_seat():
    data = request.json
    seat_code = data.get('seat_code')
    flight_id = data.get('flight_id')
    
    conn = get_db()
    cursor = conn.cursor()
    query = """
        UPDATE reservations 
        SET status='held', hold_expires_at=DATE_ADD(NOW(), INTERVAL 5 MINUTE) 
        WHERE seat_code=%s AND flight_id=%s 
        AND (status='available' OR (status='held' AND hold_expires_at < NOW()))
    """
    cursor.execute(query, (seat_code, flight_id))
    conn.commit()
    
    success = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return jsonify({"success": success, "expiry": 300}) if success else (jsonify({"success": False}), 400)

# Finalize Booking and Email PDF
@app.route('/api/book', methods=['POST'])
def book_seat():
    data = request.json
    seat_code = data.get('seat_code')
    flight_id = data.get('flight_id')
    name = data.get('name')
    email = data.get('email')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Update seat to booked
        query = "UPDATE reservations SET status='booked', passenger_name=%s WHERE seat_code=%s AND flight_id=%s AND status='held'"
        cursor.execute(query, (name, seat_code, flight_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            # Fetch Route info for the PDF
            cursor.execute("SELECT source, destination, flight_no FROM passenger_flights WHERE id = %s", (flight_id,))
            f = cursor.fetchone()
            
            # Create PDF
            pdf_buffer = generate_boarding_pass(name, seat_code, f['source'], f['destination'], f['flight_no'])
            
            # Send Email
            msg = EmailMessage()
            msg['Subject'] = f"Confirmed: Flight {f['flight_no']} to {f['destination']}"
            msg['From'] = SENDER_EMAIL
            msg['To'] = email
            msg.set_content(f"Hi {name},\n\nYour seat {seat_code} has been successfully booked. Please find your boarding pass attached.")
            
            # Attach the PDF
            msg.add_attachment(
                pdf_buffer.getvalue(), 
                maintype='application', 
                subtype='pdf', 
                filename=f"BoardingPass_{seat_code}.pdf"
            )
            
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(msg)
                
            return jsonify({"success": True})
        
        return jsonify({"success": False, "message": "Hold expired"}), 400

    except Exception as e:
        print(f"Error during booking: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # Running on Port 8000
    app.run(debug=True, port=8000)
