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


class FileDataset(ValueDataset):

    def __init__(self, pathname, transform=None, *, recursive=False, key=None, reverse=False):
        from .io import glob
        values = glob(pathname, recursive=recursive, key=key, reverse=reverse)
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
