class ContextNull:

    def __init__(self):
        raise Exception("This class is not meant to be instantiated")


class ContextValue:

    def vget(self, key):
        raise NotImplementedError()

    def vset(self, key, val):
        raise NotImplementedError()

    def vdel(self, key):
        raise NotImplementedError()


class ContextOperation:

    def __call__(self, ctx, data, params):
        pass


class Context:

    def __call__(self, key=ContextNull, val=ContextNull):
        pass

    def __iter__(self):
        pass

    def __contains__(self, obj):
        pass
