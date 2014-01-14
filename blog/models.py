from datetime import datetime
from flask import url_for
from blog import db, bcrypt


ROLE_USER = 0
ROLE_ADMIN = 1


categories = db.Table('categories',
                      db.Column('cat_id', db.Integer, db.ForeignKey('category.id')),
                      db.Column('article_id', db.Integer, db.ForeignKey('article.id')))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime)
    title = db.Column(db.String(255))
    thumbnail_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'))
    thumbnail = db.relationship('UploadedFiles', uselist=False)
    description = db.Column(db.String(350))
    body = db.Column(db.Text)
    categories = db.relationship('Category', secondary='categories', backref=db.backref('articles', lazy='dynamic'))
    comments = db.relationship('Comment', backref=db.backref('article'), lazy='dynamic')

    def __init__(self, title, body, description=None, thumbnail_id=None, categories=[]):
        self.title = unicode(title)
        self.body = unicode(body, "utf-8")
        self.description = unicode(description)
        self.thumbnail_id = thumbnail_id
        self.created_at = datetime.utcnow()
        self.categories = categories

    def __repr__(self):
        return '<Article %r>' % self.title

    def get_absolute_url(self):
        return url_for('get_article', article_id=self.id)

    def get_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.get_url()
        return None

    def get_next(self):
        return Article.query.filter(Article.created_at > self.created_at).order_by('created_at').first()

    def get_previous(self):
        return Article.query.filter(Article.created_at < self.created_at).order_by('created_at desc').first()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name

    @staticmethod
    def get_all():
        return Category.query.order_by('name').all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def is_admin(self):
        return self.role == ROLE_ADMIN

    @staticmethod
    def hash_password(password):
        return bcrypt.generate_password_hash(password)

    def password_correct(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.nickname


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author_IP = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    content = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    children = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                               lazy='dynamic')


class UploadedFiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(125))
    uploaded_at = db.Column(db.DateTime)

    def get_url(self):
        return url_for('uploaded_file', filename=self.name)