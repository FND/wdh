from functools import wraps


def memoized_property(getter):
    attrib = "_%s" % getter.__name__

    @wraps(getter)
    def memoized_getter(self):
        try:
            return getattr(self, attrib)
        except AttributeError:
            value = getter(self)
            setattr(self, attrib, value)

            index = getattr(self, "_memoized_properties", None)
            if not index:
                self._memoized_properties = set()
                index = self._memoized_properties
            index.add((getter.__name__, attrib))

            return value

    return property(memoized_getter)
