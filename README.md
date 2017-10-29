# ChristmasLights


A Project to control Christmas Lights and sync them to music using [lightshowpi](https://bitbucket.org/togiles/lightshowpi/wiki/Home) and the Raspberry Pi.

There are 2 ways to control up to 8 outlets. 
 1. Automated using crontab
 2. A Python/Flask website using MySQL
 
## Automation

To have the lights automatically run use the python scripts in the AutoLights directory
* LightsOff.py - Turns off all of the lights
* LightsOn.py - Turns on all of the lights
* SyncToChristmasMusic - Plays 3 songs from a playlist of Christmas songs
* SyncToOtherMusic - Plays 3 songs from a playlist of Random songs

Use cron to run the lights at certain times by calling the above scripts. The example below will sync lights to music at 5,6,7,8pm every day.
> 0 17,18,19,20 * * * /ChristmasLights/AutoLights/SyncToChristmasMusic.py

## Website Interface

Instead of having the lights automatically turn on, you can have a webiste which controls the lights. There are 4 modes:
* Static - Lights are controlled individually
* Christmas Music - Lights sync to a Christmas song
* Random Music - Lights sync to a random song
* Custom Sequence - Lights are controlled by a programmed sequence

The website updates a MySQL database. This data base is polled by lightController.py to update the physical lights. The database can be found in sql.sql. Import this database and set the username and password in main.py and lightController.py.

To run the website (without deployment):
> sudo python main.py

The default username and password are admin/admin.

To run the controller:
> sudo python lightController.py

## Dependencies

* MySQLdb
* RPi.GPIO
* Flask
* Passlib

## Other

This was just for personal project. You'll probably have to modify my scripts and the lightshowpi configs to meet your own needs. 


 
 
