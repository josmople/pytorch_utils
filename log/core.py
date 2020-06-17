class Combine:

    def __init__(self, values):
        self.Δ = values

    def __getattr__(self, key):
        for v in self.Δ:
            try:
                return getattr(v, key)
            except AttributeError:
                pass
        raise AttributeError(f"Attribute '{key}' not found")


class Logger:

    config = None

    def __getattr__(self, key):
        if self.config is None:
            raise AttributeError("Cannot query 'config', 'config' is 'NoneType'.")
        if key.startswith("__") and key.endswith("__"):
            raise AttributeError("Cannot query 'config' with magic methods, i.e. __<fn>__.")
        return getattr(self.ctx, key)

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()
