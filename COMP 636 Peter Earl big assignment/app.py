## Peter Earl 1129663


from pickle import NONE
from select import select
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash # I have imported a lot of modules some had special download requriements so I am not sure how this code will run for other people

import mysql
import mysql.connector
import connect
import uuid

#connection = None
dbconn = None

from datetime import datetime, timedelta
import re


app = Flask(__name__)
app.secret_key= "123456789"
app.permanent_session_lifetime = (timedelta(minutes = 5))

##TODO Create the standard time variable

dbuser = "root" 
dbpass = "Root" 
dbhost = "localhost" 
dbport = "3306" #I did not see the point in having a seperate file for connecting to my data base, not exactly sure how to run the database online so I have built my website running it locally on my machine
dbname = "airline"



def getCursor(): #Connects to MySql
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=dbuser, \
        password=dbpass, host=dbhost, \
        database=dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn
    
def getID(): #creates new id's
    return uuid.uuid4().fields[1]

@app.route("/") #home page, needs work, currently does not serve any real purpose other than being the first page the user should land on
def home():
    return render_template('home.html')


@app.route("/admin", methods=["POST", "GET"]) #logs the admin in and checks to see if they are a manager or not
def admin():
    cur = getCursor()
    cur.execute("SELECT EmailAddress FROM staff;") #gets a list of staff email addresses which will be used to create a drop box to select from
    select_result = cur.fetchall()
    if request.method  == "POST":
        AdminAccount = request.form ["AdminAccount"] #retrives the account the user selected to login with
        curr = getCursor()
        curr.execute(f"SELECT IsManager FROM staff WHERE EmailAddress = '{AdminAccount}';") #retrives the data with the information about if the employee is a manager or not
        select_result2 = cur.fetchall()
        for i in select_result2:
            i = select_result2[0] #loops take the data oout of the array's to just get a string variable
        for IsManager in i:
            IsManager = i[0]
        if IsManager == 1: #if statement checks to see if the user is a manager or not
            session.permanent = True
            Manager = "Manager"
            flash("Manger is logged in, full permissions are enabled!")
            session["Manager"] = Manager
            return redirect(url_for("adminLoggedIn"))
        elif IsManager == 0:
            session.permanent = True
            Staff = "Staff"
            session["Staff"] = Staff
            flash("Staff is logged in, full permissions are enabled for managers ONLY")
            return redirect(url_for("adminLoggedIn"))
        return render_template('admin.html', select_result=select_result)
    return render_template('admin.html', select_result=select_result)

@app.route("/adminLoggedIn", methods=["POST", "GET"]) #once the employee has logged in this is the page they will land on, which gives them a range of options of data to view/edit
def adminLoggedIn():
    Manager = None
    staff = None
    if "Manager" in session:
        Manager = session["Manager"]
        session.permanent = True
        return render_template('adminLoggedIn.html') #if statement is probably redant as it just creates a session for the employee but this probably could have been done in the previous route
    elif "Staff" in session:
        Staff = session["Staff"]
        session.permanent = True
        return render_template('adminLoggedIn.html')
    return render_template('adminLoggedIn.html')

@app.route("/flightlist", methods=["POST", "GET"])
def flightlist():
    cur = getCursor() #SQL Quiery combines multiple tables to get a list of all the flights with departing and arriving airports, and seating avaialbility
    cur.execute("SELECT FlightID, FlightNum, DepCode, DepatureAirport, ArrCode, AirportName as ArrivalAirport, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, SeatsAvailable\
    FROM\
    (SELECT FlightID, FlightNum, DepCode, AirportName AS DepatureAirport, ArrCode, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, SeatsAvailable\
    FROM\
    (SELECT FlightID, t3.FlightNum, DepCode, ArrCode, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, Seating - SeatsBooked AS SeatsAvailable \
    FROM\
    (SELECT t1.FlightID, FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked\
    FROM\
    (SELECT FlightID, FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating\
    FROM flight\
    INNER JOIN aircraft\
    ON flight.Aircraft = aircraft.RegMark)\
    AS t1\
    \
    INNER JOIN\
    \
    (SELECT\
    FlightID,\
    COUNT(*) AS `SeatsBooked`\
    FROM\
    passengerflight\
    GROUP BY\
    FlightID)\
    AS t2\
    \
    ON t1.FlightID = t2.FlightID)\
    AS t3\
    \
    INNER JOIN route\
    \
    ON t3.FlightNum = route.FlightNum)\
    AS t4\
    \
    INNER JOIN airport\
    \
    ON t4.DepCode = airport.AirportCode)\
    AS t5\
    \
    INNER JOIN airport\
    \
    ON t5.ArrCode = airport.AirportCode;")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('flightlist.html',dbresult=select_result,dbcols=column_names)

