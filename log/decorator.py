class logpath:

    def __init__(self, argname, resolver="directory"):
        self.argname = argname
        self.resolver = resolver

    def _missing_resolver(self, val):
        raise NotImplementedError(f"There is no such path resolver: {self.resolver}")

    def __call__(self, fn):
        from inspect import getargspec
        from functools import wraps
        from os.path import join, dirname
        from os import makedirs

        argnames = getargspec(fn).args[1:]
        argidx = argnames.index(self.argname)

        @wraps(fn)
        def new_fn(other, *args, **kwds):

            def path_fn(path):
                resolver = getattr(other, self.resolver, self._missing_resolver)
                path = resolver(path) if callable(resolver) else join(str(resolver), path)

                return path

            if self.argname in kwds:
                val = kwds[argname]
                nval = path_fn(val)
                nkwds = kwds.copy()
                nkwds.update({argname: nval})
                return fn(other, *args, **nkwds)

            val = args[argidx]
            nval = path_fn(val)
            nargs = list(args)
            nargs[argidx] = nval
            return fn(other, *nargs, **kwds)

        return new_fn


class overwrite:

    def __init__(self, argname, map_fn, cond_fn=None):
        self.argname = argname
        self.map_fn = map_fn
        self.cond_fn = cond_fn or (lambda v: True)

    def update(self, val):
        if self.cond_fn(val):
            return self.map_fn(val)
        return val

    def __call__(self, fn):
        from inspect import getargspec
        from functools import wraps
        from os.path import join

        argnames = getargspec(fn).args[1:]
        argidx = argnames.index(self.argname)

        @wraps(fn)
        def new_fn(other, *args, **kwds):

            if argname in kwds:
                val = kwds[argname]
                nval = self.update(val)
                nkwds = kwds.copy()
                nkwds.update({argname: nval})
                return fn(other, *args, **nkwds)

            val = args[argidx]
            nval = self.update(val)
            nargs = list(args)
            nargs[argidx] = nval
            return fn(other, *nargs, **kwds)

        return new_fn
