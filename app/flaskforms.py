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
    photo = FileField('Photo', validators=[InputRequired(), FileRequired(), FileAllowed(['jpg','jpeg','png'], 'JPG,JPEG,PNG images only!')])

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

class UpdatePostForm(FlaskForm):
    post_id = HiddenField()
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class UsernameForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Curent Password', validators=[InputRequired(), Length(min=8,max=80)])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=8,max=80)])

class SetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=8,max=80)])

class AddToCartForm(FlaskForm):
    product_id = HiddenField()
    add_to_cart = SubmitField('Add to Cart')

class RemoveFromCartForm(FlaskForm):
    product_id = HiddenField()
    remove_from_cart = SubmitField('Remove from Cart')

class UpdateCartForm(FlaskForm):
    product_id = HiddenField()
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=10)])
    remove_from_cart = SubmitField('Update')

class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    photo = FileField('Photo', validators=[InputRequired(), FileRequired(), FileAllowed(['jpg','jpeg','png'], 'JPG,JPEG,PNG images only!')])