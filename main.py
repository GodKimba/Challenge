from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
ma = Marshmallow(app)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # Just to get rid of the overhed error
app.permanent_session_lifetime = timedelta(days=5)  # This is to store the session for a longer period of time

db = SQLAlchemy(app)



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))

    def __init__(self, name):  # Variables that we must have to create a new object, didn't put id in here because it is a primary_key 
        self.name = name


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    acronym = db.Column(db.String(2))

    def __init__(self, name, acronym):
        self.name = name
        self.acronym = acronym 

class Students_Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_year = db.Column(db.Integer)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # Check if this is the right way to call the others classes
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    class_id = db.Column(db.String(1))
    number = db.Column(db.Integer)

    def __init__(self, school_year, student_id, course_id, class_id, number): 
        self.school_year = school_year
        self.student_id = student_id
        self.course_id = course_id
        self.class_id = class_id
        self.number = number

# Student Schema
#class StudentsSchema(ma.Schema):
    #class Meta:
        #fields = ("id", "name")

# Init Schema
#course_schema = StudentsSchema()
#courses_schema = StudentsSchema(many=True)


# Create a Student
#@app.route("/courses", methods=["POST"])
#def add_courses():
    #name = request.json["name"]
    #acronym = request.json["acronym"]

    #new_courses = Courses(name, acronym)
    #db.session.add(new_courses)
    #db.session.commit()

    #return courses_schema.jsonify(new_courses)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view")
def view():
    return render_template("view.html", values=Users.query.all())
 
#@app.route("/view_all")
#def view_all():
    #return render_template("view_all.html", values=Students.query.all())
  

@app.route("/login", methods=["POST", "GET"])
def login():  # function that implies that the request method sould be POST(secure) and create the user for that session
    if request.method == "POST":
        session.permanent = True  # After user and method are verified we establish that the session is permanent 
        user = request.form["nm"]
        session["user"] = user


        found_user = Users.query.filter_by(name=user).first()  # To find user, filtering by name and first() because its only gonna have 1 user for 1 name
        if found_user:
            session["email"] = found_user.email # Grabbing the email from the database
        else:
            usr = Users(user, "") 
            db.session.add(usr)
            db.session.commit() # Changing the data, so commiting

        flash("Login Successful!")
        return redirect(url_for("user"))
    else:  # If the user is already registered it redirects them to the user page, if not redirects to the login page
        if "user" in session:
            flash("Already Logged In!")
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:  # If user exists the session module saves that info and let access the user page
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = Users.query.filter_by(name=user).first()
            found_user.email = email  # Changing user email and comiting
            db.session.commit()
            flash("Email Was Saved")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        flash("Your're Not Logged In!")
        return redirect(url_for("login")) # If user does not exist the func redirects them to the login page
 

@app.route("/logout")
def logout():  # Simple login out page that pops(removes) the info that was stored for that particular user and than redirects them to login page
    flash(f"You have been logged out!", "info")  # Just flashing a message of logout, only if they were logged in before
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))




if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
