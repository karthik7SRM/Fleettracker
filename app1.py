from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="karthik",
    database="fleet"
)
cursor = db.cursor()



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

        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
            (username, email, password)
        )
        db.commit()
        return redirect("/")

    return render_template("signup.html")



@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()
    return render_template("dashboard.html", flights=flights)



@app.route("/add", methods=["POST"])
def add_flight():
    data = tuple(request.form.values())

    query = """INSERT INTO flights VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                           %s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    cursor.execute(query, data)
    db.commit()

    return redirect("/dashboard")



@app.route("/delete/<id>")
def delete(id):
    cursor.execute("DELETE FROM flights WHERE FlightID=%s", (id,))
    db.commit()
    return redirect("/dashboard")



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
    if "user" not in session:
        return redirect("/")

    cursor.execute("SELECT * FROM ships")
    data = cursor.fetchall()
    return render_template("ships.html", ships=data)



@app.route("/add_ship", methods=["POST"])
def add_ship():
    data = (
        request.form["fleetID"],
        request.form["ShipModel"],
        request.form["Manufacturer"],
        request.form["ShipCaptain"],
        request.form["FuelLoadedLiters"],
        request.form["FuelConsumedLiters"],
        request.form["DeparturePort"],
        request.form["ArrivalPort"],
        request.form["VoyageDuration"],
        request.form["MonthlyDistanceKM"],
        request.form["PayloadWeight"],
        request.form["WeatherCondition"],
        request.form["AvgSpeed"],
        request.form["SeaLevelDepth"]
    )

    query = """
    INSERT INTO ships (
        fleetID, ShipModel, Manufacturer, ShipCaptain,
        FuelLoadedLiters, FuelConsumedLiters,
        DeparturePort, ArrivalPort,
        VoyageDuration, MonthlyDistanceKM, PayloadWeight,
        WeatherCondition, AvgSpeed, SeaLevelDepth
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, data)
    db.commit()

    return redirect("/ships")



@app.route("/delete_ship/<id>")
def delete_ship(id):
    cursor.execute("DELETE FROM ships WHERE fleetID=%s", (id,))
    db.commit()
    return redirect("/ships")



@app.route("/update_ship/<id>", methods=["POST"])
def update_ship(id):
    data = (
        request.form["ShipModel"],
        request.form["Manufacturer"],
        request.form["ShipCaptain"],
        request.form["FuelLoadedLiters"],
        request.form["FuelConsumedLiters"],
        request.form["DeparturePort"],
        request.form["ArrivalPort"],
        request.form["VoyageDuration"],
        request.form["MonthlyDistanceKM"],
        request.form["PayloadWeight"],
        request.form["WeatherCondition"],
        request.form["AvgSpeed"],
        request.form["SeaLevelDepth"]
    )

    query = """
    UPDATE ships SET
        ShipModel=%s,
        Manufacturer=%s,
        ShipCaptain=%s,
        FuelLoadedLiters=%s,
        FuelConsumedLiters=%s,
        DeparturePort=%s,
        ArrivalPort=%s,
        VoyageDuration=%s,
        MonthlyDistanceKM=%s,
        PayloadWeight=%s,
        WeatherCondition=%s,
        AvgSpeed=%s,
        SeaLevelDep=%s
    WHERE fleetID=%s
    """

    cursor.execute(query, data + (id,))
    db.commit()

    return redirect("/ships")



if __name__ == "__main__":
    app.run(debug=True)