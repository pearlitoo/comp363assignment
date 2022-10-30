####### AIR WHAKATŪ FLIGHT MANAGEMENT SYSTEM #######
# Name:  Peter Earl
# Student ID: 1129663
####################################################


##############################################################    READ ME    ####################################################################
# My code is at the point where it can perform every single requirement in the assignment instructions, HOWEVER I have not had enough time
# to control user data input, show examples how the data input should be entered or display error messages for each section as this was something
# I had planned to do at the end of creating all the code functionality. As my code ended up being quite long I was not able to add in these controls 
# everywhere I would have liked, especially as the testing has become quite time consuming. So PLEASE just be careful with your data inputs
# as all of the functions SHOULD work, but the program in its current state is still fragile so often exact input is required. Please be patient and
# thankyou for taking the time to look over my code :D

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import mysql.connector
import connect
import uuid


from mysql.connector import FieldType
import datetime
import connect_to_db_Peter_Earl

dbconn = None

app = Flask(__name__)

def getCursor(): #Connects to MySql
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect_to_db_Peter_Earl.dbuser, \
    password=connect_to_db_Peter_Earl.dbpass, host=connect_to_db_Peter_Earl.dbhost, \
    database=connect_to_db_Peter_Earl.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn

def getID():
    return uuid.uuid4().fields[1]

def columnOutput(dbData,cols,formatStr):
# dbData is a list of tuples
# cols is a dictionary with column name as the key and data type as the item
# formatStr uses the following format, with one set of curly braces {} for each column.
# For each column "{: <10}" determines the width of the column, padded with spaces (10 spaces in this example)
#   <, ^ and > determine the alignment of the text: < (left aligned), ^ (centre aligned), > (right aligned)
#   The following example is for 3 columns of output: left-aligned, 5 characters wide; centred, 10 characters; right-aligned 15 characters:
#       formatStr = "{: <5}  {: ^10}  {: >15}"
# You can also pad with something other than a space and put characters between the columns, 
# e.g. this pads with full stops '.' and separates the columns with the pipe character | :
#       formatStr = "{:.<5} | {:.^10} | {:.>15}"
    print(formatStr.format(*cols))
    for row in dbData:
        rowList=list(row)
        for index,item in enumerate(rowList):
            if item==None:      # Removes any None values from the rowList, which would cause the print(*rowList) to fail
                rowList[index]=""       # Replaces them with an empty string
            elif type(item)==datetime.date or type(item)==datetime.datetime or type(item)==datetime.time or type(item)==datetime.timedelta:    # If item is a date, date-time, time or timedelta, convert to a string to avoid formatting issues
                rowList[index]=str(item)
        print(formatStr.format(*rowList))   

def listAircraft(): #Displays a list of all the aircraft
    cur = getCursor()
    cur.execute("SELECT * FROM aircraft ORDER BY Manufacturer, RegMark;")
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nAIRCRAFT\n")
    formatStr = "{: ^7}  {: <12}  {: <12}  {: >7} "    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    input("\nPress Enter to continue.")

def listRoutes(): # Displays a list of all flight routes
    cur = getCursor()
    cur.execute("SELECT *\
    FROM(\
    (SELECT FlightNum, AirportName AS Departing, AirportCode AS D_Code\
    FROM airport\
    RIGHT JOIN route \
    ON AirportCode = ArrCode)\
    \
    AS T1\
    \
    INNER JOIN\
    \
    (SELECT AirportName AS Arriving, AirportCode AS A_Code, FlightNum\
    FROM airport\
    RIGHT JOIN route \
    ON AirportCode = DepCode)\
    AS T2\
    \
    ON T1.FlightNum = T2.FlightNum)")
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nROUTES\n")
    formatStr = "| {: <11} |  {: <25} |  ({:.<6})  |  {: <25} |  ({:.<6})  |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    input("\nPress Enter to continue.")
 

def listAirportDepArr(): #Gives the user the option to choose to either see a list of flights from a particular airport, edit flights, or return to the main menu
    response=input("\n(L)ist Arrivals and Departures  |  (E)dit  |  or Enter for Main Menu: ").upper()
    if response=='E':
        updateFlight()
    elif response == "L":
        displayFlights()


