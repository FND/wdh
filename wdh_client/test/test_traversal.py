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
    assert collection.caption is None

    client.traverse("http://rels.example.org/article")
    assert len(client.resources) == 2
    articles = { res.uri: res.caption for res in client.resources }
    assert articles == {
        "http://example.org/blog/articles/1": "#1",
        "http://example.org/blog/articles/2": "#2"
    }
