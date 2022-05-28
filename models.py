from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,FileField, BooleanField,ValidationError,IntegerField,DateField,TimeField,DateTimeField
from wtforms.validators import DataRequired,EqualTo




class form(FlaskForm):
    first_name=StringField("First Name",validators=[DataRequired()])
    last_name=StringField("Last Name",validators=[DataRequired()])
    username=StringField("Username",validators=[DataRequired()])
    password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_hash2')])
    password_hash2=PasswordField("Re-enter Password",validators=[DataRequired()])
    img=FileField("Profile Image")
    submit=SubmitField("Submit")

class Loginform(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class AdminForm(FlaskForm):
    first_name=StringField("First Name",validators=[DataRequired()])
    last_name=StringField("Last Name",validators=[DataRequired()])
    username=StringField("Username",validators=[DataRequired()])
    password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_hash2')])
    password_hash2=PasswordField("Re-enter Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class course_form(FlaskForm):
    course_name=StringField("Course Name",validators=[DataRequired()])
    submit=SubmitField("Submit")

class joinCourse(FlaskForm):
    courseID=IntegerField("Course ID",validators=[DataRequired()])
    submit=SubmitField("Submit")

class schedule_Class(FlaskForm):
    courseID=IntegerField("Course ID to schedule",validators=[DataRequired()])
    class_date=DateField("Select Date",validators=[DataRequired()])
    class_start_time=TimeField("Select Start Time",validators=[DataRequired()])
    class_end_time=TimeField("Select End Time",validators=[DataRequired()])
    submit=SubmitField("Schedule Class")

class attendance_filter(FlaskForm):
    courseID=IntegerField("Course ID",validators=[DataRequired()])
    class_date=DateField("Select Date",validators=[DataRequired()])
    submit=SubmitField("View Report")