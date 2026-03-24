from flask import Flask, render_template, request, redirect, session
import mysql.connector

from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.secret_key = "secret"

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="karthik",
    database="fleet"
)
cursor = db.cursor()


# ---------------- AUTH ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
                       (username, email, password))
        db.commit()
        return redirect("/")

    return render_template("signup.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    return render_template("dashboard.html", flights=flights)


# ---------------- ADD FLIGHT ---------------- #

@app.route("/add", methods=["POST"])
def add_flight():
    data = tuple(request.form.values())

    query = """INSERT INTO flights VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                           %s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(query, data)
    db.commit()

    return redirect("/dashboard")


# ---------------- DELETE ---------------- #

@app.route("/delete/<id>")
def delete(id):
    cursor.execute("DELETE FROM flights WHERE FlightID=%s", (id,))
    db.commit()
    return redirect("/dashboard")


# ---------------- UPDATE ---------------- #

@app.route("/update/<id>", methods=["GET", "POST"])
def update(id):
    if request.method == "POST":
        data = tuple(request.form.values())

        query = """UPDATE flights SET Aircraft=%s, Manufacturer=%s, Captain=%s,
                   FuelCapacity=%s, Departure=%s, Destination=%s, FlightHours=%s,
                   MaxRange=%s, CargoWeight=%s, FuelUsed=%s, Distance=%s,
                   Weather=%s, Speed=%s, Altitude=%s, LoadFactor=%s,
                   LastMaintenance=%s, TicketRevenue=%s, OperatingCost=%s
                   WHERE FlightID=%s"""

        cursor.execute(query, data + (id,))
        db.commit()

        return redirect("/dashboard")

    cursor.execute("SELECT * FROM flights WHERE FlightID=%s", (id,))
    flight = cursor.fetchone()
    return render_template("update.html", flight=flight)


@app.route("/ships")
def ships():
    cursor.execute("SELECT * FROM ships")
    data = cursor.fetchall()
    return render_template("ships.html", ships=data)


@app.route("/add_ship", methods=["POST"])
def add_ship():
    data = (
        request.form["fleet_id"],
        request.form["ship_model"],
        request.form["manufacturer"],
        request.form["ship_captain"],
        request.form["fuel_loaded_liters"],
        request.form["fuel_consumed_liters"],
        request.form["departure_port"],
        request.form["arrival_port"],
        request.form["voyage_duration_hrs"],
        request.form["monthly_distance_km"],
        request.form["payload_weight"],
        request.form["weather_condition"],
        request.form["avg_speed"],
        request.form["sea_level_depth"]
    )

    query = """
    INSERT INTO ships (
        fleet_id, ship_model, manufacturer, ship_captain,
        fuel_loaded_liters, fuel_consumed_liters,
        departure_port, arrival_port,
        voyage_duration_hrs, monthly_distance_km, payload_weight,
        weather_condition, avg_speed, sea_level_depth
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, data)
    db.commit()

    return redirect("/ships")

@app.route("/delete_ship/<id>")
def delete_ship(id):
    cursor.execute("DELETE FROM ships WHERE fleet_id=%s", (id,))
    db.commit()
    return redirect("/ships")

@app.route("/update_ship/<id>", methods=["GET", "POST"])
def update_ship(id):
    if request.method == "POST":
        data = (
            request.form["ship_model"],
            request.form["manufacturer"],
            request.form["ship_captain"],
            request.form["fuel_loaded_liters"],
            request.form["fuel_consumed_liters"],
            request.form["departure_port"],
            request.form["arrival_port"],
            request.form["voyage_duration_hrs"],
            request.form["monthly_distance_km"],
            request.form["payload_weight"],
            request.form["weather_condition"],
            request.form["avg_speed"],
            request.form["sea_level_depth"]
        )

        query = """
        UPDATE ships SET
            ship_model=%s,
            manufacturer=%s,
            ship_captain=%s,
            fuel_loaded_liters=%s,
            fuel_consumed_liters=%s,
            departure_port=%s,
            arrival_port=%s,
            voyage_duration_hrs=%s,
            monthly_distance_km=%s,
            payload_weight=%s,
            weather_condition=%s,
            avg_speed=%s,
            sea_level_depth=%s
        WHERE fleet_id=%s
        """

        cursor.execute(query, data + (id,))
        db.commit()

        return redirect("/ships")

    cursor.execute("SELECT * FROM ships WHERE fleet_id=%s", (id,))
    ship = cursor.fetchone()

    return render_template("update_ship.html", ship=ship)

if __name__ == "__main__":
    app.run(debug=True)