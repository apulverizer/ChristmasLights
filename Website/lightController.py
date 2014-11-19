#!/usr/bin/python
""" lightController.py
    A script that polls a MYSQL database for changes and then
    updates the outlets/lights accordingly
"""

import MySQLdb
import RPi.GPIO as GPIO
import subprocess
import sys
from Outlet import Outlet
from Mode import Mode
import time

host = "localhost"  # Host the site on local machine
dbusername = "root"  # MYSQL username
dbpassword = "Tennis12"  # MYSQL password
dbname = "ChristmasLights"  # Database name

""" Main
    Loops until killed manually
"""
def main():
    lightshowProcess = None
    while(True):
        # Get the current mode form db
        mode = getCurrentMode()
        # If static mode, set the outlets
        if (mode == 1):
            setOutlets(getOutlets())
            time.sleep(1)
        # If Random Music Mode, spawn subprocess
        elif mode == 2:
            lightshowProcess = subprocess.Popen(
                [
                    sys.executable,
                    '/home/pi/lightshowpi/py/synchronized_lights.py',
                    '--playlist',
                    '/home/pi/lightshowpi/music/random/.playlist'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            # Wait until end of song before moving on
            lightshowProcess.wait()
        # If Christmas Music Mode, spawn subprocess 
        elif mode == 3:
            lightshowProcess = subprocess.Popen(
                [
                    sys.executable,
                    '/home/pi/lightshowpi/py/synchronized_lights.py',
                    '--playlist',
                    '/home/pi/lightshowpi/music/christmas/.playlist'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            # Wait until end of song
            lightshowProcess.wait()
        elif mode == 4:
            # If Custom Sequence Mode, can code your own here light show here
            pass
        else:
            # If invalid mode, default to static
            setOutlets(getOutlets())

""" Set Outlets
    Set the outles on/off based on their status in the db
"""
def setOutlets(outlets):
    GPIO.setmode(GPIO.BOARD)
    for o in outlets:
        GPIO.setup(int(o.pin), GPIO.OUT)
        GPIO.output(int(o.pin), int(o.status))

""" Get Current Mode
    Get the current mode id from db
"""
def getCurrentMode():
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute("SELECT status FROM status WHERE id=1")
    return cur.fetchone()[0]

""" Get Outlets
    Returns an array of outlets from db
"""
def getOutlets():
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute("SELECT id, pin, description, status FROM outlet ORDER BY id")
    outlets = []

    for o in cur.fetchall():
        outlet = Outlet(o[0], o[1], o[2], o[3])
        outlets.append(outlet)
    return outlets


if __name__ == '__main__':
    main()
