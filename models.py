from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,FileField, BooleanField,ValidationError,IntegerField
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
    course_link=StringField("Course link",validators=[DataRequired()])
    submit=SubmitField("Submit")

class joinCourse(FlaskForm):
    courseID=IntegerField("Course ID",validators=[DataRequired()])
    submit=SubmitField("Submit")