#!/usr/bin/python
""" main.py
    A flask based server-side website
"""


from datetime import timedelta
from flask import Flask, flash, session, render_template, request, url_for, redirect
from user_agents import parse
from passlib.hash import pbkdf2_sha256
import MySQLdb
from Outlet import Outlet
from Mode import Mode

host = "localhost"  # Host the site on local machine
dbusername = "root"  # MYSQL username
dbpassword = "password"  # MYSQL password
dbname = "ChristmasLights"  # Database name

app = Flask(__name__)
# secret key for managing cookies/session
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Ljf/,?K#'
# set session time out to 5 minutes
app.permanent_session_lifetime = timedelta(minutes=5)

""" Set the session modifier when a new request has been made 
"""
@app.before_request
def func():
    session.permanent = True
    session.modified = True  # set the session to be modified if request occurs

""" The root directory
    Returns the html to be displayed
"""
@app.route("/", methods=["GET", "POST"])
def hello():
    # Set the template to be mobile or desktop view
    template = getTemplateAddress(request.user_agent.string, "/control.html")
    # Check if the session is still valid
    if 'username' in session:
        # Check if post/put request
        if request.method == "POST":
            # If it's a post/put, get the mode from the selected box
            selectedMode = request.form['mode']
            modes = getModes()
            # Reverse key/value lookup to set the mode id in the database
            for m in modes:
                if m.name == selectedMode:
                    setMode(m.id)
                    flash("Changed Mode to: " + m.name)
                    break
            # Get the data to send to the template engine
            templateData = {
                'outlets': getOutlets(),
                'modes': getModes(),
                'mode': getCurrentMode()
            }
            return render_template(template, **templateData)
        else:
            # if get request
            # Get the data to send to the template engine
            templateData = {
                'outlets': getOutlets(),
                'modes': getModes(),
                'mode': getCurrentMode()
            }
            return render_template(template, **templateData)

    else:
        # if session ended or never started, force login
        return redirect('/login/')

""" Login 
    Handles the log-in of the user
"""
@app.route("/login/", methods=["GET", "POST"])
def login():
    # Set the template based on mobile or desktop user
    template = getTemplateAddress(request.user_agent.string, "/login.html")
    if request.method == 'POST':
        # if a post/put request, remove currently logged in user from session
        # and get a new username and password from the form
        session.pop('username', 'None')
        username = request.form['username']
        password = request.form['password']
        # check if username/password combo is correct
        if login(username, password):
            templateData = {
                'outlets': getOutlets()
            }
            # Set the username in the session and redirect to root
            session['username'] = username
            return redirect('/')
        else:
            # if invalid credentials, reload login page
            templateData = {}
            flash('Invalid username or password.')
            return render_template(template, **templateData)
    else:
        # if get request, show login page
        templateData = {}
        return render_template(template, **templateData)

""" Change Password
    Allow the user to change their password
"""
@app.route("/changePassword/", methods=["GET", "POST"])
def changePassword():
    # Set the template based on mobile/desktop user
    template = getTemplateAddress(
        request.user_agent.string,
        "/changePassword.html")
    # Check to make sure a valid user is logged in
    if 'username' in session:
        if request.method == 'POST':
            username = session['username']
            # Check to make sure passwords match
            password1 = request.form['password1']
            password2 = request.form['password2']
            if password1 == password2:
                setPassword(session['username'], password1)
                logout()
                flash('Password Changed!')
                return redirect('/')
            else:
                templateData = {}
                flash('Passwords do not match!')
                return render_template(template, **templateData)
        else:
            templateData = {}
            return render_template(template, **templateData)
    else:
        return redirect('/')

""" Logout
    Log the user out of the session
"""
@app.route("/logout/")
def logout():
    # remove the username from the session if it's there
    session.pop('username', 'password')
    flash('You were logged out!')
    return redirect('/')

