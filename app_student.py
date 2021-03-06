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
from models import Loginform,form,AdminForm,course_form,joinCourse,attendance_filter
from sqlalchemy import select

#Configuring app, database and image upload path
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
app.config['SQLALCHEMY_BINDS'] ={'course' : "sqlite:///course.db",'attendance' : "sqlite:///attendance.db",'scheduleClass' : "sqlite:///scheduleClass.db",'studies' : "sqlite:///studies.db"}
app.config['SECRET_KEY']="SECRET"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "D:\Engage\static\profile_images"     #Provide profile_images folder complete path here
Bootstrap(app)


#Initialize database
db = SQLAlchemy(app)

# Settings for migrations
migrate = Migrate(app, db)

#Database classes
class attendance(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,default=datetime.now().date(),unique=False)
    time=db.Column(db.Time,default=datetime.now().time(),unique=False)
    student_id=db.Column(db.Integer,nullable=False,unique=False)
    course_id=db.Column(db.Integer,nullable=False,unique=False)

    __bind_key__ ='attendance'
    def __repr__(self):
        return f"Name : {self.id}"

class student(UserMixin,db.Model):
    student_id=db.Column(db.Integer,primary_key=True)
    first_name = db.Column(db.String(100), nullable=False, unique=False)
    last_name = db.Column(db.String(100), nullable=False, unique=False)
    username=db.Column(db.String(100), unique=True, nullable=True)
    password_hash= db.Column(db.String(128), nullable=False, unique=False)
    img=db.Column(db.String(50), nullable=False)
    def get_id(self):
           return (self.student_id)
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

