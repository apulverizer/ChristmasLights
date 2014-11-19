#!/usr/bin/python
""" LightsOff.py
    Turns every light/outlet in the database off
"""

import MySQLdb
import RPi.GPIO as GPIO
from Outlet import Outlet

host = "localhost"  # Host the site on local machine
dbusername = "root"  # MYSQL username
dbpassword = "password"  # MYSQL password
dbname = "ChristmasLights"  # Database name

""" Main Function:
    Gets the outlets/pins from the database and turns them off
"""
def main():
    outlets = getOutlets()
    setOutlets(outlets)

""" Set Outlets:
    Turn off every pin that is in the database
"""
def setOutlets(outlets):
    GPIO.setmode(GPIO.BOARD)
    for o in outlets:
        GPIO.setup(int(o.pin), GPIO.OUT)
        GPIO.output(int(o.pin), 0)

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
