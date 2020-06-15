

def create_context(**kwds):
    from .context import Context

    def create_internal_context(k):
        return Context(DEFAULT=create_internal_context)

    c = Context(DEFAULT=create_internal_context, **kwds)

    from .basic import timestamp
    from functools import wraps

    @wraps(timestamp)
    def get_timestamp():
        return timestamp(c.ts_template)

    c.ts_template = c.ts_template or "%Y-%m-%d %H-%M-%S.%f"
    c.start_ts = c.start_ts or get_timestamp()
    c.ts = c.ts or c(get_timestamp)

    from os import getcwd
    c.cwd = c.cwd or c(getcwd)

    return c
