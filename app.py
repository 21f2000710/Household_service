#starting of the app
from flask import Flask, render_template, session
from backend.models import db

#app=Flask(__name__)
app=None

def setup_app():
    app=Flask(__name__)
    #Pending here is sqlite connetion
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///householdservice .sqlite3" #having the db file ...pushing to db
    db.init_app(app) #flask app connected to db
    app.app_context().push() #Direct access to other modules
    app.debug=True
    print("Household services app is started")

setup_app()
# @app.route("/")
# def home():
#     return render_template("index.html")

from backend.controllers import *

if __name__=="__main__":
    app.run()