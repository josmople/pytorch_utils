# From https://stackoverflow.com/a/2022629


class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.
    """

    def subscribe(self, fn):
        """
        Decorator for function subscription
        """
        self.append(fn)
        return fn

    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return f"Event({list.__repr__(self)})"
