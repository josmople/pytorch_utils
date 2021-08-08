class ctx:

    def __init__(self, data=None):
        self.φDATA = data or {}

    def __getattr__(self, key):
        raise NotImplementedError()


class root_ctx(ctx):

    def __init__(self, data):
        super().__init__(data)

    @property
    def NOT(self):
        return not_ctx(self.φDATA)

    @property
    def NEW(self):
        return not_ctx(self.φDATA)

    def __getattr__(self, key):
        if key not in self.φDATA:
            from .classes import valuetype
            self.φDATA[key] = valuetype(...)
        return self.φDATA[key]


class not_ctx(ctx):

    def __init__(self, data):
        super().__init__(data)

    def __getattr__(self, key):
        if key not in self.φDATA:
            from .classes import valuetype
            self.φDATA[key] = ~valuetype(...)
        return self.φDATA[key]


class new_ctx(ctx):

    def __init__(self, data):
        super().__init__(data)

    @property
    def NOT(self):
        return new_not_ctx(self.φDATA)

    def __getattr__(self, key):
        from .classes import valuetype
        self.φDATA[key] = valuetype(...)
        return self.φDATA[key]


class new_not_ctx(ctx):

    def __init__(self, data):
        super().__init__(data)

    def __getattr__(self, key):
        from .classes import valuetype
        self.φDATA[key] = ~valuetype(...)
        return self.φDATA[key]
