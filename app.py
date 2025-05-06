from flask import Flask, flash, render_template, request, redirect, url_for, make_response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash
from flask_cors import CORS
from models import db, ForumPost, Comment, User
from datetime import timedelta, datetime
from flask_migrate import Migrate

import content_moderation_openai as mod
import time

app = Flask(__name__)

# Configure database
app.config['CACHE_TYPE'] = 'null' # disable if in production environment
app.config['SECRET_KEY'] = 'secret key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS
CORS(app)

def check_password(a,b):
    if check_password_hash(a,b):
        return True
    else: 
        return False


def generate_password(a):
    return generate_password_hash(a, method='scrypt')


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
                error = True
                error_message = "Your username or password do not match."
                return render_template('login.html', error=error, error_message= error_message) # Display error page
        
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
    if  request.args:
        
        topic = request.args.get("t")
        keyword = request.args.get("k")
        
        if keyword == "" and topic != "all":
            posts = ForumPost.query.filter_by(topic=topic).order_by(ForumPost.likes.desc()).all()
        elif keyword != "" and topic == "all":
            posts = ForumPost.query.filter(or_((ForumPost.title.contains(keyword)), (ForumPost.content.contains(keyword)))).order_by(ForumPost.likes.desc()).all()
        elif keyword != "" and topic != "all":
            posts = ForumPost.query.filter_by(topic=topic).filter(or_((ForumPost.title.contains(keyword)), (ForumPost.content.contains(keyword)))).order_by(ForumPost.likes.desc()).all()
        else:
            now = datetime.now()
            posts = ForumPost.query.filter((now-ForumPost.created_at) < timedelta(days=7)).order_by(ForumPost.likes.desc()).all()
    else:
        now = datetime.now()
        posts = ForumPost.query.filter((now-ForumPost.created_at) < timedelta(days=7)).order_by(ForumPost.likes.desc()).all()

    return render_template('forum.html', posts=posts)




@app.route('/forum_item/<int:post_id>', methods=['GET', 'POST'])
def forum_item(post_id):
    post = ForumPost.query.get_or_404(post_id) # returns a 404 error if get fails
    if request.method == 'GET':
        comments = Comment.query.filter_by(forumpost_id=post_id).order_by(Comment.created_at.desc()).all()
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
        flag = mod.moderate_text(text)
        print(flag)
        author = session['user_id']
        topic = None

        if(flag == False):
            if request.form.get('topic'):
                topic = request.form.get('topic')

            if title and text:
                if topic:
                    new_post = ForumPost(title=title, content=text, author=author, topic=topic)
                else:
                    new_post = ForumPost(title=title, content=text, author=author)
                db.session.add(new_post)
                db.session.commit()
        else:
            error_message = "Content blocked: Violates usage policies"
            return render_template('forum_post.html', error = True, error_message = error_message)

        return redirect(url_for('forum')) # set variable 

    elif ('user_id' not in session):
        return redirect(url_for('login'))

    else:
        return render_template('forum_post.html', error = False)


@app.route('/blog/')
def blog():
    return render_template('blog.html')


@app.route('/blog_post/')
def blog_post():
    return render_template('blog_post.html')


@app.route('/blog_post_1/')
def blog_post_1():
    return render_template('blog_post_1.html')

@app.route('/blog_post_2/')
def blog_post_2():
    return render_template('blog_post_2.html')

@app.route('/blog_post_3/')
def blog_post_3():
    return render_template('blog_post_3.html')

@app.route('/resources/')
def resources():
    return render_template('resources.html')


@app.route('/forum_item/like', methods=['PUT'])
def upvote():
    print("in Like post!")
    post_id = request.get_json()
    post = db.session.query(ForumPost).filter_by(id = post_id).one_or_none()
    post.likes += 1
    db.session.commit()
    print(post.likes)
    return make_response(jsonify({"success": "true", "post":post.serialize()}), 400)



if __name__ == '__main__':
    app.run(debug=True)
