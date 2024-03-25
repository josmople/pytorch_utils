def ignore_unmatched_kwargs(f):
    """Make function ignore unmatched kwargs.

    If the function already has the catch all **kwargs, do nothing.

    From: https://stackoverflow.com/a/63787701
    """
    from inspect import Parameter, signature
    import functools

    if any(param.kind == Parameter.VAR_KEYWORD for param in signature(f).parameters.values()):
        return f
    #

    keywords_allowed = set([name for name, param in signature(f).parameters.items() if param.kind is Parameter.KEYWORD_ONLY or param.kind is Parameter.POSITIONAL_OR_KEYWORD])

    @functools.wraps(f)
    def inner(*args, **kwargs):
        # For each keyword arguments recognised by f, take their binding from **kwargs received
        filtered_kwargs = {name: kwargs[name] for name in kwargs.keys() if name in keywords_allowed}
        return f(*args, **filtered_kwargs)

    return inner
