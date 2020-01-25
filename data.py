import torch.utils.data as data

from .defaults import image_loader


class ValueDataset(data.Dataset):

    def __init__(self, values, transform=None):
        self.values = values
        self.transform = transform

    def __len__(self):
        return len(self.values)

    def __getitem__(self, idx):
        value = self.values[idx]
        if self.transform is None:
            return value
        return self.transform(value)


class ZipDataset(data.Dataset):

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
        if self.zip_transform is None:
            return tuple(array)
        return self.zip_transform(*array)


class FileDataset(ValueDataset):

    def __init__(self, pathname, transform=None, *, recursive=False, key=None, reverse=False):
        from .io import glob
        values = glob(pathname, recursive=recursive, key=key, reverse=reverse)
        super().__init__(values=values, transform=transform)


class ImageDataset(FileDataset):

    def __init__(self, pathname, transform=None, *, loader=image_loader, recursive=False, key=None, reverse=False):
        from torchvision.transforms import Compose

        if transform is None:
            transform = (lambda x: x)

        transforms = Compose([
            loader,
            transform
        ])

        super().__init__(pathname=pathname, transform=transforms, recursive=recursive, key=key, reverse=reverse)