""" Action
    Perform an action based on an outlet id number
"""
@app.route("/<int:outletId>/<action>/", methods=["GET", "POST"])
def action(outletId, action):
    # Check for valid user
    if 'username' in session:
        # If the action is toggle, toggle the outlet on/off
        if action == "Toggle":
            toggleOutlet(outletId)
            flash("Toggled outlet: " + str(outletId))
            return redirect('/')
        # If the action is edit, render a form to alter the outlet attributes
        elif action == "Edit":
            # If post/put, get data from form and push to database
            if request.method == "POST":
                description = request.form['description']
                pin = int(request.form['pin'])
                # Check for valid Outlet and Pin number
                if 1 <= outletId <= 8:
                    if 1 <= pin <= 24:
                        setOutlet(outletId, pin, description)
                        flash("Edited outlet: " + str(outletId))
                    else:
                        flash("Invalid Pin")
                else:
                    flash("Invalid Outlet Id")
                return redirect('/')
            # If get request, render editing form
            else:
                templateData = {
                    'outlet': getOutlet(outletId)
                }
                return render_template(
                    getTemplateAddress(
                        request.user_agent.string,
                        "/edit.html"),
                    **templateData)
    return redirect('/')

""" Set Status
    Change the status of the lights
"""
@app.route("/setStatus/<int:status>/") # Defaults to get only request
def setStatus(status):
    # Check for valid user
    if 'username' in session:
        # Check for valid status then set it
        if status >= 1 and status <= 4:
            setMode(status)
            return redirect('/')
        else:
            flash("Invalid Mode Selected")
            return redirect('/')
    else:
        return redirect('/')

""" Get Template Address
    Returns the file path to the template to use
"""
def getTemplateAddress(userAgentString, templateAddress):
    # Check user agent by using user_agent module
    userAgent = parse(userAgentString)
    # If mobile user, then use mobile templates
    if (userAgent.is_mobile or userAgent.is_tablet):
        return "/mobile" + templateAddress
    else:
        return templateAddress

""" Get Modes
    Returns an array of modes from the database
"""
def getModes():
    # Connect to MYSQL database
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    # Select Modes
    cur.execute("SELECT id, name FROM mode ORDER BY id")
    modes = []
    for m in cur.fetchall():
        mode = Mode(m[0], m[1])
        modes.append(mode)
    return modes

""" Get Current Mode
    Returns the id of the current mode
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

""" Set Mode
    Sets the current mode in the database
"""
def setMode(id):
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute("UPDATE status SET status = %s WHERE id=1", [int(id)])
    db.commit()

""" Get Outlets
    Returns an array of the outlets in the database
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

""" Get Outlet
    Return a single outlet based on its id
"""
def getOutlet(outletId):
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute(
        "SELECT id, pin, description, status FROM outlet WHERE id=%s ORDER BY id",
        [outletId])
    o = cur.fetchone()
    return Outlet(o[0], o[1], o[2], o[3])

""" Toggle Outlet
    Toggle an outlets status in the database
"""
def toggleOutlet(outletId):
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute(
        "UPDATE outlet SET status=NOT status WHERE id=" +
        str(outletId))
    db.commit()

""" Login
    Return true if username/password match database, otherwise return false
"""
def login(username, password):
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute("SELECT password FROM user WHERE username = %s", [username])
    queryResults = cur.fetchone()
    # Check to make sure valid username
    if queryResults is not None:
        # Check password vs password in database using passlib
        return pbkdf2_sha256.verify(password, queryResults[0])
    else:
        return False

""" Set Password
    Set the users password
"""
def setPassword(username, newPassword):
    # hash and salt password using passlib
    hash = pbkdf2_sha256.encrypt(newPassword, rounds=20, salt_size=8)
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute(
        "UPDATE user SET password = %s WHERE username = %s", [
            hash, username])
    db.commit()

""" Set Outlet
    Update the pin number and description of an outet in the db
"""
def setOutlet(outlet, pin, description):
    db = MySQLdb.connect(
        host=host,
        user=dbusername,
        passwd=dbpassword,
        db=dbname)
    cur = db.cursor()
    cur.execute(
        "UPDATE outlet SET pin=%s, description=%s WHERE id=%s", [
            pin, description, outlet])
    db.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
