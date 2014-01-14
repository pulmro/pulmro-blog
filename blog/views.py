from flask import render_template, g, url_for, redirect, request, flash, Markup, send_from_directory
from werkzeug import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from blog import app, db, loginmanager, forms
from models import User, Comment, Article, Category, UploadedFiles
from decorators import admin_login_required
from forms import LoginForm
from markdown import markdown
import time
import os
from datetime import datetime


@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.username.data).first()
        if user and user.password_correct(form.password.data):
            login_user(user)
            flash("Logged in successfully")
            time.sleep(2)
            return redirect(url_for('admin'))
        else:
            flash("Wrong username or password!")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)
    g.user = current_user


@app.route('/')
@app.route('/index')
def index():
    recent_articles = Article.query.order_by('created_at desc').limit(3).all()
    return render_template('index.html', categories=Category.get_all(), recent_articles=recent_articles)


@app.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.get(article_id)
    previous_article = article.get_previous()
    article.body_html = Markup(markdown(article.body))
    next_article = article.get_next()
    link_next = {'title': None, 'url': url_for('index')} if next_article is None\
        else {'title': next_article.title, 'url': next_article.get_absolute_url()}
    link_previous = {'title': None, 'url': url_for('index')} if previous_article is None\
        else {'title': previous_article.title, 'url': previous_article.get_absolute_url()}
    comments = [comment for comment in article.comments.filter(Comment.parent_id == 0).order_by('date').all()]
    form = forms.CommentRespondForm()
    return render_template('article.html', categories=Category.get_all(), article=article, link_previous=link_previous,
                           link_next=link_next, form=form, comments=comments)


@app.route('/comment-post', methods=['POST'])
def comment_post():
    form = forms.CommentRespondForm(request.form)
    print form.data
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(nickname=data['author'], email=data['email']).first()
        if not user:
            user = User(nickname=data['author'], email=data['email'])
            db.session.add(user)
            db.session.commit()
        comment = Comment(article_id=data['comment_post_id'], author_id=user.id, content=data['body'],
                          date=datetime.utcnow(), parent_id=data['comment_parent_id'])
        db.session.add(comment)
        db.session.commit()
        flash('Success!')
    else:
        print form.errors
    return redirect(url_for('get_article', article_id=form.comment_post_id.data))


@app.route('/edit_article/<int:article_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_article(article_id):
    form = forms.EditArticleForm(request.form)
    media_form = get_media_form()
    #print form.data
    # Populate form with all available categories
    form.categories.choices = [(cat.id, cat.name) for cat in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        data = form.data
        Article.query.filter_by(id=article_id).update({"title": data['title'], "body": data['pagedown'],
                                                       "description": data['description'],
                                                       "thumbnail_id": data['image']})
        Article.query.get(article_id).categories = [Category.query.get(i) for i in data['categories']]
        db.session.commit()
        return redirect(url_for('get_article', article_id=article_id))
    else:
        print form.errors
    article = Article.query.get(article_id)
    form.title.data = article.title
    form.pagedown.data = article.body
    form.description.data = article.description
    form.categories.data = [cat.id for cat in article.categories]
    form.image.set_data(article.thumbnail_id, article.thumbnail.get_url())
    return render_template('edit_article.html', categories=Category.get_all(), form=form, media_form=media_form)


@app.route('/admin/new_article', methods=['GET', 'POST'])
@admin_login_required
def new_article():
    form = forms.EditArticleForm()
    media_form = get_media_form()
    form.categories.choices = [(cat.id, cat.name) for cat in Category.query.order_by('name').all()]
    if form.validate_on_submit():
        data = form.data
        categories = [Category.query.get(i) for i in data['categories']]
        article = Article(data['title'], data['pagedown'], data['description'], None, categories)
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('get_article', article_id=article.id))
    return render_template('edit_article.html', categories=Category.get_all(), form=form, media_form=media_form)


@app.route('/admin/edit_category/<int:category_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_category(category_id):
    form = forms.EditCategoryForm()
    if form.validate_on_submit():
        data = form.data
        Category.query.filter_by(id=category_id).update({"name": data['name']})
        db.session.commit()
        return redirect(url_for('admin'))
    category = Category.query.get(category_id)
    form.name.data = category.name
    return render_template('edit_category.html', form=form)


@app.route('/admin/new_category', methods=['GET', 'POST'])
@admin_login_required
def new_category():
    form = forms.EditCategoryForm()
    if form.validate_on_submit():
        data = form.data
        category = Category(name=data['name'])
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_category.html', form=form)


@app.route('/admin')
@admin_login_required
def admin():
    recent_articles = Article.query.order_by('created_at desc').limit(5).all()
    recent_users = User.query.order_by('nickname').limit(5).all()
    recent_comments = Comment.query.order_by('date desc').limit(5).all()
    recent_categories = Category.query.order_by('name').limit(5).all()
    return render_template('admin.html', recent_articles=recent_articles, recent_users=recent_users,
                           recent_comments=recent_comments, recent_categories=recent_categories)


@app.route('/admin/articles')
@admin_login_required
def admin_articles():
    articles = Article.query.order_by('created_at desc').all()
    return render_template('admin_articles.html', articles=articles)


@app.route('/admin/files', methods=['GET', 'POST'])
@admin_login_required
def admin_files():
    form = forms.UploadFileForm()
    if form.validate_on_submit():
        upload_file = form.file.data
        filename = secure_filename(upload_file.filename)
        upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_file = UploadedFiles(filename)
        db.session.add(new_file)
        db.session.commit()
    else:
        filename = None
    files = UploadedFiles.query.order_by('uploaded_at desc').all()
    return render_template('admin_files.html', files=files, form=form, filename=filename)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    print app.config['UPLOAD_FOLDER']
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def get_media_form():
    media_form = forms.MediaForm()
    media_form.files.choices = [(file.id, file.get_url()) for file in UploadedFiles.query.order_by('uploaded_at').all()]
    return media_form