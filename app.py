#!/usr/bin/env python

import yaml

from datetime import date
import math

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
    articles = (Article.from_dict(aid, article)
            for aid, article in enumerate(_retrieve("articles")))
    return render_template("articles.html", title="articles", articles=articles)


@app.route("/articles/<int:article_id>")
def article(article_id):
    article = _retrieve("articles")[article_id]
    article = Article.from_dict(article_id, article)
    return render_template("article.html", title="article", article=article)


@app.route("/authors")
def authors():
    authors = (Author.from_dict(handle, details) for handle, details
            in _retrieve("authors").items())
    return render_template("authors.html", title="authors", authors=authors)


@app.route("/authors/<handle>")
def author(handle):
    author = _retrieve("authors")[handle]
    author = Author.from_dict(handle, author)
    return render_template("author.html", title="author", author=author)


class Article:

    def __init__(self, id, title, authors, content, tags=None, pubdate=None, edits=None):
        self.id = id
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
    def from_dict(id, article): # XXX: slightly awkward and store-specific
        return Article(id, article["title"], article["authors"],
                article["content"], article.get("tags"),
                article.get("pubdate"), article.get("edits"))


class Author:

    def __init__(self, handle, name=None, website=None):
        self.handle = handle # TODO: validate (alphanumerics only)
        self.name = name
        self.website = website

    @property
    def display_name(self):
        if self.name:
            return "%s (%s)" % (self.name, self.handle)
        else:
            return self.handle

    @staticmethod
    def from_dict(handle, details): # XXX: slightly awkward and store-specific
        return Author(handle, details.get("name"), details.get("website"))


def _retrieve(category):
    with open(STORE) as fh:
        store = yaml.load(fh)
    return store[category]


@app.template_filter('to_friendly_date')
def to_friendly_date(src_date):
    now = date.today()
    diff = now - src_date
    months = math.floor(diff.days / 30)
    years = math.floor(months / 12)

    suffix = "in future"
    if diff.days > 0:
        suffix = "ago"

    if diff.days == 0:
        text = "Today"
    elif abs(diff.days) < 30:
        text = "{:.0f} days {}".format(abs(diff.days), suffix)
    elif abs(months) < 12:
        text = "{:.0f} months {}".format(abs(months), suffix)
    else:
        text = "{:.0f} years {}".format(abs(years), suffix)
    return text


if __name__ == "__main__":
    app.run(debug=True) # TODO: read debug setting from config
