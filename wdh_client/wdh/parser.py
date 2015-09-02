from pyquery import PyQuery as pq


def parse(html, base_uri): # TODO: rename?
    doc = pq(html)
    doc.make_links_absolute(base_uri)
    return doc


def extract_properties(container):
    element = container if isinstance(container, pq) else pq(container)

    if element.is_("html"): # XXX: special-casing
        element = element.find("body")

    key = None
    values = []
    for node in element.children("dl").children():
        if node.tag == "dt":
            # return previous pair
            if key is not None:
                yield key, values
            # create new pair
            key = extract_text(node)
            values = []
        else:
            values.append(extract_text(node))
    if key is not None:
        yield key, values


def extract_references(container, base_uri=None):
    element = container if isinstance(container, pq) else pq(container)

    for link in element.find("a[rel]"):
        rel = link.attrib.get("rel")
        uri = link.attrib.get("href")
        caption = extract_text(link)

        # resolve local references (i.e. embedded resources)
        resource_properties = None
        if base_uri and uri.startswith("%s#" % base_uri):
            selector = uri[len(base_uri):]
            container = element.find(selector)
            uri = container.find("a[rel=self]").attr("href")
            resource_properties = extract_properties(container)

        yield rel, uri, caption, resource_properties


def extract_text(node):
    element = node if isinstance(node, pq) else pq(node)
    caption = element.text()
    return caption.strip() if caption else None
