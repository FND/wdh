from functools import wraps


def memoized_property(getter):
    attrib = "_%s" % getter.__name__

    @wraps(getter)
    def memoized_getter(self):
        try:
            return getattr(self, attrib)
        except AttributeError:
            setattr(self, attrib, getter(self))
            return getattr(self, attrib)

    return property(memoized_getter)