class studies(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_id=db.Column(db.Integer,nullable=False)
    course_id=db.Column(db.Integer,nullable=False)
    def get_id(self):
        return (self.id)
    __bind_key__ ='studies'
    def __repr__(self):
        return f"Name : {self.id}"

#Setting up login manager
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='loginStudent'

#User Loader function
@login_manager.user_loader
def load_user(user_id):
    return student.query.get(int(user_id))

#Attendance Report 
@app.route('/attendance_report',methods=["GET","POST"])
@login_required
def attendance_report():
    forms=attendance_filter()
    if forms.validate_on_submit():
        courseID=forms.courseID.data
        date=forms.class_date.data
        courses=course.query.filter_by(course_id=courseID).first() #Gets list of courses to check whether course exist or not
        attendance_records=attendance.query.filter_by(student_id=current_user.student_id,course_id=courseID,date=date).all()
        if courses==None:   #Null indicates no such course is present
            flash("This Course doest not exist.")
            return render_template("Students/attendanceReport.html",attendance=attendance_records,form=forms)
        return render_template("Students/attendanceReport.html",attendance=attendance_records,form=forms)
    attendance_records=attendance.query.filter_by(student_id=current_user.student_id).all() #By default all records will be shown
    return render_template("Students/attendanceReport.html",attendance=attendance_records,form=forms)



#Get a image
def get_img(id):
    user = student.query.filter_by(student_id=id).first() 
    img = user.img
    if not img:
        return 'Img Not Found!', 404
    return img

#Join Class
@app.route("/join_class",methods=["GET","POST"])
@login_required
def join_class():
    forms=joinCourse()
    if forms.validate_on_submit():
        course_ID=forms.courseID.data
        courses=course.query.filter_by(course_id=course_ID).first()
        studying_courses=studies.query.filter_by(student_id=current_user.student_id,course_id=course_ID).first()
        if courses==None: # Null indicates no course exist with given course id
            flash("Course does not exist.")
            return render_template('Students/joinClass.html',form=forms)
        elif studying_courses==None: # Null indicates Student has not joined this course
            flash("You have not joined this course.")
            return render_template('Students/joinClass.html',form=forms)
        classes=scheduleClass.query.filter_by(course_ID=course_ID).order_by(scheduleClass.id.desc()).first()
        current_time = datetime.now().time()
        now=datetime.now().date()
        #Checking date time of scheduled class with current date and time
        if classes.class_date==now and classes.class_start_time<current_time and classes.class_end_time>current_time: 
            isPresent=mark_attendance()
            if isPresent:
                p = attendance(student_id=current_user.student_id, course_id=course_ID)
                db.session.add(p)
                db.session.commit()
                db.session.close()
                course_link = course.query.filter_by(course_id=course_ID).first()
                return render_template("Students/joinLink.html",link=course_link)
            else:
                return render_template('Students/joinClass.html',form=forms)
        else:
            flash("No Class Scheduled for this course.")
            return render_template('Students/joinClass.html',form=forms)
    return render_template('Students/joinClass.html',form=forms)

#Join Course
@app.route("/join_course",methods=["GET","POST"])
@login_required
def join_course():
    forms=joinCourse()
    if forms.validate_on_submit():
        course_ID=forms.courseID.data
        courses=course.query.filter_by(course_id=course_ID).first()
        studying_courses=studies.query.filter_by(student_id=current_user.student_id,course_id=course_ID).first()
        if courses==None: #Checking whether course exist or not
            flash("Course does not exist.")
            return render_template('Students/joinCourse.html',form=forms)

        elif studying_courses==None: 
            try:
                p = studies(student_id=current_user.student_id, course_id=course_ID)
                db.session.add(p)
                db.session.commit()
                db.session.close()
                flash("Course joined successfully")
                return render_template("Students/student_dashboard.html")
            except:
                flash("Unknown error occured")
                return render_template('Students/joinCourse.html',form=forms)
        else:
            flash("You already study this course.")
            return render_template('Students/joinCourse.html',form=forms)
        
    return render_template('Students/joinCourse.html',form=forms)

#Login Page
@app.route('/',methods=["GET","POST"])
def loginStudent():
    #Loading login form
    form=Loginform()       
    if form.validate_on_submit():
        user=student.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                #Logging in current user
                login_user(user)
                return redirect(url_for('student_dashboard'))
            else:
                flash("Incorrect password")
        else:
            flash("User does not exist")
    return render_template("Students/loginStudent.html",form=form)


#Logout
@app.route("/logout",methods=["GET","POST"])
@login_required
def logout():
    logout_user
    flash("You have logged out")
    return redirect(url_for("loginStudent"))

#Mark Attendance
@app.route("/mark_attendance")
@login_required
def mark_attendance(): 
    isPresent=False
    camera = cv2.VideoCapture(0)
    known_face_encodings = []
    known_face_names = []
    # Load a sample picture and learn how to recognize it.
    users = student.query.filter_by(student_id=current_user.student_id).limit(3).all()
    for user in users:
        image_name=get_img(user.student_id)
        image = face_recognition.load_image_file("static/profile_images/"+image_name)
        orignal_face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(orignal_face_encoding)
        known_face_names.append(image_name)


    # Create arrays of known face encodings and their names
    
    process_this_frame = True
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
           
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []
            
            for face_encoding in face_encodings:
                
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = ""
                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    if name == current_user.img:
                        camera.release()
                        cv2.destroyAllWindows()
                        isPresent=True
                        return isPresent



#My Courses
@app.route("/my_courses",methods=["GET","POST"])
@login_required
def my_courses():
    courses=studies.query.filter_by(student_id=current_user.student_id).all()
    return render_template("Students/myCourses.html",courses=courses)
            
#Profile             
@app.route("/myProfile")
@login_required
def myProfile():
    return render_template("Students/myProfile.html")

#Sign Up page
@app.route('/signUp',methods=["GET","POST"])
def signUp():
    forms=form()
    if forms.validate_on_submit():
        fname=forms.first_name.data
        lname=forms.last_name.data
        user=forms.username.data
        pword=forms.password_hash.data
        pword1=forms.password_hash2.data

        hashed_pword=generate_password_hash(pword,"sha256")

        img = request.files['img']
        img_filename=secure_filename(img.filename)
        img_name=str(uuid.uuid1()) +"_" + img_filename
        img.save(os.path.join(app.config['UPLOAD_FOLDER'],img_name))

        try:
            p = student(first_name=fname, last_name=lname, username=user,password_hash=hashed_pword,img=img_name)
            db.session.add(p)
            db.session.commit()
            db.session.close()
            return render_template('Students/success.html')

        except:
            return render_template('Students/signUp.html',form=forms)

    else:
        return render_template('Students/signUp.html',form=forms)

#Student Dashboard
@app.route('/student_dashboard',methods=["POST","GET"])
@login_required
def student_dashboard():
    return render_template("Students/student_dashboard.html")

#Success Page
@app.route('/success')
def success():
    return render_template('Student/success.html')






if __name__=='__main__':
    app.run(debug=True)
