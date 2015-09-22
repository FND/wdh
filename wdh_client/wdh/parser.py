from collections import namedtuple, defaultdict

from pyquery import PyQuery as pq


def extract_actions(container):
    element = container if isinstance(container, pq) else parse(container)

    for form in element.find("form[data-rel]"):
        form = pq(form)
        rel = form.attr("data-rel")
        uri = form.attr("action")

        method = form.find("input[name=_method]")
        method = method.attr("value") if method else form.attr("method")

        btn = form.find("button[type=submit]")
        if btn:
            caption = extract_text(btn)
        else:
            btn = form.find("input[type=submit]")
            caption = btn.attr("value")

        fields = defaultdict(list)
        for field in form.find("input, textarea, select"):
            field = pq(field)
            name = field.attr("name")
            value = field.text() if field.is_("textarea") else field.attr("value")

            field = Field(name, value,
                    field.attr("required") is not None, _field_label(field, form))
            fields[name].append(field)

        yield rel, uri, method.upper(), caption, dict(fields)


def extract_properties(container):
    element = container if isinstance(container, pq) else parse(container)

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
    element = container if isinstance(container, pq) else parse(container)

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


def extract_metadata(doc):
    doc = doc if isinstance(doc, pq) else parse(doc)

    head = doc.find("head")
    uri = head.find("link[rel=self]").attr("href")
    title = extract_text(head.find("title"))
    return uri, title


def extract_text(node):
    element = node if isinstance(node, pq) else pq(node)
    caption = element.text()
    return caption.strip() if caption else None


def parse(html, base_uri): # TODO: rename?
    doc = pq(html)
    doc.make_links_absolute(base_uri)
    return doc


def _field_label(field, form):
    label = field.closest("label")
    if label: # field is nested within label
        if field.is_("textarea"): # might include text content
            label = label.clone()
            label.find("textarea").remove()
    else:
        id = field.attr("id")
        if id:
            label = next(label for label in form.find("label")
                    if label.attrib.get("for") == id)

    try:
        return extract_text(label)
    except NameError: # no matching label
        return None


Field = namedtuple("Field", ["name", "value", "required", "caption"])
