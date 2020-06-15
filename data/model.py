from torch.utils.data import Dataset as _Dataset, IterableDataset as _IterableDataset


class ValueDataset(_Dataset):

    def __init__(self, values, transform):
        assert callable(getattr(values, "__len__", None))
        assert callable(getattr(values, "__getitem__", None))
        assert callable(transform)

        self.values = values
        self.transform = transform

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        value = self.values[idx]
        return self.transform(value)


class ValueIterableDataset(_IterableDataset):

    def __init__(self, values, transform):
        from collections import Iterable
        assert isinstance(values, Iterable)
        assert callable(transform)

        self.values = values
        self.transform = transform

    @staticmethod
    def generator(values, transform):
        for v in values:
            yield transform(v)

    def __iter__(self):
        return self.__class__.generator(self.values, self.transform)


class ZipDataset(_Dataset):

    def __init__(self, datasets, zip_transform=None):
        assert len(datasets) > 0

        assert all([callable(getattr(ds, "__len__", None)) for ds in datasets])
        assert all([callable(getattr(ds, "__getitem__", None)) for ds in datasets])

        assert callable(zip_transform)

        ds0, *dsn = datasets
        assert all([len(ds0) == len(ds) for ds in dsn]), "Sizes of all dataset must be the same"

        self.datasets = datasets
        self.zip_transform = zip_transform

    def __len__(self):
        return len(self.datasets[0])

    def __getitem__(self, idx):
        array = []
        for ds in self.datasets:
            array.append(ds[idx])
        return self.zip_transform(tuple(array))


class ZipIterableDataset(_Dataset):

    def __init__(self, datasets, zip_transform):
        assert len(datasets) > 0

        from collections import Iterable
        assert all([isinstance(ds, Iterable) for ds in datasets])

        assert callable(zip_transform)

        self.datasets = datasets
        self.zip_transform = zip_transform

    @staticmethod
    def generator(datasets, zip_transform):
        for vals in zip(*datasets):
            yield zip_transform(vals)

    def __iter__(self):
        return self.__class__.generator(self.datasets, self.zip_transform)


class AugDataset(_IterableDataset):

    def __init__(self, values, augment):
        from collections import Iterable
        assert isinstance(values, Iterable)
        assert callable(augment)

        self.values = values
        self.augment = augment

    @staticmethod
    def generator(values, augment):
        for v in values:
            for o in augment(v):
                yield o

    def __iter__(self):
        return self.__class__.generator(self.values, self.augment)


class CachedDataset(_Dataset):

    def __init__(self, dataset, cache):
        assert callable(getattr(dataset, "__len__", None))
        assert callable(getattr(dataset, "__getitem__", None))

        assert callable(getattr(cache, "__getitem__", None))
        assert callable(getattr(cache, "__setitem__", None))
        assert callable(getattr(cache, "__contains__", None))

        self.dataset = dataset
        self.cache = cache

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        if idx not in self.cache:
            self.cache[idx] = self.dataset[idx]
        return self.cache[idx]


del _Dataset, _IterableDataset