def updateFlight(): # Gives the user the ability to update specific flights, I should have broken this up into multiple functions but I didn't realise it would get this big
    flightID = str(input("\nPlease enter the flight ID for the flight you would like to update (e.g. 10427): ")) #Chose the specifc flight to be updated
    response1=input("\nWould you like to update the scheduled depature time y/n?: ").upper() # TODO Ideally There would be control only letting the user enter a y or n, or displaying an error message for invalid input, or just returning them to the main menu
    if response1=='Y':
        depTime = str(input("\nPlease enter the new scheduled depature time (hrs:mins:sec e.g. 07:10:00): "))
        cur = getCursor()
        cur.execute("UPDATE flight \
            SET DepTime = %s\
            WHERE flightID = %s;", (depTime, flightID,))
    elif response1 == "N":
        pass
    response2=input("\nWould you like to update estimated depature time y/n?: ").upper()
    if response2=='Y':
        depEstAct = str(input("\nPlease enter the new estimated depature time (hrs:mins:sec e.g. 07:10:00): "))     ### TODO automatically calaculate and update flight duration
        cur = getCursor()
        cur.execute("UPDATE flight \
            SET DepEstAct = %s\
            WHERE flightID = %s;", (depEstAct, flightID,))
        cur.execute("   UPDATE flight\
            SET ArrTime = (SELECT ADDTIME(Duration, DepTime));")                 #automatically changes Arrival time by adding duration time to the new updated depature time
    elif response2 == "N":
        pass
    response3=input("\nWould you like to update the scheduled arrival time y/n?: ").upper()
    if response3=='Y':
        ArrTime = str(input("\nPlease enter the new scheduled arrival time (hrs:mins:sec e.g. 07:10:00): "))
        cur = getCursor()
        cur.execute("UPDATE flight \
            SET ArrTime = %s \
            WHERE flightID = %s;", (ArrTime, flightID,))
    elif response3 == "N":
        pass
    response4=input("\nWould you like to update the flight's status y/n?: ").upper()
    if response4=='Y':
        print("1 - On Time")
        print("2 - Delayed")
        print("3 - Departed")
        print("4 - Landed")
        print("5 - Cancelled")
        FlightStatusInput = str(input("\nPlease enter the updated flight's status: "))
        if FlightStatusInput == "1":
            FlightStatus = str("On Time")
        elif FlightStatusInput == "2":
            FlightStatus = str("Delayed")
        elif FlightStatusInput == "3":
            FlightStatus = str("Departed")
        elif FlightStatusInput == "4":
            FlightStatus = str("Landed")
        elif FlightStatusInput == "5":
            FlightStatus = str("Cancelled")
            cur = getCursor()
            cur.execute("UPDATE flight \
	        SET DepEstAct = NULL\
	        WHERE flightID =%s;", (flightID,))
            cur.execute("UPDATE flight \
	        SET ArrEstAct = NULL \
	        WHERE flightID =%s;", (flightID,))                                          ###While this code works to update estimated time status' in SQL I have not had time to be able to make it print "NULL" in python
        else: print ("Incorrect input, looking for a number. For example: 3")           ###TODO Test error message
        cur = getCursor()
        cur.execute("UPDATE flight \
            SET FlightStatus = %s \
            WHERE flightID = %s;", (FlightStatus, flightID,))
    elif response4 == "N":
        pass
    response5=input("\nWould you like to change the aircraft designated for this flight y/n?: ").upper()  ###TODO Control user input, airplane should only be added if it exists on the aircraft list
    if response5=='Y':
        Aircraft = str(input("\nPlease enter the new aircraft (e.g. ZK-NEF): "))
        cur = getCursor()
        cur.execute("UPDATE flight \
            SET AirCraft = %s \
            WHERE flightID = %s;", (Aircraft, flightID,))
        pass
    elif response5 == "N":
        pass
    response6=input("\nWould you like to update another flight y/n?: ").upper()
    if response6=='Y':
        updateFlight()
    elif response6 == "N":
        dispMenu()                                                                                   # TODO add functionality at the end of this function, currently it just returns the user to the main menu but this could be improved


