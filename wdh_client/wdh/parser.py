from pyquery import PyQuery as pq


def extract_properties(node):
    element = node if isinstance(node, pq) else pq(node)

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


def extract_text(node):
    element = node if isinstance(node, pq) else pq(node)
    caption = element.text()
    return caption.strip() if caption else None
