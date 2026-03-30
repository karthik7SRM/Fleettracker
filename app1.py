from flask import Flask, render_template, request, redirect, session, send_file
import mysql.connector
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import orangered, orange, yellow, black, white, lightgrey

app = Flask(__name__)
app.secret_key = "secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="karthik",
    database="fleet"
)
cursor = db.cursor(dictionary=True, buffered=True)

def create_pdf_response(title, details, filename):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    p.setStrokeColor(black)
    p.setLineWidth(2)
    p.roundRect(50, 200, 700, 300, 15, stroke=1, fill=0)

    p.setFillColor(orangered)
    p.roundRect(50, 430, 700, 70, 10, stroke=0, fill=1)
    
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(70, 460, "FLEET TRACKER PASS")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(730, 460, title)

    p.setDash(6, 3)
    p.setStrokeColor(lightgrey)
    p.line(550, 200, 550, 430)
    p.setDash() 

    p.setFillColor(black)

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(orangered)
    p.drawString(80, 390, "COMMANDER / CAPTAIN")
    p.setFillColor(black)
    p.setFont("Helvetica", 14)
    p.drawString(80, 370, str(details.get('Captain', details.get('ShipCaptain', 'N/A'))).upper())

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(orangered)
    p.drawString(80, 320, "REGISTRATION / ID")
    p.setFillColor(black)
    p.setFont("Helvetica", 14)
    p.drawString(80, 300, str(details.get('FlightID', details.get('fleetID', 'N/A'))))
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(orangered)
    p.drawString(300, 390, "ROUTE / OPERATIONS")
    p.setFillColor(black)
    p.setFont("Helvetica", 14)
    dep = details.get('Departure', details.get('DeparturePort', '---'))
    arr = details.get('Destination', details.get('ArrivalPort', '---'))
    p.drawString(300, 370, f"{dep} >> {arr}")

    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(orangered)
    p.drawString(300, 320, "MODEL / MANUFACTURER")
    p.setFillColor(black)
    p.setFont("Helvetica", 14)
    p.drawString(300, 300, str(details.get('Aircraft', details.get('ShipModel', 'N/A'))))

    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(orangered)
    p.drawString(570, 390, "BOARDING PASS")
    
    p.setFillColor(black)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(570, 365, str(details.get('FlightID', details.get('fleetID', 'FLEET'))))
    
    p.setFont("Helvetica", 9)
    p.drawString(570, 330, "DATE: 2026-03-30")
    p.drawString(570, 315, "GATE: ALPHA-1")
    p.drawString(570, 300, "CLASS: Passenger")

    p.setFont("Helvetica-Oblique", 8)
    p.setFillColor(lightgrey)
    p.drawCentredString(width/2, 215, "OFFICIAL FLEET RECORD - VALID FOR INTERNAL LOGISTICAL AUTHORIZATION ONLY")

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        if cursor.fetchone():
            session["user"] = email
            return redirect("/dashboard")
        return "Invalid login"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session: return redirect("/")
    cursor.execute("SELECT * FROM flights")
    flights_data = cursor.fetchall()
    flights = [list(f.values()) for f in flights_data]
    return render_template("dashboard.html", flights=flights)

@app.route("/add", methods=["POST"])
def add_flight():
    try:
        data = (
            request.form.get("FlightID"), request.form.get("Aircraft"),
            request.form.get("Manufacturer"), request.form.get("Captain"),
            request.form.get("FuelCapacity"), request.form.get("Departure"),
            request.form.get("Destination"), request.form.get("FlightHours"),
            request.form.get("MaxRange"), request.form.get("CargoWeight"),
            request.form.get("FuelUsed"), request.form.get("Distance"),
            request.form.get("Weather"), request.form.get("Speed"),
            request.form.get("Altitude"), request.form.get("LoadFactor"),
            request.form.get("LastMaintenance"), request.form.get("TicketRevenue"),
            request.form.get("OperatingCost")
        )
        query = "INSERT INTO flights VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, data)
        db.commit()
        return create_pdf_response("FLIGHT MISSION PASS", request.form.to_dict(), f"Flight_{request.form.get('FlightID')}.pdf")
    except Exception as e:
        return f"Error: {e}"

@app.route("/delete/<id>")
def delete(id):
    cursor.execute("DELETE FROM flights WHERE FlightID=%s", (id,))
    db.commit()
    return create_pdf_response("DELETION CONFIRMATION", {"FlightID": id, "Status": "DECOMMISSIONED"}, "delete_conf.pdf")

@app.route("/ships")
def ships():
    if "user" not in session: return redirect("/")
    cursor.execute("SELECT * FROM ships")
    ships_data = cursor.fetchall()
    ships = [list(s.values()) for s in ships_data]
    return render_template("ships.html", ships=ships)

@app.route("/add_ship", methods=["POST"])
def add_ship():
    try:
        data = (
            request.form["fleetID"], request.form["ShipModel"],
            request.form["Manufacturer"], request.form["ShipCaptain"],
            request.form["FuelLoadedLiters"], request.form["FuelConsumedLiters"],
            request.form["DeparturePort"], request.form["ArrivalPort"],
            request.form["VoyageDuration"], request.form["MonthlyDistanceKM"],
            request.form["PayloadWeight"], request.form["WeatherCondition"],
            request.form["AvgSpeed"], request.form["SeaLevelDepth"]
        )
        query = "INSERT INTO ships VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query, data)
        db.commit()
        return create_pdf_response("MARITIME VOYAGE PASS", request.form.to_dict(), f"Ship_{request.form['fleetID']}.pdf")
    except Exception as e:
        return f"Ship Error: {e}"

if __name__ == "__main__":
    app.run(debug=True)
