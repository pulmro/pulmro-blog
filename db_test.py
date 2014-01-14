#!bin/python
# -*- coding: utf-8 -*-
import os
import unittest
from datetime import datetime

from config import basedir
from blog import app, db
from blog.models import Article, Comment, Category


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add(self, obj):
        db.session.add(obj)
        db.session.commit()

    def print_sub_comments(self, comment, n):
        for cmt in comment.childs:
            print "- "+cmt.content+" ("+str(n)+")"
            self.print_sub_comments(cmt, n+1)

    def populate_subcomments(self, comment):
        comment.childs = []
        for cmt in comment.children.order_by('date desc').all():
            comment.childs.append(cmt)
            self.populate_subcomments(cmt)

    def test_comments(self):
        a = Article('Articolo 1', 'Questo è il primo articolo')
        b = Article('Articolo 2', 'Questo è il secondo articolo')
        self.add(a)
        self.add(b)
        c1 = Comment(article_id=a.id, date=datetime.utcnow(), content='Primo commento', parent_id=0)
        self.add(c1)
        c2 = Comment(article_id=a.id, date=datetime.utcnow(), content='Secondo commento',
                     parent_id=c1.id)
        self.add(c2)
        c3 = Comment(article_id=a.id, date=datetime.utcnow(), content='Terzo commento', parent_id=0)
        self.add(c3)
        c4 = Comment(article_id=b.id, date=datetime.utcnow(), content='Altro commento',
                     parent_id=c2.id)
        self.add(c4)
        article = Article.query.get(1)
        comments = []
        for comment in article.comments.filter(Comment.parent_id == 0).order_by('date desc').all():
            self.populate_subcomments(comment)
            comments.append(comment)
        for comment in comments:
            print comment.content
            self.print_sub_comments(comment, 1)
        cat1 = Category(name='1st Category')
        cat2 = Category(name='2nd Category')
        self.add(cat1)
        self.add(cat2)
        article.categories = [cat1]
        #Article.query.filter_by(id=1).update({'categories': [cat1]})
        db.session.commit()
        print Article.query.get(1).categories


if __name__ == '__main__':
    unittest.main()