#!/usr/bin/python
""" SyncToRandomMusic.py
    Uses lightshowpi to sync music to random music.
    Turns all lights on after 3 songs
"""

import MySQLdb
import RPi.GPIO as GPIO
import subprocess
import sys
from Outlet import Outlet

host = "localhost"  # Host the site on local machine
dbusername = "root"  # MYSQL username
dbpassword = "password"  # MYSQL password
dbname = "ChristmasLights"  # Database name

""" Main Function:
    Plays 3 random random songs from a playlist using lightshowpi
    Then turns on all the lights
"""
def main():
    for i in range(0, 3):
        lightshowProcess = subprocess.Popen(
            [
                sys.executable,
                '/home/pi/lightshowpi/py/synchronized_lights.py',
                '--playlist',
                '/home/pi/lightshowpi/music/random/.playlist'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        lightshowProcess.wait()
    setOutlets(getOutlets())

""" Set Outlets:
    Turn on every pin that is in the database
"""
def setOutlets(outlets):
    GPIO.setmode(GPIO.BOARD)
    for o in outlets:
        GPIO.setup(int(o.pin), GPIO.OUT)
        GPIO.output(int(o.pin), 1)

""" Get Outlets:
    Gets the outlets from the MySql database
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
