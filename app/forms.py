from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileField
from wtforms.fields import DateTimeLocalField
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, BooleanField, HiddenField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Email, EqualTo, Length, Regexp, Optional
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

    # May not be necessary to validate here
    # def validate_username(self, username):
    #     user = db.session.scalar(sa.select(User).where(
    #         User.username == username.data))
    #     if user is None:
    #         raise ValidationError('username is Invalid.')

class CreateTournamentForm(FlaskForm):
    name = StringField('Tournament Name', validators=[
        InputRequired(message="Tournament Name is required."),
        Length(min=1, max=256, message="Tournament title must be between 1-256 characters")
    ])

    start_time = DateTimeLocalField("Tournament Start Time",format="%Y-%m-%dT%H:%M",validators=[
        InputRequired(message="Tournament Start Time is required.")
    ])
    
    description = StringField('Tournament Description', validators=[
        InputRequired(message="Tournament Description is required."),
        Length(min=1, max=512, message="Description must be between 1-512 characters")
    ])

    visibility = SelectField(
        'Tournament Visibility',  coerce=int,
        validators=[
            DataRequired(message="You must select an option.")
        ]
    )

    # TODO: team validation

    csv_file = FileField(
        'CSV Upload (Optional)',
        validators=[
            Optional(),
            FileAllowed(['csv'], 'CSV files only.')
        ]
    )

    submit = SubmitField("Create Tournament")

class UpdateAccountForm(FlaskForm):
    username = StringField('New Username', validators=[
        Optional(), Length(min=3, max=25)
    ])
    email = StringField('New Email', validators=[
        Optional(), Email(), Length(min=6, max=254)
    ])
    picture = FileField('Update Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Update')

class UserSelectionForm(FlaskForm):
    tid = HiddenField("tid", validators=[DataRequired()])
    selected_users = HiddenField("Selected Users")
    submit = SubmitField("Submit")