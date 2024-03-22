from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
import re


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=25)])
    submit = SubmitField('Login')


class CreateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=25, message='Password must be at least 8 characters long.'),
        EqualTo('confirm_password', message='Passwords must match.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=25)])
    submit = SubmitField('Create Account')

    def validate_password(self, password):
        complexity_check = re.compile(r'^(?=.*[A-Z].*[A-Z])(?=.*[!@#$&*])(?=.*[0-9].*[0-9])(?=.*[a-z].*[a-z]).{8,}$')
        if not complexity_check.match(password.data):
            raise ValidationError('Password must contain at least 2 uppercase letters, 2 lowercase letters, 2 digits, and 2 special characters.')
