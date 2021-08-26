import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
# Need to render object Id in order to find documents from Mongo DB
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
# Only import env.py file if the os can find an existing
# file path
if os.path.exists("env.py"):
    import env

# Create an instance of Flask and store it in app var
app = Flask(__name__)

# Grabs database name
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
# Configure actual connection string = Mongo_URI
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
# Grab secret key which is a requirement when running flask functions
app.secret_key = os.environ.get("SECRET_KEY")

# Set up an instance of PyMongo and add app to it using constructor method
mongo = PyMongo(app)


# Test function with a route in it that will
# display some text to window as proof app works
# "/" refers to default root
@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    # Find all docs from tasks collection and assign them to tasks var 
    tasks = mongo.db.tasks.find()
    # 1st tasks is what template will use, 2nd tasks is tasks var above
    return render_template("tasks.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Check if requested method is equal to Post
    if request.method == "POST":
        # Check if username already exists within db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # Display flash message to user if username already exists
        if existing_user:
            flash("Username already exists")
            # Redirect user back to register to try again
            return redirect(url_for("register"))

        # If no existing user is found
        register = {
            'username': request.form.get("username").lower(),
            # Use werkzeug security helpers
            'password': generate_password_hash(request.form.get('password'))
        }
        # Call users collection on MongoDB
        mongo.db.users.insert_one(register)

        # Put the new user into session cookie
        session['user'] = request.form.get('username').lower()
        # Display flash message to user after username is placed into session cookie
        flash('Registration Successful!')
        return redirect(url_for('profile', username=session['user']))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {'username':request.form.get('username').lower()})
        
        if existing_user:
            # Ensure hashed password matches user input
            if check_password_hash(
                existing_user['password'], request.form.get('password')):
                    # Put the new user into session cookie
                    session['user'] = request.form.get('username').lower()
                    # Display flash message to user 
                    flash('Welcome, {}'.format(
                        request.form.get('username')))
                    return redirect(url_for(
                        'profile', username=session['user']))
            else:
                # Invalid password
                flash('Incorrect Username and/or Password')
                return redirect(url_for('login'))

        else:
            # Username doesn't exist
            flash('Incorrect Username and/or Password')
            return redirect(url_for('login'))


    return render_template('login.html')


@app.route("/profile/<username>", methods=['GET', 'POST'])
def profile(username):
    # Grab the session user's username from db
    username = mongo.db.users.find_one(
        {'username': session['user']})['username']
    return render_template('profile.html', username=username)



# Tell app how and where to run application
if __name__ == "__main__":
    # Fetch default IP value from env.py file
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)