"""
a typical explorative usage scenario
"""

from .fixtures import MockClient


def test_exploration():
    client = MockClient({
        "http://example.org": "example.org/index.html",
        "http://example.org/blog": "example.org/blog.html"
    })
    client.enter("http://example.org")

    assert len(client.resources) == 1
    resource = client.resources[0]
    assert not resource.fetched

    refs = resource.refs
    assert resource.fetched

    assert "http://rels.example.org/blog" in refs
    search = refs["search"][0]
    assert search.uri == "http://example.org/search"
    assert search.caption == "global search"

    client.traverse("http://rels.example.org/blog")

    assert len(client.resources) == 1
    resource = client.resources[0]
    assert not resource.fetched

    refs = resource.refs
    assert resource.fetched
    assert "http://rels.example.org/articles" in refs
    search = refs["search"][0]
    assert search.uri == "http://example.org/blog/search"
    assert search.caption == "article search"


def test_chaining():
    client = (MockClient({
        "http://example.org": "example.org/index.html",
        "http://example.org/blog": "example.org/blog.html",
        "http://example.org/blog/articles": "example.org/articles.html"
    }).enter("http://example.org").
            traverse("http://rels.example.org/blog").
            traverse("http://rels.example.org/articles"))

    refs = client.resources[0].refs
    articles = refs["http://rels.example.org/article"]
    assert articles[0].uri == "http://example.org/blog/articles/1"
    assert articles[0].caption == "#1"
    assert articles[1].uri == "http://example.org/blog/articles/2"
    assert articles[1].caption == "#2"
