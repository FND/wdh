import httplib2

from collections import namedtuple, defaultdict

from .parser import (extract_actions, extract_properties, extract_references,
        extract_metadata, extract_text, parse)
from .util import memoized_property


class Client:

    def __init__(self, headers=None):
        self.headers = headers

    def enter(self, uri):
        self.resources = [Resource(uri, retriever=self._retrieve)]
        return self

    def traverse(self, *rels):
        rel = rels[0]
        references = set()
        for resource in self.resources:
            if not resource.fetched:
                resource.fetch()

            for resource in resource.refs.get(rel, []):
                references.add(resource)
        self.resources = list(references)

        if len(rels) > 1:
            self.traverse(*rels[1:])

        return self

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

    @memoized_property
    def actions(self):
        actions = defaultdict(lambda: defaultdict(list)) # `{ rel: method: [actions] } }`
        for rel, uri, method, caption, fields in extract_actions(self.document):
            actions[rel][method].append(Action(uri, caption, fields))
        return dict(actions)

    @memoized_property
    def refs(self):
        refs = defaultdict(list)
        for rel, uri, caption, props in extract_references(self.document):
            resource = Resource(uri, retriever=self.retriever, caption=caption)

            if props:
                properties = resource.props
                for key, values in props: # XXX: does not belong here!?
                    properties[key] = values

            refs[rel].append(resource) # TODO: dedup?
        return dict(refs)

    @memoized_property
    def props(self):
        return PropertyList(self.missing_property_handler)

    @memoized_property
    def document(self):
        if not self.fetched:
            self.fetch()

        return parse(self._content, self.uri)

    def fetch(self):
        # reset memoized properties
        for prop, attrib in getattr(self, "_memoized_properties", []):
            delattr(self, attrib)

        self._content = self.retriever(self.uri)
        self.fetched = True

        uri, title = extract_metadata(self.document)
        if uri:
            self.uri = uri
        if title:
            self.caption = title

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


Action = namedtuple("Action", ["uri", "caption", "fields"])
