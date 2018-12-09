import datetime
import json
import os
import sys
import time

import requests

# import pygame
# from pygame import mixer
# import pygame.mixer
from pyo import *


import serial  # rainbow, gameday, unkwn, live, good, bad, win, loss

serFound = True


class Error(Exception):
    """Base class for other exceptions"""
    pass


class RequestDidntWork(Error):
    """Raised when the input value is too large"""
    pass


# from datetime import datetime
timeMin = 120

now = datetime.datetime.now() - datetime.timedelta(minutes=timeMin)  # Gets Time at this moment
date_url = "%d-%02d-%02d" % (now.year, now.month, now.day)  # Formats Date for API

teamID = 12  # Set Team You want to Use

# Adds to the Console Text File
c = open("console.txt", "a+")
c.write("------------------------------------BEGIN------------------------------------\r\n")
c.write("-----------------------------%02d/%02d/%d %02d:%02d:%02d-----------------------------\r\n\r\n" % (
    now.month, now.day, now.year, now.hour, now.minute, now.second))
c.close()


# Method to Print Statement as well as add it to the Console Text File
def printStatement(statement=""):
    c = open("console.txt", "a+")
    print("%s" % statement)
    c.write("%s\r\n" % statement)
    c.close()


# Method to update the JSON Request
def updateURL(new_date=date_url):
    url_new = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=%s&startDate=%s&endDate=%s" % (
        teamID, new_date, new_date)  # String to update the URL
    re = requests.get(url=url_new)  # Request Variable
    updated_json = json.loads(re.text)  # Turned Request into Json Variable

    now = datetime.datetime.now()  # Gets Current Time

    timeChecked = "%d/%d/%d-%d:%02d:%02d" % (
        now.month, now.day, now.year, now.hour, now.minute, now.second)  # String for when it is checked

    return re
    # Prevents Error when Showing Status
    # if 2 < int(updated_json["dates"][0]["games"][0]["status"]["statusCode"]) > 4:
    #     if len(updated_json["dates"]) == 1:
    #         printStatement("Checked on: %s       Status: %s" % (
    #         timeChecked, updated_json["dates"][0]["games"][0]["status"]["abstractGameState"]))
    #     elif len(updated_json["dates"]) == 0:
    #         printStatement("Checked on: %s       Status: NA" % timeChecked)
    # Returns the Request Instead of the JSON

# os.system('./canes_goal-2019.wav &')

try:
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # open serial port
    print(ser.name)  # check which port was really used
    ser.write(b'r')  # Write byte rainbow to serial
    printStatement("Serial: Rainbow")

    printStatement()
    printStatement("Serial Found!")
    printStatement("\tSleeping")
    time.sleep(6)
    printStatement("\tAwake")

    # ser.write(b'p')  # Write byte police to serial
except Exception:
    serFound = False
    printStatement("Serial Not Found.")

url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=%s&startDate=%s&endDate=%s" % (
    teamID, date_url, date_url)  # Sets the URL on first run
printStatement(url)  # Prints URL

printStatement("Setup Complete...")  # Prints out that it is Complete

timeNow = "%d/%d/%d - %d:%02d:%02d" % (now.month, now.day, now.year, now.hour, now.minute, now.second)  # String Date
printStatement("Date: %s" % timeNow)  # Prints the Current Time


print("Pre_Init")
# pygame.mixer.pre_init(44100, 16, 2, 4096)
print("Init")
# pygame.mixer.init()
# mixer.init()
print("Load")
# pygame.mixer.music.load("canes_goal-2019.wav")
# sound = mixer.Sound("canes_goal-2019.wav")

# sound = pygame.mixer.Sound('canes_goal-2019.wav')
print("Play")
# pygame.mixer.music.play()
# sound.play()
#time.sleep(5)
print("Done")


# s = Server().boot()
s = Server(duplex=0).boot()
s.start()
time.sleep(5)
sf = SfPlayer('canes_goal-2019.wav', speed=1, loop=False).out()


# os.system('mpg321 canes_goal-2019.wav &')

canesScore = 0
otherScore = 0

