Web-discoverable Hypermedia (WDH)
=================================

WDH is a proposal for employing HTML as a hypermedia format in HTTP services. It
uses HTML's standardized semantics, establishing a few simple conventions to
express data structures, links and actions.

By relying on established semantics, WDH can take advantage of HTML's existing
ecosystem. This includes web browsers, which means that WDH APIs can be explored
and inspected interactively without the need for additional tools.

This effort is partly inspired by Jon Moore's
[Building Hypermedia APIs with HTML].


Alternatives
------------

Existing hypermedia formats — e.g. [AtomPub], [HAL], [JSON-LD],
[Collection+JSON], [Siren] etc. — are typically based on JSON or XML. As such,
they need to redefine most of the concepts already well-established within HTML
(arguably the web's original hypermedia format) — notably links and forms.

JSON in particular has numerous advantages: It's simple, lightweight and
ubiquitous. However, arguably most of those advantages become less relevant when
entering hypermedia territory, due to the aforementioned need to establish
semantics that go beyond its origins as a barebones data exchange format.

Note that WDH's primary purpose is not to augment existing GUIs, as the
assumption is that typically end-users' needs are significantly different from
machines' (e.g. regarding workflows, access patterns, efficiency requirements
etc.), warranting a strict separation. Thus for certain scenarios, in-page
annotations via [Microdata], [microformats] or [RDFa] might be a more suitable
approach.


Format Description
------------------

WDH documents are valid HTML5 documents. While only a subset of HTML is
specified here, documents may arbitrarily be extended with additional HTML
elements — provided WDH structures remain undisturbed.

WDH establishes three types of machine-readable content: data structures
("properties"), links and actions.


### Links

Links (`link` or `a` elements) can either augment the current resource or
reference related documents. This relationship between the current resource and
the link target is expressed via [link relations].

Link relations are scoped to the respective link's nearest `article` parent
element, if any (see [Embedded Resources]), otherwise to the entire document —
and thus apply to the associated resource.

```html
…
<head>
    <title>Hello World</title>
    <link rel="self" href="/items/1">
</head>
<body>
    <h1>Hello World</h1>
    <a href="/items" rel="collection">all items</a>

    <details>
        <summary>
            <a href="/authors/jod" rel="author">John Doe</a>
        </summary>
        <article>
            <h1>John Doe</h1>
            <a href="/authors/jad" rel="next">Jane Doe</a>
        </article>
    </details>
</body>
…
```


### Properties

Properties are data structures associated with a resource. They are expressed
as key-value pairs  (`dt` and `dd`, respectively) within a description list
(`dl`). Keys are always strings, values may constitute either primitives or
compound values:

```html
…
<dl>
    <dt>title</dt>
    <dd>Hello World</dd>

    <dt>tags</dt>
    <dd>
        <ul>
            <li>foo</li>
            <li>bar</li>
            <li>baz</li>
        </ul>
    </dd>

    <dt>pubdate</dt>
    <dd><time datetime="2015-09-07">September 7, 2015</time></dd>

    <dt>pages</dt>
    <dd data-type="number">4</dd>
</dl>
…
```

Supported data types for `dd` elements:

* string: any text value unless otherwise specified
* number: text value with `data-type="number"` — any signed decimal number
  with an optional fractional part, may use exponential E notation
* boolean: "true" or "false" text values with `data-type="boolean"`
* timestamp: a `time` element with arbitrary `datetime` precision
* set: a `ul` element
* array: an `ol` element
* map: a `dl` element

Compound values (i.e. set, array or map) may be arbitrarily nested. Unknown
`data-type` values are ignored, defaulting to string.

Like link relations, properties are scoped to the nearest `article` parent
element, if any (see [Embedded Resources]), otherwise to the entire document.


Embedded Resources
------------------

Any resource may embed other resources, either partially or in its entirety,
within a `details` section:

```html
<h1>Authors</h1>
<ul>
    <li>
        <a href="/authors/jod" rel="author">John Doe</a>
    </li>
    <li>
        <details>
            <summary>
                <a href="/authors/jad" rel="author">Jane Doe</a>
            </summary>
            <article>
                <dl>
                    <dt>name</dt>
                    <dd>Jane Doe</dd>

                    <dt>e-mail</dt>
                    <dd>jad@example.org</dd>
                </dl>
            </article>
        </details>
    </li>
</ul>
```

The resource referenced within `summary` is embedded as an adjacent `article`
element.

Clients may choose to ignore embedded resources and follow the link relation
instead.


Media Type Considerations
-------------------------

serving as `text/html` allows exploration via web browsers — however, this means
that a resource cannot have both (unless resorting to `application/xhtml+xml`)
an API-specific and a UI-specific representation (cf.
[Alternatives](#alternatives))


Open Issues
-----------

* media type, cf. [Media Type Considerations](#media-type-considerations)
* semantic augmentation, e.g. via Microdata
* `dd > pre`, e.g. for code snippets
* actions (i.e. forms)


[Building Hypermedia APIs with HTML]: http://www.infoq.com/presentations/web-api-html
[AtomPub]: https://tools.ietf.org/html/rfc5023
[HAL]: https://tools.ietf.org/html/draft-kelly-json-hal
[JSON-LD]: http://json-ld.org
[Collection+JSON]: http://amundsen.com/media-types/collection/
[Siren]: https://github.com/kevinswiber/siren
[Microdata]: https://html.spec.whatwg.org/multipage/microdata.html#microdata
[microformats]: http://microformats.org
[RDFa]: http://rdfa.info
[link relations]: https://blog.whatwg.org/the-road-to-html-5-link-relations#what
[Embedded Resources]: #embedded-resources