def displayFlights(): # displays a list of incoming and out going flights from a specific airport in a specific week
    crr = getCursor()
    crr.execute("select AirportCode, AirportName from airport;") # shows the user what airport codes currently exist to choose from
    dbOutput = crr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in crr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <12} | {: <25} |"    # See columnOutput function for details on formatting options
    print("\nAIRPORT CODES:\n")
    columnOutput(dbOutput,colOutputDict,formatStr)
    airportCode = str(input("\nPlease enter airport code: ")).upper() # lets user enter an airport code, might have been better to give them a menu of options to choose from but this isnt scalable if more airports got added to the data
                                                                      # TODO needs user input control, e.g. limit input to 3 letters only, give error message if non existing code entered ect
    grr = getCursor()
    grr.execute("SELECT DISTINCT WeekNum FROM flight;") #displays a list of currently available weeks
    dbOutput = grr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in grr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <8} |"    # See columnOutput function for details on formatting options
    print("\nWEEKS AVAILABLE:\n")
    columnOutput(dbOutput,colOutputDict,formatStr)
    weekNum = str(input("\nPlease enter week: ")) # creates a variable to be used later with the week the user would like to view # TODO control user input

    cur = getCursor() # sends a query to sql to get all the departing flights for the chosen airport and week
    cur.execute("SELECT FlightID, flight.FlightNum, ArrCode AS DestCode, DestiationAirport, DepTime, DepEstAct, FlightStatus, WeekNum, DepCode\
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
    WHERE DepCode = %s AND WeekNum = %s \
    ORDER BY DepTime;", (airportCode, weekNum))
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nDEPARTURES\n")
    formatStr = "| {: <9} |  {: <10} |  {: <9}  |  {: <25} |  {: <8}  |  {: <10}  |  {: <12} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr) #displays departing flights

    brr = getCursor() # sends a query to sql to get all the arriving flights for the chosen airport and week
    brr.execute("SELECT FlightID, flight.FlightNum, depCode AS SorCode, SourceAirport, ArrTime, ArrEstAct, FlightStatus, WeekNum, ArrCode\
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
    WHERE ArrCode = %s AND WeekNum = %s\
    ORDER BY ArrTime;", (airportCode, weekNum))
    dbOutput = brr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in brr.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nARRIVALS\n")
    formatStr = "| {: <9} |  {: <10} |  {: <9}  |  {: <25} |  {: <8}  |  {: <10}  |  {: <12} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr) #dispalys arriving flights, TODO It would probably be nice to have the arriving flights at the top and departing display below
    answer = input("\n(E)dit  |  Press Enter to continue.").upper() #gives the user the option to edit a flight or return to main menu
    if answer =='E':
        return updateFlight()


def addFlights(): #displays a menu giving users an option for how they would like to add in new flights
    print("\n1 - Edit existing flights") 
    print("2 - Add a single new line")
    print("3 - Copy previous weeks flight schedule")
    print("4 - Go back to main Menu")
    response=input("\nHow would you like to add new flights?: \n").upper() #TODO Control user input
    if response == "1":
        updateFlight()
    elif response == "2":
        addNewFlight()
    elif response == "3":
        copyFlightSchedule()
    elif response == "4":
        return dispMenu()
    else:
        print("Invalid Response") # TODO currently the code just crashs for some reason rather than just taking you to the add flights menu
        addFlights()

def addNewFlight():    #Allows the user to add a single flight to the database                                       ### TODO Add options for the user to skip steps or to exit before the end of the function
    grr = getCursor()
    grr.execute("SELECT * FROM route;") #displays a list of currently available routes
    dbOutput = grr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in grr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <9} | {: <8} | {: <8} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    FlightNumber = str(input("\nAdd in Flight Number from the above list: ")).upper()          ### TODO Add input control/data validation  ### TODO Display routes table
    print("\nWEEKS CURRENTLY SCHECDULED:\n")
    grrr = getCursor()
    grrr.execute("SELECT DISTINCT WeekNum FROM flight;") #displays a list of currently available weeks
    dbOutput = grrr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in grrr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <8} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    WeekNum = str(input("\nAdd in Week Number: "))            ### TODO Display existing week numbers
    FlightDate = str(input("Add in Flight Date (yyyy-mm-dd e.g. 2022-08-27): "))            
    DepTime = str(input("Add in DepTime (hrs:mins:sec e.g. 07:10:00): "))                  #TODO Input control
    ArrTime = str(input("Add in ArrTime (hrs:mins:sec e.g. 07:10:00): "))                  #TODO Arrival time should not be before depature time, estimated times should not be before scheduled times
    DepEstAct = str(input("Add in DepEstAct (hrs:mins:sec e.g. 07:10:00): "))                             #### TODO remove this and just make it equal scheduled time? ------------- keep for now as the user might want to add in a different scheduled time?
    ArrEstAct = str(input("Add in ArrEstAct (hrs:mins:sec e.g. 07:10:00): "))                            #### TODO remove this and just make it equal scheduled time? --------------Although maybe could ask y/n make estimated time same as scheduled
    Duration = str("04:20:00")
    print("\nPlease select flight status")
    print("1 - On Time")
    print("2 - Delayed")
    print("3 - Departed")
    print("4 - Landed")
    print("5 - Cancelled")
    flightStatus = str(input("Add in FlightStatus : "))
    if flightStatus == "1":
        FlightStatus = "On Time"
    elif flightStatus == "2":
        FlightStatus = "Delayed"
    elif flightStatus == "3":
        FlightStatus = "Departed"
    elif flightStatus == "4":
        FlightStatus = "Landed"
    elif flightStatus == "5":
        FlightStatus = "Cancelled"
    else:
        print ("Invalid input looking for a number e.g. '4'")
        addNewFlight()
    print ("\n Available Aircraft: \n")
    grr = getCursor()
    grr.execute("SELECT RegMark, Manufacturer, Model FROM aircraft;") #displays a list of currently available Aircraft
    dbOutput = grr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in grr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <15} | {: <15} | {: <15} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    Aircraft = str(input("\n Add in Aircraft RegMark from the above list: ")).upper() 
    print ("\n This is the data being entered into the database:    " ,FlightNumber," | " ,WeekNum," | " , FlightDate," | " , DepTime," | " , ArrTime," | " , DepEstAct," | " , ArrEstAct," | " , FlightStatus," | " , Aircraft," | " ,) # TODO ask if the user would like to proceed with adding this update or start again
    infoCheck = str(input("\n Does this look right? y/n: ")).upper()
    if infoCheck == 'N':
        addNewFlight()
    elif infoCheck == "Y":
        bru = getCursor()
        bru.execute("INSERT INTO flight (FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)\
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); ", (FlightNumber, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft,)) #sends query to mysql to insert the new row
        bru = getCursor()
        bru.execute("UPDATE flight SET Duration = (SELECT TIMEDIFF(ArrTime, DepTime));")    ###This automatically calucates the difference between arivals and depatures to give duration time
        response=input("\n Would you like to add another flight y/n?: ").upper()
        if response=='Y':
            addNewFlight()
        elif response == "N":
            dispMenu()   
    
    
    #### TODO ask user if they would like to (a) add in another flight (b) return to add flight menu or (c) return to main menu