@app.route("/passengerdetails", methods=["POST", "GET"]) #displays a list of all of the airlines passengers
def passengerdetails():
    cur = getCursor()
    cur.execute("SELECT * FROM passenger")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template('passengerdetails.html',dbresult=select_result,dbcols=column_names)

@app.route("/flightdetails", methods=["POST", "GET"]) #displays an individual flights manifest
def flightdetails():
    FlightIDD = [request.args.get("flightID")]
    FlightID = FlightIDD[0]
    cur = getCursor()
    cur.execute(f"SELECT FlightID, FlightNum, DepCode, DepatureAirport, ArrCode, AirportName as ArrivalAirport, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, SeatsAvailable\
    FROM\
    (SELECT FlightID, FlightNum, DepCode, AirportName AS DepatureAirport, ArrCode, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, SeatsAvailable\
    FROM\
    (SELECT FlightID, t3.FlightNum, DepCode, ArrCode, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked, Seating - SeatsBooked AS SeatsAvailable \
    FROM\
    (SELECT t1.FlightID, FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating, SeatsBooked\
    FROM\
    (SELECT FlightID, FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft, Seating\
    FROM flight\
    INNER JOIN aircraft\
    ON flight.Aircraft = aircraft.RegMark)\
    AS t1\
    \
    INNER JOIN\
    \
    (SELECT\
    FlightID,\
    COUNT(*) AS `SeatsBooked`\
    FROM\
     passengerflight\
    GROUP BY\
      FlightID)\
      AS t2\
    \
     ON t1.FlightID = t2.FlightID)\
    AS t3\
    \
    INNER JOIN route\
    \
    ON t3.FlightNum = route.FlightNum)\
    AS t4\
    \
    INNER JOIN airport\
    \
    ON t4.DepCode = airport.AirportCode)\
    AS t5\
    \
    INNER JOIN airport\
    \
    ON t5.ArrCode = airport.AirportCode\
    \
    WHERE FlightID = '{FlightID}'")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    curr = getCursor()
    curr.execute(f"SELECT passenger.PassengerID, FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth, LoyaltyTier, FlightID\
    FROM passenger\
    \
    INNER JOIN passengerflight\
    \
    ON passenger.passengerID = passengerflight.passengerID\
    \
    WHERE FlightID = '{FlightID}'")
    select_result2 = curr.fetchall()
    column_names2 = [desc[0] for desc in cur.description]
    return render_template('flightdetails.html',dbresult=select_result,dbcols=column_names, dbresult2=select_result2,dbcols2=column_names2)


