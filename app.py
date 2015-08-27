#!/usr/bin/env python

import yaml

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
    articles = ((i, article) for i, article in enumerate(_retrieve("articles")))
    return render_template("articles.html", title="articles", articles=articles)


@app.route("/articles/<article_id>")
def article(article_id):
    article = _retrieve("articles")[int(article_id)]
    return render_template("article.html", title="article", article=article)


@app.route("/authors")
def authors():
    abort(501)


def _retrieve(category):
    with open(STORE) as fh:
        store = yaml.load(fh)
    return store[category]


if __name__ == "__main__":
    app.run(debug=True) # TODO: read debug setting from config
