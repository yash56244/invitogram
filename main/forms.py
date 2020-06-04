from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, IntegerField, SelectMultipleField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from main.models import User
from flask_login import current_user
from datetime import date, datetime

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email already exists!')

class BirthdayForm(FlaskForm):
    name = StringField('Name of person', validators=[DataRequired()])
    birthday_no = IntegerField('Which Birthday?', validators=[DataRequired()])
    date1 = DateField('Date',format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    host_name = StringField('Host Name', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    submit = SubmitField('Send Invite')


class WeddingForm(FlaskForm):
    bride = StringField('Bride\'s Name', validators=[DataRequired()])
    groom = StringField('Groom\'s Name', validators=[DataRequired()])
    date1 = DateField('Date',format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    host_name = StringField('Host Name', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    submit = SubmitField('Send Invite')

class OtherForm(FlaskForm):
    event_name = StringField('Name of Event', validators=[DataRequired()])
    date1 = DateField('Date',format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    host_name = StringField('Host Name', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    submit = SubmitField('Send Invite')

class UpdateAccount(FlaskForm):
    name = StringField('Username', validators=[DataRequired(),Length(min=4, max=15)])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
