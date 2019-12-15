from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, equal_to

class LoginForm(FlaskForm):
  #Restrict length of username field to 100 characters to match the VARCHAR(100) data type in the database
  username = StringField("username", validators=[DataRequired(), Length(max=100)])
  password = PasswordField("password", validators=[DataRequired(), Length(max=200)])

class RegisterForm(FlaskForm):
  #Restrict length of username field to 100 characters to match the VARCHAR(100) data type in the database
  username = StringField("username", validators=[DataRequired(), Length(max=100)])
  password = PasswordField("password", validators=[DataRequired(), Length(max=200)])
  reEnterPassword = PasswordField("reEnterPassword", validators=[DataRequired(), Length(max=200), equal_to("password", "Passwords must match")])