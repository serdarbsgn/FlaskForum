from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField,HiddenField, SubmitField,IntegerField,TextAreaField, FloatField, FileField
from wtforms.validators import InputRequired, Email, Length,DataRequired, NumberRange
from flask_wtf.file import FileRequired, FileAllowed

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8,max=80)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class AddProfilePicture(FlaskForm):
    photo = FileField('Photo', validators=[InputRequired(), FileRequired(), FileAllowed(['jpg'], 'JPEG images only!')])

class CreateForumForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')

class CreatePostForm(FlaskForm):
    forum_id = HiddenField()
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CreateCommentForm(FlaskForm):
    post_id = HiddenField()
    comment_id = HiddenField()
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')