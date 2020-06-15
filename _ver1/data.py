from torch.utils.data import Dataset as _Dataset

from .img import pil_loader as _default_image_loader


class ValueDataset(_Dataset):

    def __init__(self, values, transform=None):
        self.values = values
        self.transform = transform

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        value = self.values[idx]
        if callable(self.transform):
            return self.transform(value)
        return value


class ZipDataset(_Dataset):

    def __init__(self, dataset, *others, zip_transform=None):
        assert all([len(dataset) == len(other) for other in others]), "Sizes of all dataset must be the same"

        self.dataset = dataset
        self.others = others
        self.zip_transform = zip_transform

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        array = [other[idx] for other in self.others]
        array.insert(0, self.dataset[idx])
        if callable(self.zip_transform):
            return self.zip_transform(*array)
        return tuple(array)


class AugDataset(_Dataset):

    def __init__(self, root_values, aug_fn=None):
        aug_fn = aug_fn or (lambda x: [x])

        self.root_values = root_values
        self.aug_fn = aug_fn
        self.values = self.compute_values(self.root_values, self.aug_fn)

    def compute_values(self, root_values, aug_fn):
        values = []
        for rv in root_values:
            for av in aug_fn(rv):
                values.append(av)
        return values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        item = self.values[idx]
        if callable(item):
            item = item()
        return item


class FileDataset(ValueDataset):

    def __init__(self, pathname, transform=None, *, recursive=False, key=None, reverse=False):
        from glob import glob

        if isinstance(pathname, str):
            pathname = [pathname]

        assert isinstance(pathname, (list, tuple))
        assert all([isinstance(p, str) for p in pathname])

        values = []
        for path in pathname:
            values += glob(path, recursive=recursive)

        values = sorted(values, key=key, reverse=reverse)
        super().__init__(values=values, transform=transform)


class ImageDataset(FileDataset):

    def __init__(self, pathname, transform=None, *, loader=_default_image_loader, recursive=False, key=None, reverse=False):
        from torchvision.transforms import Compose

        if transform is None:
            transform = (lambda x: x)

        assert callable(transform)
        assert callable(loader)

        transforms = Compose([
            loader,
            transform
        ])

        super().__init__(pathname=pathname, transform=transforms, recursive=recursive, key=key, reverse=reverse)
