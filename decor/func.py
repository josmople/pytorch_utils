class init_before_first_call:
    """
    Calls an initialize function (i.e. init_fn)
    before the first call to main function (i.e. fn).

    The 'args' of 'init_fn' is same as the 'args'during the initial call to 'fn'

    Example:

    # Wrong
    fn(a, b)
    init_fn() # Will cause error

    # Right
    f(a, b)
    init_fn(a, b)

    # Right
    f(a, b, c)
    init_fn(a, *args, **kwds)

    # Wrong
    f(a, b, c)
    init_fn(b, *args, **kwds) # b could be from args[0] or kwds['b']

    """

    def __init__(self, init_fn=None):
        self.init_fn = init_fn

    def __call__(self, fn):
        init = self.init_fn

        from functools import wraps
        @wraps(fn)
        def new_fn(*args, **kwds):
            needs_init = getattr(new_fn, "needs_init", True)
            if needs_init:
                if init is not None:
                    init(*args, **kwds)
                setattr(new_fn, "needs_init", False)

            return fn(*args, **kwds)

        return new_fn
