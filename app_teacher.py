from flask import Flask, render_template, Response,redirect,request,url_for,flash
import cv2
import face_recognition
from datetime import datetime,date,time,timedelta
from flask_login import LoginManager,current_user,login_user,login_required,UserMixin,logout_user
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import uuid as uuid
import os
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from werkzeug.security import generate_password_hash,check_password_hash
from models import Loginform,form,AdminForm,course_form,schedule_Class,attendance_filter
from sqlalchemy import select,MetaData,create_engine


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SQLALCHEMY_BINDS'] ={'course' : "sqlite:///course.db",'scheduleClass' : "sqlite:///scheduleClass.db",'attendance':"sqlite:///attendance.db"}
app.config['SECRET_KEY']="SECRET123"
Bootstrap(app)

db = SQLAlchemy(app)
# Settings for migrations
migrate = Migrate(app, db)


#Databse classes
class attendance(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,default=datetime.now().date(),unique=False)
    time=db.Column(db.Time,default=datetime.now().time(),unique=False)
    student_id=db.Column(db.Integer,nullable=False,unique=False)
    course_id=db.Column(db.Integer,nullable=False,unique=False)

    __bind_key__ ='attendance'
    def __repr__(self):
        return f"Name : {self.id}"

class admin(UserMixin,db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(100), nullable=False, unique=False)
    last_name = db.Column(db.String(100), nullable=False, unique=False)
    username=db.Column(db.String(100), unique=True, nullable=True)
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
    course_teacher=db.Column(db.Integer,nullable=False)
    def get_id(self):
           return (self.course_id)
    __bind_key__ ='course'
    def __repr__(self):
        return f"Name : {self.course_name}"
        
class scheduleClass(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    course_ID=db.Column(db.Integer,nullable=False)
    class_date=db.Column(db.Date,nullable=False)
    class_start_time=db.Column(db.Time ,nullable=False)
    class_end_time=db.Column(db.Time,nullable=False)
    __bind_key__ ='scheduleClass'
    def __repr__(self):
        return f"Name : {self.id}"

#Setting up login manager
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='loginAdmin'

#User Loader function
@login_manager.user_loader
def load_user(user_id):
    return admin.query.get(int(user_id))

#Add Course
@app.route('/add_course',methods=["GET","POST"])
def add_course():
    forms=course_form()
    if forms.validate_on_submit():
        course_name=forms.course_name.data

        try:
            p = course(course_name=course_name ,course_teacher=current_user.admin_id)
            db.session.add(p)
            db.session.commit()
            # courses=course.query.all()
            db.session.commit()
            flash("Course Added successfully. You can see course id in My Courses.")
            return render_template("admn/admin_dashboard.html")

        except:
            return render_template('admn/add_course.html',form=forms)

    else:
        return render_template('admn/add_course.html',form=forms)

#Attendance Report
@app.route('/attendance_report',methods=["GET","POST"])
@login_required
def attendance_report():
    forms=attendance_filter()
    if forms.validate_on_submit():
        course_ID=forms.courseID.data
        date=forms.class_date.data
        courses=course.query.filter_by(course_id=course_ID).first()
        if courses==None:
            flash("This Course doest not exist.")
            return render_template("admn/attendanceReport.html",form=forms)
        if courses.course_teacher==current_user.admin_id:
        # attendance_records=attendance.query(attendance_records).filter_by(attendance_records.student_id.like(current_user.id),attendance_records.course_id.like(course),attendance_records.date.like(date)).all()
            attendance_records=attendance.query.filter_by(course_id=course_ID,date=date).all()
            return render_template("admn/attendanceReport.html",attendance=attendance_records,form=forms)
        else:
            flash("You dont teach this course")
    return render_template("admn/attendanceReport.html",form=forms)

#Dashboard
@app.route('/admin_dashboard',methods=["POST","GET"])
@login_required
def admin_dashboard():
    return render_template("admn/admin_dashboard.html")

#Login Page
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

#Logout
@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user
    flash("You have logged out")
    return redirect(url_for("loginAdmin"))

#My courses
@app.route("/my_courses",methods=["GET","POST"])
@login_required
def my_courses():
    courses=course.query.filter_by(course_teacher=current_user.admin_id).all()
    if courses==None:
        flash("You dont teach any course")
    return render_template("admn/myCourses.html",courses=courses)


#My Profile
@app.route("/myProfileAdmin")
@login_required
def myProfileAdmin():
    return render_template("admn/myProfileAdmin.html")



#Schedule Class
@app.route("/schedule_class",methods=["GET","POST"])
@login_required
def schedule_class():
    forms=schedule_Class()
    if forms.validate_on_submit():
        courseID=forms.courseID.data
        class_date=forms.class_date.data
        class_start_time=forms.class_start_time.data
        class_end_time=forms.class_end_time.data
        courses=course.query.filter_by(course_id=courseID).first()
        if courses==None:
            flash("This Course doest not exist.")
            return render_template('admn/scheduleClass.html',form=forms)

        if courses.course_teacher==current_user.admin_id:
            try:
                p = scheduleClass(course_ID=courseID, class_date=class_date,class_start_time=class_start_time,class_end_time=class_end_time)
                db.session.add(p)
                db.session.commit()
                # courses=course.query.all()
                db.session.commit()
                flash("Class scheduled Sucessfully")
                return redirect(url_for("admin_dashboard"))

            except:
                return render_template('admn/scheduleClass.html',form=forms)
        else:
            flash("You dont teach this course")
            return render_template('admn/scheduleClass.html',form=forms)

    else:
        return render_template('admn/scheduleClass.html',form=forms)


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

#Success
@app.route('/successAdmin')
def successAdmin():
    return render_template('admn/successAdmin.html')


if __name__=='__main__':
    app.run(debug=True)
