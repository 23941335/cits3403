from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, SubmitField, StringField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

# List of validators https://wtforms.readthedocs.io/en/2.3.x/validators/
# Doubt this is correct, just setting the base
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    # May not be necessary to validate here
    # def validate_username(self, username):
    #     user = db.session.scalar(sa.select(User).where(
    #         User.username == username.data))
    #     if user is None:
    #         raise ValidationError('username is Invalid.')