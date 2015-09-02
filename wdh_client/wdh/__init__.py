import httplib2

from collections import defaultdict

from .parser import parse, extract_properties, extract_references, extract_text


class Client:

    def __init__(self, headers=None):
        self.headers = headers

    def enter(self, uri):
        self.resources = [Resource(uri, retriever=self._retrieve)]

    def traverse(self, *rels):
        rel = rels[0]
        references = set()
        for resource in self.resources:
            if not resource.fetched:
                resource.fetch()

            for resource in resource.links.get(rel, []):
                references.add(resource)
        self.resources = references

        if len(rels) > 1:
            self.traverse(*rels[1:])

    def _retrieve(self, uri):
        args = { "method": "get" }
        if self.headers:
            args["headers"] = headers
        res, content = httplib2.Http().request(uri, **args) # XXX: automatically follows redirects

        assert res["status"].startswith("2") # XXX: too simplistic? -- TODO: use custom exception
        return content


class Resource:

    def __init__(self, uri, retriever, caption=None):
        self.uri = uri
        self.caption = caption
        self.fetched = False
        self.retriever = retriever # XXX: awkward dependency

    @property # TODO: `memoize` decorator
    def links(self): # TODO: rename to "refs"?
        try:
            return self._links
        except AttributeError:
            pass

        self._links = defaultdict(set)
        for rel, uri, caption, props in extract_references(self.document, self.uri):
            resource = Resource(uri, retriever=self.retriever, caption=caption)

            if props:
                properties = resource.props
                for key, values in props: # XXX: does not belong here!?
                    properties[key] = values

            self._links[rel].add(resource)
        return self._links

    @property # TODO: `memoize` decorator
    def props(self):
        try:
            return self._props
        except AttributeError:
            self._props = PropertyList(self.missing_property_handler)
            return self._props

    @property # TODO: `memoize` decorator
    def document(self):
        try:
            return self._document
        except AttributeError:
            self._document = parse(self._content, self.uri)
            return self._document

    def fetch(self):
        self._content = self.retriever(self.uri)
        # TODO: reset cached attributes?
        self.fetched = True

    def missing_property_handler(self, key, props): # XXX: `props` unnecessary; identical to `self._props`!?
        if not self.fetched:
            self.fetch()

        for _key, values in extract_properties(self.document): # XXX: belongs into `props`!?
            props[_key] = values

        if key in props: # avoids infinite recursion
            return props[key]
        else:
            raise KeyError(key)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(self.uri) # XXX: fetch status, fetched timestamp?

    def __repr__(self):
        status = "fetched" if self.fetched else "unfetched"
        txt = "%s [%s]" % (self.uri, status)
        if self.caption:
            txt = "%s '%s'" % (txt, self.caption) # XXX: caption might include single quotes
        return "<%s %s>" % (txt, self.props) # XXX: `props` is potentially quite large


class PropertyList(dict):

    def __init__(self, missing_handler):
        self.missing_handler = missing_handler

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.missing_handler(key, self)
