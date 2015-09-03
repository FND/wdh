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


def extract_references(container):
    element = container if isinstance(container, pq) else pq(container)

    for link in element.find("a[rel]"):
        link = pq(link)
        rel = link.attr("rel")
        uri = link.attr("href")
        caption = extract_text(link)

        # resolve embedded resource properties
        resource_properties = None
        if link.closest("summary"):
            resource = link.closest("details").children("article")
            resource_properties = extract_properties(resource)

        yield rel, uri, caption, resource_properties


def extract_text(node):
    element = node if isinstance(node, pq) else pq(node)
    caption = element.text()
    return caption.strip() if caption else None
