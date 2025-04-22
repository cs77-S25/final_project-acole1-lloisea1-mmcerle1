from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_cors import CORS
from models import db, ForumPost, Comment, User
from datetime import timedelta, datetime
from flask_migrate import Migrate

app = Flask(__name__)

# Configure database
app.config['CACHE_TYPE'] = 'null' # disable if in production environment
app.config['SECRET_KEY'] = 'secret key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

# Remove me in production
def check_password(a,b):
    # if check_password_hash(user.password, password):
    if a == b:
        return True
    else: 
        return False

# Remove me in production
def generate_password(a):
    # return generate_password_hash(password, method='sha256')
    return a

# Initialize db to be used with current Flask app
with app.app_context():
    db.init_app(app)

    # Create the database if it doesn't exist
    # Note: create_all does NOT update tables if they are already in the database. 
    # If you change a model’s columns, use a migration library like Alembic with Flask-Alembic 
    # or Flask-Migrate to generate migrations that update the database schema.
    db.create_all()

    # database migrations are used to keep the database up to date 
    # when new models are added or existing ones are changed
    migrate = Migrate(app, db)


# ROUTES

@app.route('/')
def home():
    return render_template('home.html', session=session)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' not in session:
        if request.method == 'POST':  # If the form is submitted
            username = request.form['username']  # Get the username from the form
            password = request.form['password']  # Get the password from the form
            user = User.query.filter_by(username=username).first()  # Query the user by username
            
            if user and check_password(user.password, password):  # Check if user exists and password is correct
                session['user_id'] = user.id  # Set the user ID in the session
                session['username'] = user.username
                session.permanent = True
                return redirect(url_for('home'))  # Redirect to homepage
            else:
                error = "your username or password do not match."
                return render_template('error.html', error=error) # Display error page
        
        else:
            return render_template('login.html')  # Render the login template
    else:
        return redirect(url_for('home'))  # Redirect to the login page


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)  # Remove the user ID from the session
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' not in session:
        if request.method == 'POST':  # If the form is submitted
            username = request.form['username']  # Get the username from the form
            password = request.form['password']  # Get the password from the form
            email = request.form['email']
            new_password = generate_password(password) 
            new_user = User(username=username, password=new_password, email = email)  # Create a new user object
            db.session.add(new_user)  # Add the new user to the session
            db.session.commit()  # Commit the session to the database
            return redirect(url_for('login'))  # Redirect to the login page
        else:
            return render_template('register.html')  # Render the register template
    else:
        return redirect(url_for('home'))  # Redirect to the login page

@app.route('/forum/')
def forum():
    # TODO make this load with tags!!!!! please please please
    now = datetime.now()
    posts = ForumPost.query.filter((now-ForumPost.created_at) < timedelta(days=7)).order_by(ForumPost.likes.desc()).all()
    return render_template('forum.html', posts=posts)


@app.route('/forum_item/<int:post_id>', methods=['GET', 'POST'])
def forum_item(post_id):
    post = ForumPost.query.get_or_404(post_id) # returns a 404 error if get fails
    if request.method == 'GET':
        comments = Comment.query.filter_by(forumpost_id=post_id).order_by(Comment.likes.desc()).all()
        # comments = post.comments
        return render_template('forum_item.html', post=post, comments=comments) # return the thread object

    elif request.method == 'POST' and 'user_id' in session:
        print("IN ELIF!!!!!!!!!!!!!!!!!!!!!", flush=True)

        form = request.get_json()
        content = form["content"]
        author = session['user_id']
        # author = User.query.filter_by(username=session['username']).first()

        if content:
            new_comment = Comment(author=author, content=content, forumpost_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            print(f"Added new comment: {new_comment.serialize()}", flush=True)
            return make_response(jsonify({"success": "true", "comment": new_comment.serialize()}), 200)
    
    else:
        return redirect(url_for('login'))


@app.route('/forum/compose/', methods=['GET', 'POST'])
def make_forum_post():
    if (request.method == 'POST') and ('user_id' in session):

        title = request.form.get('title')
        text = request.form.get('content')
        author = session['user_id']

        if title and text:
            new_post = ForumPost(title=title, content=text, author=author)
            db.session.add(new_post)
            db.session.commit()

        return redirect(url_for('forum')) # set variable 

    elif ('user_id' not in session):
        return redirect(url_for('login'))

    else:
        return render_template('forum_post.html')


@app.route('/blog/')
def blog():
    return render_template('blog.html')


@app.route('/blog_post/')
def blog_post():
    return render_template('blog_post.html')


@app.route('/blog_post_1/')
def blog_post_1():
    return render_template('blog_post_1.html')


@app.route('/resources/')
def resources():
    return render_template('resources.html')


@app.route('/search/')
def search():
    return render_template('search.html')

    

# @app.route('/new_thread', methods=['POST'])
# def new_thread():
#     form = request.get_json()
#     title = form["title"]
#     content = form["content"]
#     if title and content:
#         new_thread = Thread(title=title, content=content)
#         db.session.add(new_thread)
#         db.session.commit()
#         print(f"Added new thread: {new_thread.serialize()}")
#         return make_response(jsonify({"success": "true", "thread": new_thread.serialize()}), 200) # return both JSON object and HTTP response status (200: OK)

#     return make_response(jsonify({"success": "false"}), 400) # return both JSON object and HTTP response status (400: bad request)

# @app.route('/comment/<int:thread_id>', methods=['POST'])
# def comment(thread_id):
#     thread = Thread.query.get_or_404(thread_id) # returns a 404 error if get fails
#     comment_text = request.form.get('comment')
#     if comment_text:
#         new_comment = Comment(thread_id=thread.id, content=comment_text)
#         db.session.add(new_comment)
#         db.session.commit()

#     return redirect(url_for('thread', thread_id=thread_id)) # set variable thread_id to be thread_id

if __name__ == '__main__':
    app.run(debug=True)
