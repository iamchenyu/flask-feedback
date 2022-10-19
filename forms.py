from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, EqualTo, Length


class UserRegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("username can't be empty"), Length(
        min=1, max=20, message="username length should be between 1 and 20 characters")])

    password = PasswordField("Password", validators=[InputRequired(
        "password can't be empty"), EqualTo("confirm", message="password must match")])

    confirm = PasswordField("Confirm Password", validators=[
                            InputRequired("password can't be empty")])

    email = EmailField("Email Address", validators=[InputRequired("email address can't be empty"), Email(
        "not a valid email address"), Length(max=50, message="email address length should be between 1 and 50 characters")])

    first_name = StringField("First Name", validators=[InputRequired("first name can't be empty"), Length(
        max=30, message="first name length should be between 1 and 30 characters")])

    last_name = StringField("Last Name", validators=[InputRequired("last name can't be empty"), Length(
        max=30, message="last name length should be between 1 and 30 characters")])


class UserEditForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("username can't be empty"), Length(
        min=1, max=20, message="username length should be between 1 and 20 characters")])

    email = EmailField("Email Address", validators=[InputRequired("email address can't be empty"), Email("not a valid email address"), Length(
        min=1, max=50, message="email address length should be between 1 and 50 characters")])

    first_name = StringField("First Name", validators=[InputRequired("first name can't be empty"), Length(
        min=1, max=30, message="first name length should be between 1 and 30 characters")])

    last_name = StringField("Last Name", validators=[InputRequired("last name can't be empty"), Length(
        min=1, max=30, message="last name length should be between 1 and 30 characters")])


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(
        max=100, message="title should be no more than 100 characters")])

    content = StringField("Content", validators=[InputRequired()])
