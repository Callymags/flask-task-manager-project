import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
# Need to render object Id in order to find documents from Mongo DB
from bson.objectid import ObjectId
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
app.secret.key = os.environ.get("SECRET_KEY")

# Set up an instance of PyMongo and add app to it using constructor method
mongo = PyMongo(app)



# Test function with a route in it that will
# display some text to window as proof app works
# "/" refers to default root
@app.route("/")
@app.route('/get_tasks')
def get_tasks():
    # Find all docs from tasks collection and assign them to tasks var 
    tasks = mongo.db.tasks.find()
    # 1st tasks = what template will use, 2nd tasks is tasks var above
    return render_template("tasks.html", tasks=tasks)



# Tell app how and where to run application
if __name__ == "__main__":
    # Fetch default IP value from env.py file
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)