@app.route("/userprofile", methods=["POST", "GET"]) ########################################### TODO This page should be ADMIN ACCESS ONLY! currently page is acessed via get method, so anyone can view by simply searching the url, change to post method
def userprofile():
    email = request.args.get("email")
    session["email"] = email                           
    cur = getCursor()
    cur.execute(f"SELECT * FROM passenger WHERE EmailAddress = '{email}';")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    curr = getCursor() #SQL Quiery retrives and displays the passengers flight data TODO sort displayed data by date/time
    curr.execute(f"SELECT passenger.PassengerID, FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
    FROM\
    (SELECT PassengerID, FlightNum, passengerflight.FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
    FROM\
    (SELECT flight.FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
    FROM\
    (SELECT t1.FlightNum, t1.MasterRoute, depature, Arrival\
    FROM\
    (SELECT FlightNum, MasterRoute, AirportName AS depature, MaxRunwayLength\
    FROM route\
    INNER JOIN airport\
    ON DepCode = AirportCode) AS t1\
    \
    INNER JOIN\
    \
    (SELECT FlightNum, MasterRoute, AirportName AS Arrival, MaxRunwayLength\
    FROM route\
    INNER JOIN airport\
    ON ArrCode = AirportCode) AS T2\
    \
    ON t1.FlightNum = t2.FlightNum) AS t3\
    \
    INNER JOIN flight\
    \
    ON flight.FlightNum = t3.FlightNum) AS t4\
    \
    INNER JOIN passengerflight\
    \
    ON passengerflight.FlightID = t4.FlightID) as t5\
    \
    INNER JOIN passenger\
    \
    ON passenger.PassengerID = t5.PassengerID\
    \
    WHERE EmailAddress = '{email}';")
    select_result2 = cur.fetchall()
    column_names2 = [desc[0] for desc in cur.description]
    return render_template('userprofile.html',dbresult=select_result,dbcols=column_names, dbresult2=select_result2,dbcols2=column_names2)


@app.route("/Arrivals & Depatures/", methods = ['GET']) #this route displays a list of incoming and outgoing flights relevant to a chosen airport ##TODO Needs to filter by time to only show the next 5 days and previous 2 days
def ArrivalsAndDepatures():
    airport = [request.args.get("airport")]
    cur = getCursor()
    cur.execute("SELECT FlightID, flight.FlightNum, ArrCode AS DestCode, DestiationAirport, DepTime, DepEstAct, FlightStatus, DepCode, FlightDate\
    FROM(\
    SELECT T1.FlightNum, SourceAirport, DestiationAirport, DepCode, ArrCode\
    FROM (\
    (SELECT AirportName AS DestiationAirport, FlightNum, DepCode, ArrCode\
    FROM airport\
    INNER JOIN route \
    ON AirportCode = ArrCode) AS T1\
    \
    INNER JOIN\
    \
    (SELECT AirportName AS SourceAirport, FlightNum\
    FROM airport\
    INNER JOIN route \
    ON AirportCode = DepCode) AS T2\
    \
    ON T1.FlightNum = T2.FlightNum)) AS T3\
    \
    INNER JOIN flight\
    ON flight.FlightNum = T3.FlightNum\
    WHERE DepCode = %s;",(airport))
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    cur = getCursor()
    cur.execute(
    "SELECT FlightID, flight.FlightNum, depCode AS SorCode, SourceAirport, ArrTime, ArrEstAct, FlightStatus, ArrCode, FlightDate\
    FROM(\
    SELECT T1.FlightNum, SourceAirport, DestiationAirport, DepCode, ArrCode\
    FROM (\
    (SELECT AirportName AS DestiationAirport, FlightNum, DepCode, ArrCode\
    FROM airport\
    INNER JOIN route \
    ON AirportCode = ArrCode) AS T1\
    \
    INNER JOIN\
    \
    (SELECT AirportName AS SourceAirport, FlightNum\
    FROM airport\
    INNER JOIN route \
    ON AirportCode = DepCode) AS T2\
    \
    ON T1.FlightNum = T2.FlightNum)) AS T3\
    \
    INNER JOIN flight \
    \
    ON flight.FlightNum = T3.FlightNum\
    WHERE ArrCode = %s;",(airport))
    select_result2 = cur.fetchall()
    column_names2 = [desc[0] for desc in cur.description]
    return render_template('ArrivalsAndDepatures.html',dbresult=select_result,dbcols=column_names,dbresult2=select_result2,dbcols2=column_names2)


@app.route("/bookings", methods=["POST", "GET"]) #allows user to book and edit flights TODO allow booking of flights
def bookings():
    email = None
    if "email" in session:
        email = session["email"]
        cur = getCursor() #SQL Quiery retrives and displays the passengers flight data TODO sort displayed data by date/time                           test account: Jonty_Jensen@gmail.com
        cur.execute(f"SELECT FlightNum, passenger.PassengerID, FlightID, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
        FROM\
        (SELECT PassengerID, FlightNum, passengerflight.FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
        FROM\
        (SELECT flight.FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
        FROM\
        (SELECT t1.FlightNum, t1.MasterRoute, depature, Arrival\
        FROM\
        (SELECT FlightNum, MasterRoute, AirportName AS depature, MaxRunwayLength\
        FROM route\
        INNER JOIN airport\
        ON DepCode = AirportCode) AS t1\
        \
        INNER JOIN\
        \
        (SELECT FlightNum, MasterRoute, AirportName AS Arrival, MaxRunwayLength\
        FROM route\
        INNER JOIN airport\
        ON ArrCode = AirportCode) AS T2\
        \
        ON t1.FlightNum = t2.FlightNum) AS t3\
        \
        INNER JOIN flight\
        \
        ON flight.FlightNum = t3.FlightNum) AS t4\
        \
        INNER JOIN passengerflight\
        \
        ON passengerflight.FlightID = t4.FlightID) as t5\
        \
        INNER JOIN passenger\
        \
        ON passenger.PassengerID = t5.PassengerID\
        \
        WHERE EmailAddress = '{email}';")
        select_result = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]

        curr = getCursor()
        curr.execute(f"SELECT FlightID\
        FROM\
        (SELECT PassengerID, FlightNum, passengerflight.FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
        FROM\
        (SELECT flight.FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
        FROM\
        (SELECT t1.FlightNum, t1.MasterRoute, depature, Arrival\
        FROM\
        (SELECT FlightNum, MasterRoute, AirportName AS depature, MaxRunwayLength\
        FROM route\
        INNER JOIN airport\
        ON DepCode = AirportCode) AS t1\
        \
        INNER JOIN\
        \
        (SELECT FlightNum, MasterRoute, AirportName AS Arrival, MaxRunwayLength\
        FROM route\
        INNER JOIN airport\
        ON ArrCode = AirportCode) AS T2\
        \
        ON t1.FlightNum = t2.FlightNum) AS t3\
        \
        INNER JOIN flight\
        \
        ON flight.FlightNum = t3.FlightNum) AS t4\
        \
        INNER JOIN passengerflight\
        \
        ON passengerflight.FlightID = t4.FlightID) as t5\
        \
        INNER JOIN passenger\
        \
        ON passenger.PassengerID = t5.PassengerID\
        \
        WHERE EmailAddress = '{email}';")
        select_result2 = curr.fetchall()
        getid = select_result[0]
        PassengerID = getid[1]
        if request.method == "POST":
            #session.permanent = True
            #email = session["email"]                                 #TODO for some reason getting a "bad request" when trying to get flight id submitted by the user, no apparent reason but possibly to do with the forloop that generates the drop box, specifically the name being repeated
            flightID = request.form ["flightiddropbox"]
            cur = getCursor()
            cur.execute(f"DELETE FROM passengerflight \
            WHERE FlightID = {flightID} AND PassengerID = {PassengerID};")
            flash("Your has been cancelled, login again to see your updated flight list")
            return redirect(url_for("logout"))                                                                                  # test account: Jonty_Jensen@gmail.com
        return render_template('bookings.html', dbresult=select_result,dbcols=column_names, select_result2=select_result2)
    else:
        session.permanent = True
        email = session["email"]
        return render_template("bookings.html")



@app.route("/register", methods=["POST", "GET"]) #allows user to create new account, accessed via the login page
def register():
    if request.method == "POST":
        FirstName = request.form["FirstName"]
        LastName = request.form["LastName"]
        EmailAddress = request.form["EmailAddress"]
        PhoneNumber = request.form["PhoneNumber"]
        PassportNumber = request.form["PassportNumber"]
        DateOfBirth = request.form["DateOfBirth"]
        cur = getCursor()
        cur.execute(f"INSERT INTO passenger (FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth)\
        VALUES ('{FirstName}', '{LastName}', '{EmailAddress}', '{PhoneNumber}', '{PassportNumber}', '{DateOfBirth}');")
        flash(f"Account for {EmailAddress} created succesfully, please login")
        return  redirect(url_for("login"))
    else:
        return render_template("register.html")
# TODO CONTROL USER INPUTS
# TODO prevent users from creating multiple accounts with the same email
# TODO prevent users from creating multiple accounts with the same passport number
# TODO convert emails to lowercase? 


@app.route("/editpersonal", methods=["POST", "GET"]) #similar to the register account page, populates a similar form with the users existing details and allows them to make changes and then the sql query updates the data base
def editpersonal():
    if request.method == "POST":
        session.permanent = True

        email = session["email"]
        cur = getCursor()
        cur.execute(f"SELECT * FROM passenger WHERE EmailAddress = '{email}';")
        select_result = cur.fetchall()
        tupleinlist = select_result[0]
        PassengerID = tupleinlist[0]
        session["PassengerID"] = PassengerID

        FirstName = request.form["FirstName"]
        LastName = request.form["LastName"]
        EmailAddress = request.form["EmailAddress"]
        PhoneNumber = request.form["PhoneNumber"]
        PassportNumber = request.form["PassportNumber"]
        DateOfBirth = request.form["DateOfBirth"]
        cur = getCursor()
        cur.execute(f"\
        UPDATE passenger \
        SET FirstName = '{FirstName}', LastName = '{LastName}', EmailAddress = '{EmailAddress}', PhoneNumber = '{PhoneNumber}', PassportNumber = '{PassportNumber}', DateOfBirth = '{DateOfBirth}'\
        WHERE PassengerID = {PassengerID};")
        flash("Please login again to see updated personal details")
        return  redirect(url_for("logout"))
    else:                                                                       #the else is the pages default and must pre populate the fields while the if actually updates the database apon form submission
        email = session["email"]
        cur = getCursor()
        cur.execute(f"SELECT * FROM passenger WHERE EmailAddress = '{email}';") 
        select_result = cur.fetchall()
        tupleinlist = select_result[0]
        PassengerID = tupleinlist[0]
        session["PassengerID"] = PassengerID
        FirstName = tupleinlist[1]
        LastName = tupleinlist[2]
        EmailAddress = tupleinlist[3]
        PhoneNumber = tupleinlist[4]
        PassportNumber = tupleinlist[5]
        DateOfBirth = tupleinlist[6]
        return render_template("editpersonal.html",FirstName=FirstName,LastName=LastName,EmailAddress=EmailAddress,PhoneNumber=PhoneNumber,PassportNumber=PassportNumber,DateOfBirth=DateOfBirth)


@app.route("/login", methods=["POST", "GET"]) #login page, unfortunately also populates a lot of the data for the user page, this was a design flaw due to it being one of the first things I built and I wasnt sure what I was doing
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        session["email"] = email
        cur = getCursor()
        cur.execute(f"SELECT EmailAddress FROM passenger WHERE EmailAddress = '{email}';")
        sql_email = cur.fetchall()
        if sql_email == []:
            flash("Your email does not match any in our database, please try retyping or if you do not have an account please register below")
            return redirect(url_for("logout")) 
        else:
            brr = sql_email[0] #Takes the email out of the list
            megatron = brr[0] #Takes the email out of the tuple
            if megatron == email:# test to see if the email the user entered matchs whats in the database         test account: Jonty_Jensen@gmail.com
                ###Get personal details and print in user page
                cur = getCursor()
                cur.execute(f"SELECT * FROM passenger WHERE EmailAddress = '{email}';")
                select_result = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]
                curr = getCursor() #SQL Quiery retrives and displays the passengers flight data TODO sort displayed data by date/time
                curr.execute(f"SELECT passenger.PassengerID, FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
                FROM\
                (SELECT PassengerID, FlightNum, passengerflight.FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
                FROM\
                (SELECT flight.FlightNum, FlightID, MasterRoute, depature, Arrival, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
                FROM\
                (SELECT t1.FlightNum, t1.MasterRoute, depature, Arrival\
                FROM\
                (SELECT FlightNum, MasterRoute, AirportName AS depature, MaxRunwayLength\
                FROM route\
                INNER JOIN airport\
                ON DepCode = AirportCode) AS t1\
                \
                INNER JOIN\
                \
                (SELECT FlightNum, MasterRoute, AirportName AS Arrival, MaxRunwayLength\
                FROM route\
                INNER JOIN airport\
                ON ArrCode = AirportCode) AS T2\
                \
                ON t1.FlightNum = t2.FlightNum) AS t3\
                \
                INNER JOIN flight\
                \
                ON flight.FlightNum = t3.FlightNum) AS t4\
                \
                INNER JOIN passengerflight\
                \
                ON passengerflight.FlightID = t4.FlightID) as t5\
                \
                INNER JOIN passenger\
                \
                ON passenger.PassengerID = t5.PassengerID\
                \
                WHERE EmailAddress = '{email}';")
                select_result2 = cur.fetchall()
                column_names2 = [desc[0] for desc in cur.description]
                return render_template('user.html',dbresult=select_result,dbcols=column_names, dbresult2=select_result2,dbcols2=column_names2) # if email matchs then send user to user page
            else:        # else ask user to try retyping their email or to create a new profile if one does not exist
                flash("Your email does not match any in our database, please try retyping or if you do not have an account please register below")
                return redirect(url_for("logout"))        # logs user out and ends the session
    else:
        if "email" in session:
            flash("You are already logged in", "info")
            return redirect(url_for("user"))
        return render_template("login.html")


@app.route("/user", methods=["POST", "GET"])       #populates the user page
def user():
    email = None
    if "email" in session:
        email = session["email"]
        flash(f"{email} is logged in")
        return render_template('user.html', email = email)
    else:
        flash(f"You are not logged in", "info")
        return redirect(url_for("login"))


@app.route("/logout")      #logs the user out and ends all sessions
def logout():
    flash("You have been logged out", "info")
    session.pop("user",None)
    session.pop("email",None)
    session.pop("PassengerID",None)
    session.pop("Staff",None)
    session.pop("Manager",None)
    return redirect(url_for("login"))
