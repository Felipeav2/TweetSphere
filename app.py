from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

# Define a model for the blog posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

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
    if request.method == 'POST':
        new_post = Post(title=request.form['title'], content=request.form['content'])
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_post.html')

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
