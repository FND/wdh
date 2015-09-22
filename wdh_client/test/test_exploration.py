"""
a typical explorative usage scenario
"""

from .fixtures import MockClient, RESPONSES


def test_exploration():
    client = MockClient(RESPONSES)
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

    client.traverse("http://rels.example.org/articles")
    # XXX: detailed form tests don't belong here

    actions = client.resources[0].actions
    assert sorted(actions.keys()) == ["http://rels.example.org/article",
            "http://rels.example.org/articles"]
    collection_ops = actions["http://rels.example.org/articles"]
    entity_ops = actions["http://rels.example.org/article"]
    assert list(collection_ops.keys()) == ["GET"]
    assert list(entity_ops.keys()) == ["POST"]
    assert len(collection_ops["GET"]) == 1
    assert len(entity_ops["POST"]) == 1

    filtering = collection_ops["GET"][0]
    assert filtering.caption == "filter articles"
    assert list(filtering.fields.keys()) == ["query"]
    assert len(filtering.fields["query"]) == 1
    field = filtering.fields["query"][0]
    assert field.name == "query"
    assert field.value is None
    assert field.required
    assert field.caption == "search term"

    creating = entity_ops["POST"][0]
    assert creating.caption == "create article"
    assert len(creating.fields) == 2
    field = creating.fields["title"][0]
    assert field.name == "title"
    assert field.value is None
    assert field.required
    assert field.caption == "title:"
    field = creating.fields["content"][0]
    assert field.name == "content"
    assert field.value == "lorem ipsum dolor sit amet"
    assert not field.required
    assert field.caption == "content:"


def test_chaining():
    client = (MockClient(RESPONSES).enter("http://example.org").
            traverse("http://rels.example.org/blog").
            traverse("http://rels.example.org/articles"))

    refs = client.resources[0].refs
    articles = refs["http://rels.example.org/article"]
    assert articles[0].uri == "http://example.org/blog/articles/1"
    assert articles[0].caption == "#1"
    assert articles[1].uri == "http://example.org/blog/articles/2"
    assert articles[1].caption == "#2"
