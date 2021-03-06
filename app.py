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
    tasks = list(mongo.db.tasks.find())
    # 1st tasks is what template will use, 2nd tasks is tasks var above
    return render_template("tasks.html", tasks=tasks)


@app.route('/search', methods=['GET', 'POST'])
def search():
    # ('query') = Query name attribute from form
    query = request.form.get('query')
    # Perform a '$search' on any '$text index' for this collection using the query variable
    tasks = list(mongo.db.tasks.find({'$text': {'$search': query}}))
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

    if session['user']:
        return render_template('profile.html', username=username)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    flash('You have been logged out')
    # Remove user from session cookies
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    # Check to see if requested method is a Post method
    if request.method == 'POST':
        # Ternary operator to deal with is_urgent item in dict
        is_urgent = 'on' if request.form.get('is_urgent') else 'off'
        task = {
            'category_name': request.form.get('category_name'), 
            'task_name': request.form.get('task_name'), 
            'task_description': request.form.get('task_description'), 
            'is_urgent': is_urgent,
            'due_date': request.form.get('due_date'), 
            'created_by': session['user']
        }
        # If so, insert dictionary above into db
        mongo.db.tasks.insert_one(task)
        flash('Task Successfully Added')
        return redirect(url_for('get_tasks'))
    # Find category names in Mongo DB
    # Sort(1) will sort the category in Alphabetical order
    categories = mongo.db.categories.find().sort('category_name', 1)
    return render_template('add_task.html', categories=categories)


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    # Check to see if requested method is a Post method
    if request.method == 'POST':
        # Ternary operator to deal with is_urgent item in dict
        is_urgent = 'on' if request.form.get('is_urgent') else 'off'
        submit = {
            'category_name': request.form.get('category_name'), 
            'task_name': request.form.get('task_name'), 
            'task_description': request.form.get('task_description'), 
            'is_urgent': is_urgent,
            'due_date': request.form.get('due_date'), 
            'created_by': session['user']
        }
        # Search for a task in db by the task Id coming from the route
        # Update task with submit dictionary above once task Id is found
        mongo.db.tasks.update({'_id': ObjectId(task_id)}, submit)
        flash('Task Successfully Updated')

    # Retrieve task you want to edit from db
    # _id is primary key that identifies specific task
    task = mongo.db.tasks.find_one({'_id': ObjectId(task_id)})

    # Grab list of categories and render template
    categories = mongo.db.categories.find().sort('category_name', 1)
    return render_template('edit_task.html', task=task, categories=categories)


@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    # Get specific task by Object Id and delete it
    mongo.db.tasks.remove({'_id': ObjectId(task_id)})
    flash('Task Successfully Deleted')
    # Redirect user back to primary function for the home page
    return redirect(url_for('get_tasks'))


@app.route('/get_categories')
def get_categories():
    # Store data in categories var 
    # Convert to list that is sorted alphabetically
    categories = list(mongo.db.categories.find().sort('category_name', 1))
    # 1st categories = what gets passed into our template to use
    # 2nd categories = categories var defined above
    # Which is the data returned from db
    return render_template('categories.html', categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        # Post method to create dictionary to be inserted into db
        category =  {
            'category_name': request.form.get('category_name')
        }
        mongo.db.categories.insert_one(category)
        flash('New Category Added')
        return redirect(url_for('get_categories'))
    # Get method will display the empty form to the admin
    return render_template('add_category.html')


@app.route('/edit_category/<category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    if request.method == 'POST':
        # Submit new data via dictionary
        submit = {
            'category_name': request.form.get('category_name')
        }
        # Update method takes two dictionaries
        # 1st = which specific category we want to update
        # 2nd = submit dictionary
        mongo.db.categories.update({'_id': ObjectId(category_id)}, submit)
        flash('Category Successfully Updated')
        return redirect(url_for('get_categories'))

    category = mongo.db.categories.find_one({'_id': ObjectId(category_id)})
    # 1st category = what gets passed into our template to use
    # 2nd category = categories var defined above
    # Which is the data returned from db
    return render_template('edit_category.html', category=category)

# Dont need POST method because we are not sending anything to db
# Don't need to insert GET as it is the default method
@app.route('/delete_category/<category_id>')
def delete_category(category_id):
    # Remove() takes a dictionary that will look for specific ObjectId
    # ObjectID is passed through as an argument in the template above as <category_id>
    mongo.db.categories.remove({'_id': ObjectId(category_id)})
    flash('Category Siccessfully Deleted')
    return redirect(url_for('get_categories'))

# Tell app how and where to run application
if __name__ == "__main__":
    # Fetch default IP value from env.py file
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)