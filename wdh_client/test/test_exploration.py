"""
a typical explorative usage scenario
"""

from .fixtures import MockClient, loader


def test_exploration():
    client = MockClient({
        "http://example.org": loader("example.org/index.html"),
        "http://example.org/blog": loader("example.org/blog.html")
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
