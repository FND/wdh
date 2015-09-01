from .fixtures import MockClient, RESPONSES


def test_property_parsing():
    uri = "http://example.org/blog/articles/1"
    client = MockClient({
        uri: RESPONSES[uri]
    })
    client.enter(uri)

    assert len(client.resources) == 1
    article = list(client.resources)[0]
    assert not article.fetched

    assert article.props == {}
    assert not article.fetched

    assert article.props["title"] == ["Hello World"]
    assert article.fetched
