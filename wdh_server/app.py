#!/usr/bin/env python

import os
import math

import yaml

from datetime import date
from collections import OrderedDict

from flask import Flask, render_template, redirect, url_for, request


app = Flask(__name__)

RELS = "http://rels.example.org"
store_location = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(store_location, "store.yml") # TODO: read from config


@app.route("/")
def index():
    resources = OrderedDict()
    resources["%s/articles" % RELS] = ("articles",
            url_for("articles", _external=True))
    resources["%s/authors" % RELS] = ("authors",
            url_for("authors", _external=True))
    resources["%s/search" % RELS] = ("search",
            url_for("search", _external=True))
    return render_template("index.html", title="index",
            self_uri=url_for("index"), resources=resources)


@app.route("/articles")
def articles():
    articles = (Article.from_dict(aid, article)
            for aid, article in enumerate(_retrieve("articles")))
    return render_template("articles.html", title="articles",
            self_uri=url_for("articles"), articles=articles)


@app.route("/articles/<int:article_id>")
def article(article_id):
    article = _retrieve("articles")[article_id]
    article = Article.from_dict(article_id, article)
    return render_template("article.html", title="article",
            self_uri=url_for("article", article_id=article.id), article=article)


@app.route("/authors")
def authors():
    authors = (Author.from_dict(handle, details) for handle, details
            in _retrieve("authors").items())
    return render_template("authors.html", title="authors",
            self_uri=url_for("authors"), authors=authors)


@app.route("/authors/<handle>")
def author(handle):
    author = _retrieve("authors")[handle]
    author = Author.from_dict(handle, author)
    return render_template("author.html", title="author",
            self_uri=url_for("author", handle=author.handle), author=author)


@app.route('/search')
def search():
    term = request.args.get("term", "").lower()
    category = request.args.get("category")

    categories = [("article", "Article"), ("author", "Author")]

    if not term or not category:
        return render_template("search.html", self_uri=url_for("search"),
                title="search", categories=categories)

    title = "Search result: \"{}\" ({})".format(term, category),

    if category == "article":
        articles = []
        for aid, article in enumerate(_retrieve("articles")):
            article = Article.from_dict(aid, article)
            if term in article.title.lower():
                articles.append(article)

        return render_template("articles.html", title=title,
            self_uri=request.url, articles=articles)

    if category == "author":
        authors = []
        for handle, details in _retrieve("authors").items():
            author = Author.from_dict(handle, details)
            if term in author.display_name.lower():
                authors.append(author)

        return render_template("authors.html", title=title,
            self_uri=request.url, authors=authors)

    return redirect(url_for("search"))


@app.template_filter("friendly_date")
def friendly_date(src_date):
    diff = date.today() - src_date
    months = math.floor(diff.days / 30)
    years = math.floor(months / 12)

    suffix = "ago" if diff.days > 0 else "in future"

    if diff.days == 0:
        text = "Today"
    elif abs(diff.days) < 30:
        text = "{:.0f} days {}".format(abs(diff.days), suffix)
    elif abs(months) < 12:
        text = "{:.0f} months {}".format(abs(months), suffix)
    else:
        text = "{:.0f} years {}".format(abs(years), suffix)
    return text


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


if __name__ == "__main__":
    import sys
    settings = { # TODO: read from config
        "debug": True
    }
    try:
        settings["port"] = int(sys.argv[1])
    except IndexError as exc:
        pass
    app.run(**settings)
