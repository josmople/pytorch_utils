class Dirp:

    dirpath = ""

    def __init__(self, *paths):
        from os.path import join
        self.dirpath = join(*paths)

    def __call__(self, *paths):
        from os.path import join
        return join(self.dirpath, *paths)

    def __str__(self):
        return self.dirpath

    def __repr__(self):
        return f"{self.__class__.__name__}(dirpath='{self.dirpath}')"


def context_dirp_formatter(path, ctx):
    return path.format_map(ctx)


class ContextDirp(Dirp):

    def __init__(self, *paths, ctx=None, formatter=context_dirp_formatter, auto_mkdir=True, auto_norm=True):
        super().__init__(*paths)
        self.ctx = ctx or {}
        self.formatter = formatter
        self.auto_mkdir = auto_mkdir
        self.auto_norm = auto_norm

    def _mkdir(self, path):
        from os.path import dirname
        from os import makedirs
        dirpath = dirname(path)
        makedirs(dirpath, exist_ok=True)

    def _norm(self, path):
        from os.path import normpath
        return normpath(path)

    def __call__(self, *paths, auto_mkdir=None, auto_norm=None, ctx_edit_fn=None, formatter_override_fn=None):
        path = super().__call__(*paths)

        if (self.auto_norm if auto_norm is None else auto_norm):
            path = self._norm(path)

        ctx = ctx_edit_fn(self.ctx) if callable(ctx_edit_fn) else self.ctx
        formatter = formatter_override_fn if callable(formatter_override_fn) else self.formatter
        path = formatter(path, ctx)

        if (self.auto_mkdir if auto_mkdir is None else auto_mkdir):
            self._mkdir(path)

        return path
