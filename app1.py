from flask import Flask, render_template, Response,redirect,request,url_for,flash
import cv2
import face_recognition
from datetime import datetime
from flask_login import LoginManager,current_user,login_user,login_required,UserMixin,logout_user
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import uuid as uuid
import os
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from werkzeug.security import generate_password_hash,check_password_hash
from models import Loginform,form,AdminForm,course_form
from sqlalchemy import select,MetaData,create_engine


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SQLALCHEMY_BINDS'] ={'course' : "sqlite:///course.db"}
app.config['SECRET_KEY']="SECRET123"
Bootstrap(app)

db = SQLAlchemy(app)
# Settings for migrations
migrate = Migrate(app, db)

class admin(UserMixin,db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(100), nullable=False, unique=False)
    last_name = db.Column(db.String(100), nullable=False, unique=False)
    username=db.Column(db.String(100), unique=False, nullable=True)
    password_hash= db.Column(db.String(128), nullable=False, unique=False)
   
    def get_id(self):
           return (self.admin_id)
    @property
    def password(self):
        raise AttributeError('Incorrect password')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Name : {self.first_name}"

class course(UserMixin,db.Model):
    course_id=db.Column(db.Integer,primary_key=True)
    course_name=db.Column(db.String(100),nullable=False)
    # group_admin=db.Column(db.String(100),nullable=False)
    course_link=db.Column(db.String(100),nullable=False)
    course_teacher=db.Column(db.Integer,nullable=False)
    def get_id(self):
           return (self.course_id)
    __bind_key__ ='course'
    def __repr__(self):
        return f"Name : {self.course_name}"
        
#Setting up login manager
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='loginAdmin'

#User Loader function
@login_manager.user_loader
def load_user(user_id):
    return admin.query.get(int(user_id))


# #Home Page
# @app.route('/')
# def index():
#     return render_template('Login/login.html')






@app.route('/',methods=["GET","POST"])
def loginAdmin():
    #Loading login form
    form=Loginform()       
    if form.validate_on_submit():
        user=admin.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                #Logging in current user
                login_user(user)
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Incorrect password")
        else:
            flash("User does not exist")
    return render_template("admn/loginAdmin.html",form=form)

#Sign Up page
@app.route('/signUpAdmin',methods=["GET","POST"])
def signUpAdmin():
    forms=AdminForm()
    if forms.validate_on_submit():
        fname=forms.first_name.data
        lname=forms.last_name.data
        user=forms.username.data
        pword=forms.password_hash.data
        pword1=forms.password_hash2.data
        hashed_pword=generate_password_hash(pword,"sha256")

        
        try:
            p = admin(first_name=fname, last_name=lname, username=user,password_hash=hashed_pword)
            db.session.add(p)
            db.session.commit()
            return render_template('admn/successAdmin.html')

        except:
            return render_template('admn/SignUpAdmin.html',form=forms)

    else:
        return render_template('admn/signUpAdmin.html',form=forms)



@app.route('/admin_dashboard',methods=["POST","GET"])
@login_required
def admin_dashboard():
    return render_template("admn/admin_dashboard.html")

@app.route('/courseAdded')
@login_required
def courseAdded():
    courses=course.query.all()
    return render_template("admn/courseAdded.html",course=courses)


@app.route('/successAdmin')
def successAdmin():
    return render_template('admn/successAdmin.html')

@app.route('/add_course',methods=["GET","POST"])
def add_course():
    forms=course_form()
    if forms.validate_on_submit():
        course_name=forms.course_name.data
        course_link=forms.course_link.data

        try:
            p = course(course_name=course_name, course_link=course_link,course_teacher=current_user.admin_id)
            db.session.add(p)
            db.session.commit()
            # courses=course.query.all()
            db.session.commit()
            return redirect(url_for("courseAdded"))

        except:
            return render_template('admn/add_course.html',form=forms)

    else:
        return render_template('admn/add_course.html',form=forms)



@app.route("/myProfileAdmin")
@login_required
def myProfileAdmin():
    return render_template("admn/myProfileAdmin.html")

@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user
    flash("You have logged out")
    return redirect(url_for("login"))


@app.route("/teaches")
@login_required
def teaches():
    courses=course.query.all()
    return render_template("admn/teaches.html",courses=courses)

if __name__=='__main__':
    app.run(debug=True)
