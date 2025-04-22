from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ForumPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    comments = db.relationship('Comment', backref='forumpost', cascade="all, delete-orphan", lazy=True)
    likes = db.Column(db.Integer, default=0)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        string = f"ID: {self.id}, Title: {self.title}, Content: {self.content}, Created_At: {self.created_at}, Comments: {self.comments}, Author: {self.author}"
        return string
    
    def serialize(self):
        return {"id": self.id,\
                "title": self.title,\
                "author": self.author.username,\
                "likes": self.likes,\
                "content": self.content}


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forumpost_id = db.Column(db.Integer, db.ForeignKey('forum_post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default = 0)

    def serialize(self):
        return {"id": self.id,\
                "author": self.author.username,\
                "likes": self.likes,\
                "content": self.content}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    comments = db.relationship('Comment', backref='user', cascade="all, delete-orphan", lazy=True)
    forumposts = db.relationship('ForumPost', backref='user', cascade="all, delete-orphan", lazy=True)

    def __repr__(self) -> str:
        return f"ID: {self.id}, Username: {self.username}, Password: {self.password}"


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
