from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import Users, BannedUsers


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(BannedUsers).where(
            BannedUsers.username == username.data))
        if user is not None:
            raise ValidationError('YOU HAVE BEEN BANNED!')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(Users).where(
            Users.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(BannedUsers).where(
            BannedUsers.email == email.data))
        if user is not None:
            raise ValidationError('YOU HAVE BEEN BANNED!')

        user = db.session.scalar(sa.select(Users).where(
            Users.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')



class BanUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Ban')

    def validate_username(self, username):
        unknown_user_test = db.session.scalar(sa.select(Users).where(
            Users.username == username.data))
        if unknown_user_test is None:
            raise ValidationError('Please use a different username.')
        banned_user_test = db.session.scalar(sa.select(BannedUsers).where(
            BannedUsers.username == username.data))
        if banned_user_test is not None:
            raise ValidationError('This user is already banned!')

class UnbanUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('unban')

    def validate_username(self, username):
        unknown_user_test = db.session.scalar(sa.select(BannedUsers).where(
            Users.username == username.data))
        if unknown_user_test is None:
            raise ValidationError('Please use a different username.')
        not_banned_user_test = db.session.scalar(sa.select(BannedUsers).where(
            BannedUsers.username == username.data))
        if not_banned_user_test is None:
            raise ValidationError('This user is not banned!')
