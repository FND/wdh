from wdh import Client


TEMPLATE = """<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="self" href="{uri}">
</head>

<body>
    {body}
</body>

</html>
"""


def _generate_html(body, uri="http://example.org", title="Lipsum"):
    return TEMPLATE.format(title=title, uri=uri, body=body)


RESPONSES = {
    "http://example.org": _generate_html("""
        <a href="/foo" rel="http://rels.example.org/service">Foo</a>
        <a href="/lipsum">lorem ipsum</a>
        <a href="/bar" rel="http://rels.example.org/service">Bar</a>
        <a href="/blog" rel="http://rels.example.org/blog">...</a>
        <a href="/baz" rel="http://rels.example.org/service">Baz</a>
        """),
    "http://example.org/blog": _generate_html("""
        <a href="/blog/articles" rel="http://rels.example.org/articles"></a>
        """),
    "http://example.org/blog/articles": _generate_html("""
        <ul>
            <li>
                <a href="/blog/articles/1" rel="http://rels.example.org/article">#1</a>
            </li>
            <li>
                <details>
                    <summary>
                        <a href="/blog/articles/2"
                                rel="http://rels.example.org/article">#2</a>
                    </summary>
                    <article>
                        <dl>
                            <dt>title</dt>
                            <dd>Lipsum</dd>
                        </dl>
                    </article>
                </details>
            </li>
        </ul>
        """),
    "http://example.org/blog/articles/1": _generate_html("""
        <dl>
            <dt>title</dt>
            <dd>Hello World</dd>
            <dt>author</dt>
            <dd>John Doe</dd>
        </dl>
        """),
    "http://example.org/blog/articles/2": _generate_html("""
        <dl>
            <dt>title</dt>
            <dd>Lipsum</dd>
            <dt>author</dt>
            <dd>Jane Doe</dd>
        </dl>
        """)
}


class MockClient(Client):

    def __init__(self, responses, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._responses = responses

    def _retrieve(self, uri):
        return self._responses[uri]
