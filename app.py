from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'secret-key'  # Set a secret key for security purposes
db = SQLAlchemy(app)
csrf = CSRFProtect(app)  # Enable CSRF protection

# Define a model for the blog posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Define the form for adding a new post
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Add Post')

def create_tables():
    with app.app_context():
        db.create_all()

# Home page route - lists all posts
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

# View a single post
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Add a new post
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_post.html', form=form)

@csrf.exempt
# Route to delete a post
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home'))
    

if __name__ == '__main__':
    create_tables()  # Initialize the database
    app.run(debug=True)


