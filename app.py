#!/usr/bin/env python

import yaml

from datetime import date

from flask import Flask, render_template, abort, url_for


app = Flask(__name__)

RELS = "http://rels.example.org"
STORE = "store.yml" # TODO: read from config


@app.route("/")
def index():
    resources = {}
    resources["%s/articles" % RELS] = ("articles",
            url_for("articles", _external=True))
    resources["%s/authors" % RELS] = ("authors",
            url_for("authors", _external=True))
    return render_template("index.html", title="index", resources=resources)


@app.route("/articles")
def articles():
    with open(STORE) as fh:
        store = yaml.load(fh)
    # add article IDs
    articles = ((i, Article.from_dict(article))
            for i, article in enumerate(_retrieve("articles")))
    return render_template("articles.html", title="articles", articles=articles)


@app.route("/articles/<article_id>")
def article(article_id):
    article = _retrieve("articles")[int(article_id)]
    article = Article.from_dict(article)
    return render_template("article.html", title="article", article=article)


@app.route("/authors")
def authors():
    abort(501)


class Article:

    def __init__(self, title, authors, content, tags=None, pubdate=None, edits=None):
        self.title = title
        self.authors = authors
        self.tags = tags or []
        self.pubdate = pubdate
        self.edits = edits or 0
        self.content = content

    @property
    def published(self):
        return date.today() > self.pubdate if self.pubdate else False

    @staticmethod
    def from_dict(article, article_id=None):
        article = Article(article["title"], article["authors"],
                article["content"], article.get("tags"),
                article.get("pubdate"), article.get("edits"))
        if article_id:
            article.id = article_id
        return article


def _retrieve(category):
    with open(STORE) as fh:
        store = yaml.load(fh)
    return store[category]


if __name__ == "__main__":
    app.run(debug=True) # TODO: read debug setting from config
