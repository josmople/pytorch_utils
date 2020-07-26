from .context import ContextOperation


class context_ops(ContextOperation):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, ctx, data, params):
        self.fn(ctx, data, params)


@context_ops
def GET(ctx, data, key):
    return data[str(key)]


@context_ops
def SET(ctx, data, kv):
    key, val = kv
    data[str(key)] = val


@context_ops
def DEL(ctx, data, key):
    data[str(key)]
