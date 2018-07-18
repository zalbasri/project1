import os
import requests, json

from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Home page where you can login or register
@app.route("/")
def index():
    return render_template("home.html")


@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    # Make sure username is available
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        error1 = "username not available"
        return render_template("home.html", error=error1)

    # Check if password length is appropriate
    elif len(password) < 6:
        error2 = "password must have at least 6 characters"
        return render_template("home.html", error=error2)

    else:
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
        db.commit()
    msg = "You are registered! You can now log in."
    return render_template("home.html", msg=msg)


@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # check if username exists
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
        error = "user does not exist"
        return render_template("home.html", error=error)

    #check if password is correct
    elif db.execute("SELECT password FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        error = "password incorrect"
        return render_template("home.html", error=error)

    #login
    else:
        session.clear()
        session['logged_in'] = True
        session["username"] = username
        msg = "You have successfully logged in."
        return render_template("home.html", msg = msg)


@app.route("/logout", methods=['POST','GET'])
def logout():
    session.clear()
    msg = "You have logged out."
    return render_template("home.html", msg = msg)


@app.route("/search")
def search():
    search = request.form.get("search")
    # This does not work, I don't think it's getting the search from the form or if the 'LIKE %:search' works
    locations = db.execute("SELECT * FROM locations WHERE zip LIKE %:search% OR city LIKE %:search%", {"search": search}).fetchall()

    # Check if there are no results
    if len(locations) == 0:
        return render_template("search.html", no_results = True)

    return render_template("search.html", locations=locations)


# Page for each zipcode
@app.route("/locations/<string:zip>")
def location(zip):
    # Get the location.. I don't think I got the zipcode becasue the program doesn't get the location
    location = db.execute("SELECT * FROM locations WHERE zip = :zip", {"zip": zip}).fetchone()
    latitude = db.execute("SELECT latitude FROM locations WHERE zip = :zip", {"zip": zip})
    longitude = db.execute("SELECT longitude FROM locations WHERE zip = :zip", {"zip": zip})

    # I couldn't find a way to combine latitude and longitude
    link = "https://api.darksky.net/forecast/d2acc0a3f7511c3a114dd4dab62e3b1c/" + str(latitude) + "," + str(longitude)
    weather = requests.get(link).json()
    time = weather["currently"]["time"]
    summary = weather["currently"]["summary"]
    temp = weather["currently"]["time"]
    dew = weather["currently"]["dewPoint"]
    humidity = weather["currently"]["humidity"] * 100.0
    humidityPercent = str(humidity) + "%"
    check_in = db.execute("SELECT * FROM check_ins WHERE zip = :zip", {"zip": zip}).fetchone()
    num = db.execute("SELECT * FROM check_ins WHERE zip = :zip", {"zip": zip}).rowcount

    # Get the name of the user in session.. I am not sure this works
    username = session['username']

    check = False

    # Determine if check in is allowed
    if session['logged_in'] and db.execute("SELECT * FROM check_ins WHERE zip = :zip AND username = :username", {"zip": zip, "username": username}).rowcount == 0:
        check = True
    return render_template("location.html", location=location, time=time, summary=summary, temp=temp, dew=dew, humidityPercent=humidityPercent, check=check)


# So user can check in
@app.route("/check_in")
def check_in(zip):
    comment = request.form.get("comment")
    username = session['username']
    db.execute("INSERT INTO check_ins (zip, comment, username) VALUES (:zip, :comment, :username)", {"zip": zip, "comment": comment, "username": username})
    db.commit()
    return redirect(url_for('locations/<string:zip>'))


@app.route("/api/locations/<string:zip>")
def location_api(zip):

    # Check if zip exists
    if db.execute("SELECT * FROM locations WHERE zip = :zip", {"zip": zip}).rowcount() == 0:
        return jsonify({"error": "Invalid zipcode"}), 404

    num = db.execute("SELECT * FROM check_ins WHERE zip = :zip", {"zip": zip}).rowcount
    return jsonify({
            "place_name": location.city,
            "state": location.state,
            "zip": zip,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "population": location.population,
            "check_ins": num
        })