def copyFlightSchedule(): #copys flight schedule from the users chosen week and adds it into the chosen week. flight dates are updated to be one week in advance however the user might not always be creating the new schedule one week in advance
    grr = getCursor()
    grr.execute("SELECT DISTINCT WeekNum FROM flight;")
    dbOutput = grr.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in grr.description}  # creates a dictionary with column name as the key and data type as the item
    formatStr = "| {: <8} |"    # See columnOutput function for details on formatting options
    print("\nWEEKS AVAILABLE:\n")
    columnOutput(dbOutput,colOutputDict,formatStr)
    weekNumToCopy = str(input("\nPlease select a week to copy: ")) #TODO Control user input
    weekNumToCreate = str(input("\nPlease enter the week number you would like to insert the copied schedule into: ")) #TODO Control user input
    brr = getCursor() 
    brr.execute("CREATE TABLE T1 AS\
    SELECT FlightID, FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
    FROM flight\
    WHERE WeekNum = %s;",(weekNumToCopy,))
    brr.execute("UPDATE T1\
    SET WeekNum = %s;",(weekNumToCreate,))
    brr.execute("UPDATE T1\
    SET FlightDate = FlightDate + INTERVAL 7 DAY;") ### updates the dates to be one week in advance
    brr.execute("UPDATE T1\
    SET DepEstAct = DepTime;") ## the following few lines update the estimated times to be the same as scheduled times and resets flight status to "on time"
    brr.execute("UPDATE T1\
    SET ArrEstAct = ArrTime;")
    brr.execute("UPDATE T1\
    SET FlightStatus = 'On time';")
    brr.execute("INSERT INTO airline.flight \
    (FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft)\
    SELECT FlightNum, WeekNum, FlightDate, DepTime, ArrTime, Duration, DepEstAct, ArrEstAct, FlightStatus, Aircraft\
    FROM T1;") 
    brr.execute("DROP TABLE T1;")
    cur = getCursor() 
    cur = getCursor()
    cur.execute("SELECT * FROM flight;")
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nUPDATED FLIGHT LIST\n")
    formatStr = "| {: <8} | {: <9} | {: <8} | {: <11} | {: <10} | {: <10} | {: <11} | {: <10} | {: <11} | {: <12} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    input("\nPress Enter to continue.")
    #### TODO Would you like to (a) add individual flights (b) edit flight details or (c) return to the main menu



def depRunwayLength(): ### compares airport runway length to the planes min runway length
    brr = getCursor() 
    brr.execute("CREATE TABLE T3\
    SELECT FlightID, T1.FlightNum, Aircraft, Manufacturer, Model, Seating, MinRunwayLength, DepCode, MaxRunwayLength, (MaxRunwayLength - MinRunwayLength) AS safteyMargin\
    FROM(\
    (SELECT *\
    FROM flight\
    RIGHT JOIN aircraft \
    ON Aircraft = RegMark)\
    AS T1\
    \
    INNER JOIN\
    \
    (SELECT *\
    FROM airport\
    RIGHT JOIN route \
    ON AirportCode = DepCode)\
    AS T2\
    \
    ON T1.FlightNum = T2.FlightNum)\
    ORDER BY safteyMargin ASC;")
    brr.execute("DELETE FROM T3 \
    WHERE FlightID NOT IN\
    (SELECT MIN(FlightID) as id\
    FROM (select * from T3) as T4\
    GROUP BY Model, DepCode);")
    cur = getCursor()
    cur.execute("SELECT * FROM T3;")
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nDEPATRUE CHECK\n")
    formatStr = "| {: <8} | {: <9} | {: <8} | {: <12} | {: <12} | {: <8} | {: <15} | {: <8} | {: <15} | {: <12} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    brrr = getCursor()
    brrr.execute("drop TABLE T3;")
    input("\nPress Enter to continue.")

def arrRunwayLength(): ### compares airport runway length to the planes min runway length
    brr = getCursor() 
    brr.execute("CREATE TABLE T3\
    SELECT FlightID, T1.FlightNum, Aircraft, Manufacturer, Model, Seating, MinRunwayLength, ArrCode, MaxRunwayLength, (MaxRunwayLength - MinRunwayLength) AS safteyMargin\
    FROM(\
    (SELECT *\
    FROM flight\
    RIGHT JOIN aircraft \
    ON Aircraft = RegMark)\
    AS T1\
    \
    INNER JOIN\
    \
    (SELECT *\
    FROM airport\
    RIGHT JOIN route \
    ON AirportCode = ArrCode)\
    AS T2\
    \
    ON T1.FlightNum = T2.FlightNum)\
    ORDER BY safteyMargin ASC;")
    brr.execute("DELETE FROM T3 \
    WHERE FlightID NOT IN\
    (SELECT MIN(FlightID) as id\
    FROM (select * from T3) as T4\
    GROUP BY Model, ArrCode);")
    cur = getCursor()
    cur.execute("select * from T3;")
    dbOutput = cur.fetchall()
    colOutputDict = {desc[0]:FieldType.get_info(desc[1]) for desc in cur.description}  # creates a dictionary with column name as the key and data type as the item
    print("\nARRIVAL CHECK\n")
    formatStr = "| {: <8} | {: <9} | {: <8} | {: <12} | {: <12} | {: <8} | {: <15} | {: <8} | {: <15} | {: <12} |"    # See columnOutput function for details on formatting options
    columnOutput(dbOutput,colOutputDict,formatStr)
    brrr = getCursor()
    brrr.execute("drop TABLE T3;")
    input("\nPress Enter to continue.")

#function to display the menu
def dispMenu():
    print("\n==== WELCOME TO AIR WHAKATŪ FLIGHT MANAGEMENT SYSTEM ====\n")
    print("1 - Aircraft")
    print("2 - Routes")
    print("3 - Arrivals and Departures")
    print("4 - Add Flights")
    print("5 - Min take off")                            ### TODO 5 and 6 should probably just come under one menu option, AND either display both querys together or have a nested menu to select which option they would like to view
    print("6 - Min landing distance")                    ### TODO additionally it would probably be good to have some kind of alert if the runway margin gets to less than 50 meters for example
    print("R - Menu")
    print("Q - Quit")
    response = input("\nPlease select menu choice: ").upper()
    return response

#Display the menu and prompt the user to select an item
response = dispMenu()
while response != "Q": #repeat this loop until user enters a "Q"
    if response == "1":
        listAircraft()
    elif response == "2":
        listRoutes()
    elif response == "3":
        listAirportDepArr()
    elif response == "4":
        addFlights()    
    elif response == "5":
        depRunwayLength() 
    elif response == "6":
        arrRunwayLength() 
    elif response == "R":
        dispMenu()    
    else:
        print("Invalid response, please re-enter.")
    #Add Runway Safety Margin Report to this menu

    print("")
    #Display the menu and prompt the user to select an item
    response = dispMenu()

print("=== Thank you for using AIR WHAKATŪ FLIGHT MANAGEMENT SYSTEM ===")


