Web-discoverable Hypermedia (WDH)
=================================

WDH is a proposal for employing HTML as a hypermedia format in HTTP services.

Existing hypermedia formats<sup id="fna1">[1](#fn1)</sup> are typically based on
JSON or XML and thus need to redefine most of the concepts already
well-established within HTML (arguably the web's original hypermedia format) —
notably links and forms.

JSON in particular has numerous advantages: It's simple, lightweight and
ubiquitous. However, arguably most of those advantages become less relevant when
entering hypermedia territory, due to the aforemention need to establish
semantics that go beyond its origins as a barebones data exchange format.

Thus for some scenarios, HTML might be a more suitable foundation. WDH uses
HTML's standardized semantics and establishes a few simple conventions on top.

This effort is partly inspired by Jon Moore's
[Building Hypermedia APIs with HTML], though WDH opts for simpler fundamentals
(cf. [Semantic Augmentation]).


----

<sup id="fn1">1</sup>
    e.g. [HAL](https://tools.ietf.org/html/draft-kelly-json-hal),
    [JSON-LD](http://json-ld.org),
    [Collection+JSON](http://amundsen.com/media-types/collection/),
    [Siren](https://github.com/kevinswiber/siren) etc.
    [↩](#fna1)


[Building Hypermedia APIs with HTML]: http://www.infoq.com/presentations/web-api-html
[Semantic Augmentation]: #semantic-augmentation
