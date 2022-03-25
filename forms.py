"""Forms for FPL Analytics app."""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Email, Length

class RegisterForm(FlaskForm):
    """Form for registering."""
    first_name = StringField("First Name:", validators=[InputRequired()])
    last_name = StringField("Last Name:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired(), Email()])
    user_name = StringField("Username:", validators=[InputRequired()])
    team_name = StringField("Team Name:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired(), Length(min=6), EqualTo("confirm", message="Passwords must match")])
    confirm  = PasswordField("Repeat Password")

class LoginForm(FlaskForm):
    """Form for logging in."""
    user_name = StringField("Username:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])

class UserDataForm(FlaskForm):
    """Form for modifying user data."""
    first_name = StringField("First Name:", validators=[InputRequired()])
    last_name = StringField("Last Name:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired(), Email()])
    user_name = StringField("Username:", validators=[InputRequired()])
    team_name = StringField("Team Name:", validators=[InputRequired()])
    password = PasswordField("Password must be provided to confirm changes:", validators=[InputRequired(), Length(min=6)])

class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""
    old_password = PasswordField("Old Password:", password = PasswordField("Password:", validators=[InputRequired(), Length(min=6), EqualTo("confirm", message="Passwords must match")]))
    password = PasswordField("Password:", validators=[InputRequired(), Length(min=6), EqualTo("confirm", message="Passwords must match")])
    confirm  = PasswordField("Repeat Password")

class UserEditDataForm(FlaskForm):
    """Form for editing user data."""
    first_name = StringField("First Name:", validators=[InputRequired()])
    last_name = StringField("Last Name:", validators=[InputRequired()])
    email = StringField("Email:", validators=[InputRequired(), Email()])
    user_name = StringField("Username:", validators=[InputRequired()])
    team_name = StringField("Team Name:", validators=[InputRequired()])
    password = PasswordField("Password must be provided to confirm changes:", validators=[InputRequired(), Length(min=6)])

class UserEditPasswordForm(FlaskForm):
    """Form for editing user password."""
    old_password = PasswordField("Old Password:", validators=[InputRequired(), Length(min=6)])
    new_password = PasswordField("New Password:", validators=[InputRequired(), Length(min=6), EqualTo("confirm", message="Passwords must match")])
    confirm  = PasswordField("Repeat Password")
