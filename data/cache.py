class Cache(object):

    def __getitem__(self, idx):
        raise NotImplementedError()

    def __setitem__(self, idx, val):
        raise NotImplementedError()

    def __contains__(self, idx):
        raise NotImplementedError()


class FileCache(Cache):

    def __init__(self, path_fn, save_fn, load_fn):
        self.path_fn = path_fn
        self.save_fn = save_fn
        self.load_fn = load_fn

    def __getitem__(self, idx):
        path = self.path_fn(idx)
        return self.load_fn(path)

    def __setitem__(self, idx, val):
        path = self.path_fn(idx)
        return self.save_fn(path, val)

    def __contains__(self, idx):
        path = self.path_fn(idx)
        from os.path import exists, isfile
        return exists(path) and isfile(path)


class TorchTensorCache(FileCache):

    def __init__(self, path_fn):
        from torch import save, load
        super().__init__(path_fn, lambda p, obj: save(obj, p), load)
