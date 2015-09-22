from .fixtures import MockClient, RESPONSES


def test_property_parsing():
    client = MockClient(RESPONSES)
    client.enter("http://example.org/blog/articles/1")

    assert len(client.resources) == 1
    article = client.resources[0]
    assert not article.fetched

    assert article.props == {}
    assert not article.fetched

    assert article.props["title"] == ["Hello World"]
    assert article.fetched


def test_embedded_properties():
    client = MockClient(RESPONSES)
    client.enter("http://example.org/blog/articles")
    client.traverse("http://rels.example.org/article")

    assert len(client.resources) == 2
    article = next(article for article in client.resources
        if article.uri == "http://example.org/blog/articles/2")
    assert not article.fetched

    assert article.props["title"] == ["Lipsum"]
    assert not article.fetched

    assert article.props["author"] == ["Jane Doe"]
    assert article.fetched
