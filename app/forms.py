from flask_wtf import FlaskForm
from wtforms import IntegerField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo

# List of validators https://wtforms.readthedocs.io/en/2.3.x/validators/
# Doubt this is correct, just setting the base
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = StringField('Confirm Password', validators=[DataRequired()])