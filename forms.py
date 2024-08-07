from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.fields.simple import FileField
from wtforms.validators import DataRequired, Length, Email, Optional

class ReviewFormCreate(FlaskForm):
    profile_id = IntegerField('Profile ID', validators=[DataRequired()])
    film_id = IntegerField('Film ID', validators=[DataRequired()])
    title = StringField('Short Text', validators=[DataRequired(), Length(max=100)])
    review_text = StringField('Long Text', validators=[DataRequired(), Length(max=1000)])
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class SerialReviewFormCreate(FlaskForm):
    profile_id = IntegerField('Profile ID', validators=[DataRequired()])
    serial_id = IntegerField('Serial ID', validators=[DataRequired()])
    title = StringField('Short Text', validators=[DataRequired(), Length(max=100)])
    review_text = StringField('Long Text', validators=[DataRequired(), Length(max=1000)])
    rating = FloatField('Rating', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=40)])
    password = StringField('Password', validators=[DataRequired()], render_kw={'type': 'password'})
    submit = SubmitField('Log In')

class ProfileForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    name = StringField('Username', validators=[DataRequired(), Length(min=4, max=40)])
    avatar = FileField('Avatar', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = StringField('Bio', validators=[Optional(), Length(max=400)])
    submit = SubmitField('Update Profile')
