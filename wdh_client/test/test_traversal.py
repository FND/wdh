from .fixtures import MockClient, RESPONSES


def test_traversal():
    client = MockClient({
        "http://example.org": RESPONSES["http://example.org"]
    })
    client.enter("http://example.org")

    assert len(client.resources) == 1
    index = client.resources[0]
    assert not index.fetched

    client.traverse("http://rels.example.org/service")
    assert index.fetched

    assert len(client.resources) == 3
    services = { res.uri: res.caption for res in client.resources }
    assert services == {
        "http://example.org/foo": "Foo",
        "http://example.org/bar": "Bar",
        "http://example.org/baz": "Baz"
    }


def test_multi_traversal():
    client = MockClient(RESPONSES)
    client.enter("http://example.org")
    client.traverse("http://rels.example.org/blog",
            "http://rels.example.org/articles")

    assert len(client.resources) == 1
    collection = client.resources[0]
    assert collection.uri == "http://example.org/blog/articles"
    assert collection.caption == "article index"

    client.traverse("http://rels.example.org/article")
    assert len(client.resources) == 2
    articles = { res.uri: res.caption for res in client.resources }
    assert articles == {
        "http://example.org/blog/articles/1": "#1",
        "http://example.org/blog/articles/2": "#2"
    }


def test_link_handling():
    client = MockClient(RESPONSES)
    client.enter("http://example.org")

    resource = client.resources[0]
    assert resource.uri == "http://example.org"
    assert resource.caption is None
    resource.fetch()
    assert resource.uri == "http://example.org/"
    assert resource.caption == "index"

    client.traverse("http://rels.example.org/blog")

    resource = client.resources[0]
    assert resource.uri == "http://example.org/blog"
    assert resource.caption == "blog"

    resource.fetch()

    assert resource.uri == "http://example.org/blog?page=1"
    assert resource.caption == "blog index"

    about = resource.refs["about"][0]
    assert about.uri == "http://example.org/blog/about"
    assert about.caption == "about"

    about.fetch()

    assert about.uri == "http://example.org/blog/about"
    assert about.caption == "about"

    copyright = resource.refs["copyright"][0]
    assert copyright.uri == "http://example.org/legal"
    assert copyright.caption is None
