class ContextValue:

    def vget(self, key):
        raise NotImplementedError()

    def vset(self, key, val):
        raise NotImplementedError()


class Context:

    __slots__ = ["Δ", "Φ"]

    def __init__(self, data, default=None):
        object.__setattr__(self, "Δ", data)
        object.__setattr__(self, "Φ", default)

    def __invert__(self):
        return self.Δ

    def __getitem__(self, k):
        if k not in self.Δ and self.Φ is not None:
            if callable(self.Φ):
                self.Δ[k] = self.Φ(k)
            else:
                self.Δ[k] = self.Φ

        v = self.Δ[k]
        if isinstance(v, ContextValue):
            return v.vget(k)
        return v

    def __setitem__(self, k, v):
        if k in self.Δ:
            ov = self.Δ[k]
            if isinstance(ov, ContextValue):
                ov.vset(k, v)
                return
        self.Δ[k] = v

    def __delitem__(self, k):
        del self.Δ[k]

    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v

    def __delattr__(self, k):
        del self[k]

    def __iter__(self):
        return iter(self.Δ)

    def __contains__(self, k):
        return k in self.Δ

    def __len__(self):
        return len(self.Δ)

    def __call__(self, exclude_eval=[]):
        exclude_eval = exclude_eval or []
        exclude_eval += [self]

        out = {}
        for k in iter(self):
            v = self.Δ[k]

            # Evaluates the ContextValue
            if isinstance(v, ContextValue) and (v not in exclude_eval):
                v = v.vget(k)

            # Recursively evaluate Context and prevents circle-references
            if isinstance(v, Context) and (self not in exclude_eval):
                v = v(exclude_eval=exclude_eval)

            out[k] = v

        return out
