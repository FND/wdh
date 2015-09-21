import os

from wdh import Client


RESPONSES = {
    "http://example.org": "example.org/index.html",
    "http://example.org/blog": "example.org/blog.html",
    "http://example.org/blog/articles": "example.org/articles.html",
    "http://example.org/blog/articles/1": "example.org/article1.html",
    "http://example.org/blog/articles/2": "example.org/article2.html"
}


class MockClient(Client):

    def __init__(self, responses, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._responses = responses

    def _retrieve(self, uri):
        filepath = self._responses[uri]
        filepath = os.path.join("test", "fixtures", *filepath.split("/"))
        with open(filepath) as fh:
            return fh.read()