try:
    nhl_yes = updateURL()  # Creates variable for request
    nhlJSON = json.loads(nhl_yes.text)  # Coverts request into JSON

    # Checks to make sure request was OK
    while nhl_yes.status_code == 200:
        printStatement("It Worked!")

        # new_time = datetime.datetime.now()
        # update_date = "%d-%02d-%02d" % (new_time.year, new_time.month, new_time.day)
        # nhl = updateURL(update_date)

        if len(nhlJSON["dates"]) == 0:
            printStatement("No Game Today.")
            if serFound:
                ser.write(b'r')
                printStatement("Serial: Rainbow")
        while len(nhlJSON["dates"]) == 0:
            now = datetime.datetime.now()  # Gets Current Time

            # printStatement("Serial: Police")
            # ser.write(b'p')  # Write byte rainbow to serial

            if now.minute % 5 == 0 and now.second == 0:
                printStatement("")  # Prints Blank Line
                new_time = datetime.datetime.now()  # Gets Current time without changing now
                update_date = "%d-%02d-%02d" % (new_time.year, new_time.month, new_time.day)  # Creates New Date for URL
                nhl = updateURL(update_date)  # Calls Update URL Method and returns request
                nhlJSON = json.loads(nhl.text)  # Converts request into JSON

            time.sleep(1)

        if len(nhlJSON["dates"]) == 1:
            printStatement("Get WOKE! It is Gameday!")

        while len(nhlJSON["dates"]) == 1:
            location = ""  # Creates Variable as a Blank
            locationOther = ""  # Creates Variable as a Blank

            if nhlJSON["dates"][0]["games"][0]["teams"]["away"]["team"]["id"] == teamID:
                location = "away"  # Sets Canes
                locationOther = "home"  # Sets Other Teams
                printStatement("%s are playing." % (nhlJSON["dates"][0]["games"][0]["teams"][location]["team"]["name"]))
            elif nhlJSON["dates"][0]["games"][0]["teams"]["home"]["team"]["id"] == teamID:
                location = "home"  # Sets Canes
                locationOther = "away"  # Sets Other Teams
                printStatement("%s are playing." % (nhlJSON["dates"][0]["games"][0]["teams"][location]["team"]["name"]))
            else:
                print("Could not find the Canes!")
                raise Error  # Raises error if canes are not home or away

            main_name = nhlJSON["dates"][0]["games"][0]["teams"][location]["team"]["name"]
            # Prints out if Canes are home or away
            printStatement("The %s are %s" % (main_name, location))
            printStatement()  # Inserts Blank Line

            statusCode = int(nhlJSON["dates"][0]["games"][0]["status"]["statusCode"])

            # rainbow(r), gameday(g), unkwn(u), live(l), good(c), bad(b), win(w), loss(o)
            if statusCode == 1 or statusCode == 2:
                if serFound:
                    ser.write(b'g')
                    printStatement("Serial: Gameday")
            # Status is Preview #
            while statusCode == 1 or statusCode == 2:
                time.sleep(0.5)

                now = datetime.datetime.now()  # Gets Current Time

                if now.minute % 5 == 0 and now.second == 0:
                    printStatement("")  # Prints Blank Line
                    new_time = datetime.datetime.now()  # Gets Current time without changing now
                    update_date = "%d-%02d-%02d" % (
                        new_time.year, new_time.month, new_time.day)  # Creates New Date for URL
                    nhl = updateURL(update_date)  # Calls Update URL Method and returns request
                    nhlJSON = json.loads(nhl.text)  # Converts request into JSON
                    statusCode = int(nhlJSON["dates"][0]["games"][0]["status"]["statusCode"])  # Updates Status Code

            # Status is In Progress or In Progress - Critical #
            printStatement("Set Score!")
            while statusCode == 3 or statusCode == 4:
                now = datetime.datetime.now()
                if now.second % 30 == 0:
                    if serFound:
                        ser.write(b'l')
                        printStatement("Serial: Live")
                if location is None or locationOther is None:
                    raise Error

                time.sleep(0.25)  # Sleeps so it doesnt constantly request

                g_NHL = nhlJSON["dates"][0]["games"][0]  # Shrinks nhlJSON to just the part you need

                # printStatement("%s to %s" % (canesScore, otherScore))

                if g_NHL["teams"][location]["score"] != canesScore:
                    printStatement("%s scored!" % (g_NHL["teams"][location]["team"]["name"]))
                    printStatement(
                        "%s to %s" % (g_NHL["teams"][location]["score"], g_NHL["teams"][locationOther]["score"]))
                    if serFound:
                        # os.system('mpg321 canes_goal-2019.wav &')
                        # sound.play()
                        time.sleep(5)
                        printStatement("Serial: Good Guy Score")
                        ser.write(b'c')

                if int(g_NHL["teams"][locationOther]["score"]) != otherScore:
                    printStatement("%s scored..." % (g_NHL["teams"][locationOther]["team"]["name"]))
                    printStatement(
                        "%s to %s" % (g_NHL["teams"][location]["score"], g_NHL["teams"][locationOther]["score"]))
                    if serFound:
                        printStatement("Serial: Bad Guy Score")
                        ser.write(b'b')

                canesScore = g_NHL["teams"][location]["score"]
                otherScore = g_NHL["teams"][locationOther]["score"]

                game_feed_url = "https://statsapi.web.nhl.com%s" % g_NHL["link"]
                game_req = requests.get(url=game_feed_url)  # Request Variable
                game_json = json.loads(game_req.text)

                intm = game_json["liveData"]["linescore"]["intermissionInfo"]["inIntermission"]
                while intm:
                    if serFound:
                        ser.write(b'i')
                        printStatement("Serial: Intermission")
                        time.sleep(4)
                    game_req = requests.get(url=game_feed_url)  # Request Variable
                    game_json = json.loads(game_req.text)

                    intm = game_json["liveData"]["linescore"]["intermissionInfo"]["inIntermission"]

                # printStatement("%s to %s" % (canesScore, otherScore))

                # printStatement("")  # Prints Blank Line
                nhl = updateURL()  # Calls Update URL Method and returns request
                nhlJSON = json.loads(nhl.text)  # Converts request into JSON
                statusCode = int(nhlJSON["dates"][0]["games"][0]["status"]["statusCode"])  # Updates Status Code

            if 4 < statusCode < 7:
                ser.write(b'u')
                printStatement("Serial: Unkown")
            # Status is Unknown #
            while 4 < statusCode < 6:
                now = datetime.datetime.now()
                timeNow = "%d/%d/%d - %d:%02d:%02d" % (now.month, now.day, now.year, now.hour, now.minute, now.second)

                if now.minute % 5 == 0 and now.second == 0:
                    gameState = nhlJSON["dates"][0]["games"][0]["status"]["statusCode"]
                    gameStatus = nhlJSON["dates"][0]["games"][0]["status"]["detailedState"]

                    f = open("GameState_%s.txt" % gameState, "w+")  # Creates File to store unknown status
                    f.write("Game State \"%s\" means that the status is \"%s\"\r\nDate: %s\r\n" % (
                        gameState, gameStatus, timeNow))  # Writes to file with status
                    f.close()  # Closes File

                    printStatement("")  # Prints Blank Line
                    try:
                        new_time = datetime.datetime.now()  # Gets Current time without changing now
                        update_date = "%d-%02d-%02d" % (
                            new_time.year, new_time.month, new_time.day)  # Creates New Date for URL
                        nhl = updateURL(update_date)  # Calls Update URL Method and returns request
                        nhlJSON = json.loads(nhl.text)  # Converts request into JSON
                        statusCode = int(nhlJSON["dates"][0]["games"][0]["status"]["statusCode"])  # Updates Status Code
                    except Exception:
                        printStatement("Whoops!")

            # Status is Final #
            while statusCode == 6 or statusCode == 7:
                time.sleep(60)

                printStatement("")  # Prints Blank Line
                new_time = datetime.datetime.now()  # Gets Current time without changing now
                update_date = "%d-%02d-%02d" % (
                    new_time.year, new_time.month, new_time.day)  # Creates New Date for URL
                nhl = updateURL(update_date)  # Calls Update URL Method and returns request
                nhlJSON = json.loads(nhl.text)  # Converts request into JSON
                statusCode = int(nhlJSON["dates"][0]["games"][0]["status"]["statusCode"])  # Updates Status Code

                statusCode = nhlJSON["dates"][0]["games"][0]["status"]["statusCode"]

                if serFound:
                    main_score = nhlJSON["dates"][0]["games"][0]["teams"][location]["score"]
                    if main_score > nhlJSON["dates"][0]["games"][0]["teams"][locationOther]["score"]:
                        ser.write(b'w')
                        printStatement("Serial: Win")
                    elif main_score < nhlJSON["dates"][0]["games"][0]["teams"][locationOther]["score"]:
                        ser.write(b'o')
                        printStatement("Serial: Loss")

            if serFound:
                ser.write(b'r')
                printStatement("Serial: Rainbow")

    while nhl.status_code == 404 or 403 or 401 or 400 or 301:
        printStatement("Status")
        if nhl.status_code == 404:
            printStatement("The resource you tried to access wasn't found on the server.")
        elif nhl.status_code == 403:
            printStatement("The resource you're trying to access is forbidden.")
        elif nhl.status_code == 401:
            printStatement("The server thinks you're not authenticated.")
        elif nhl.status_code == 400:
            printStatement("The server thinks you made a bad request.")
        elif nhl.status_code == 301:
            printStatement("The server is redirecting you to a different endpoint.")
        else:
            printStatement("How did you do this?!")
        raise RequestDidntWork


except IOError:
    printStatement('An error occured trying to read the file.')
except ValueError:
    printStatement('Non-numeric data found in the file.')
except ImportError:
    printStatement("NO module found")
except EOFError:
    printStatement('Why did you do an EOF on me?')
except KeyboardInterrupt:
    printStatement()
    printStatement('You cancelled the operation.')
    printStatement()
except RequestDidntWork:
    printStatement("Check the request for API")
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    printStatement('An error occured.')

if serFound:
    ser.write(b'r')
    printStatement("Serial: Rainbow")

    ser.close()
    printStatement("\tSerial Stop")

printStatement("Stopping PyGame!")
# sound.stop()

# Closes the Console Text File
c = open("console.txt", "a+")
c.write(
    "\r\n-------------------------------------END-------------------------------------\r\n\r\n\r\n\r\n\r\n\r\n\r\n")
c.close()
