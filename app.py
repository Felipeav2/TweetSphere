from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required,
    UserMixin,
    LoginManager
)
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager, csrf
from models import User
from datetime import datetime
from flask_migrate import Migrate
#username Felipe password hello


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'secret-key'  # Set a secret key for security purposes


# Initialize Flask-Login
login_manager.init_app(app)

# Initialize SQLAlchemy
db.init_app(app)

with app.app_context():
    db.create_all()

# Initialize CSRF protection
csrf.init_app(app)

# After initializing your Flask app and SQLAlchemy
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # The name of the view to redirect to when login is required.


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define a model for the blog posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #Foreign key for referencing User
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    author = db.relationship("User", backref="posts")


# Define the form for adding a new post
class PostForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Post')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


def create_tables():
    with app.app_context():
        db.create_all()


# Home page route - lists all posts
@app.route('/', methods=['GET', 'POST'])
def home():
    #define post form so that user can add posts from the main page
    form = PostForm()

    if request.method == 'POST':

        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if form.validate_on_submit():
            new_post = Post(content=form.content.data, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('home'))
    
    #Fetch post from database to display on the main page
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('home.html', posts=posts, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/some-protected-page')
@login_required
def some_protected_page():
    # Your view logic here
    return render_template('protected_page.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))



# View a single post
@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@csrf.exempt
# Route to delete a post
@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))
    

if __name__ == '__main__':
    create_tables()  # Initialize the database
    app.run(debug=True)


