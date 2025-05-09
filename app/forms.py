from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo, Length, Regexp
import sqlalchemy as sa
from app import db
from app.models import User


USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 25
USERNAME_REGEX = r'^[A-Za-z0-9_]+$'
USERNAME_REGEX_MESSAGE = 'Username can only contain letters, numbers, and underscores.'
USERNAME_LEN_MESSAGE = f'Username must be between {USERNAME_MIN_LEN} and {USERNAME_MAX_LEN} characters long.'

EMAIL_MIN_LEN = 6
EMAIL_MAX_LEN = 254
EMAIL_LEN_MESSAGE = f'Email address length is invalid (max {EMAIL_MAX_LEN} characters).'

PASSWORD_MIN_LEN = 8
PASSWORD_MAX_LEN = 128 
PASSWORD_LEN_MESSAGE = f'Password must be at least {PASSWORD_MIN_LEN} characters long.'

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required."),
        Length(min=USERNAME_MIN_LEN, max=USERNAME_MAX_LEN, message=USERNAME_LEN_MESSAGE),
        Regexp(USERNAME_REGEX, message=USERNAME_REGEX_MESSAGE)
    ])
    email = StringField('Email Address', validators=[
        InputRequired(message="Email is required."),
        Email(message="Invalid email address format."),
        Length(min=EMAIL_MIN_LEN, max=EMAIL_MAX_LEN, message=EMAIL_LEN_MESSAGE)
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required."),
        Length(min=PASSWORD_MIN_LEN, max=PASSWORD_MAX_LEN, message=PASSWORD_LEN_MESSAGE),
        EqualTo('confirm_password', message='Passwords do not match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(message="Please confirm your password.")
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username. This one is already taken.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address. This one is already registered.')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Nickname', validators=[
        InputRequired(), Length(min=3, max=25)
    ])
    email = StringField('Email', validators=[
        InputRequired(), Email()
    ])
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files allowed.')
    ])
    submit = SubmitField('Update')

    # May not be necessary to validate here
    # def validate_username(self, username):
    #     user = db.session.scalar(sa.select(User).where(
    #         User.username == username.data))
    #     if user is None:
    #         raise ValidationError('username is Invalid.')