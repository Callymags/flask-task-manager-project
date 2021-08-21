import os
from flask import Flask
# Only import env.py file if the os can find an existing
# file path
if os.path.exists("env.py"):
    import env

# Create an instance of Flask and store it in app var
app = Flask(__name__)


# Test function with a route in it that will
# display some text to window as proof app works
# "/" refers to default root
@app.route("/")
def hello():
    return "Hello"


# Tell app how and where to run application
if __name__ == "__main__":
    # Fetch default IP value from env.py file
    app.run(host=os.environ.get("IP"), 
            port=int(os.environ.get("PORT")),
            debug=True)