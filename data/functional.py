
#####################################################
# Basic Functions
#####################################################


def identity_transform(x):
    return x


#####################################################
# Dataset Operations
#####################################################

def dmap(values, transform=None, force_iter=False):
    transform = transform or identity_transform
    if isinstance(transform, (list, tuple)):
        from torchvision.transforms import Compose
        transform = Compose(transform)

    # If force as IterableDataset
    if force_iter:
        from .model import ValueIterableDataset
        return ValueIterableDataset(values, transform)

    # If dataset[idx] and len(dataset) are available, use ValueDataset
    if callable(getattr(values, "__getitem__", None)) and callable(getattr(values, "__len__", None)):
        from .model import ValueDataset
        return ValueDataset(values, transform)

    # Fallback to IterableDataset
    from .model import ValueIterableDataset
    return ValueIterableDataset(values, transform)


def dzip(*datasets, zip_transform=None):
    zip_transform = zip_transform or identity_transform
    if isinstance(zip_transform, (list, tuple)):
        from torchvision.transforms import Compose
        zip_transform = Compose(zip_transform)

    # Check if there are IterableDataset, then use ZipIterableDataset
    from torch.utils.data import IterableDataset
    if any([isinstance(ds, IterableDataset) for ds in datasets]):

        from .model import ZipIterableDataset
        return ZipIterableDataset(datasets, zip_transform)

    # Otherwise, use ZipDataset
    from .model import ZipDataset
    return ZipDataset(datasets, zip_transform)


def dcombine(*datasets, comb_transform=None):
    comb_transform = comb_transform or identity_transform
    if isinstance(comb_transform, (list, tuple)):
        from torchvision.transforms import Compose
        comb_transform = Compose(comb_transform)

    # Check if there are IterableDataset, then use CombineIterableDataset
    from torch.utils.data import IterableDataset
    if any([isinstance(ds, IterableDataset) for ds in datasets]):

        from .model import CombineIterableDataset
        return CombineIterableDataset(datasets, comb_transform)

    # Otherwise, use ZipDataset
    from .model import CombineDataset
    return CombineDataset(datasets, comb_transform)


def daugment(dataset, aug_fn=None):
    aug_fn = aug_fn or identity_transform
    if isinstance(aug_fn, (list, tuple)):
        from torchvision.transforms import Compose
        aug_fn = Compose(aug_fn)

    from .model import AugmentedDataset
    return AugmentedDataset(dataset, aug_fn)


def dcache(dataset, cache):
    from .model import CachedDataset
    return CachedDataset(dataset, cache)


#####################################################
# Dataset Constructors
#####################################################

def files(paths, transform=None, *, glob_recursive=False, sort_key=None, sort_reverse=False):
    from .utils import glob
    return dmap(glob(paths, recursive=glob_recursive, key=sort_key, reverse=sort_reverse, unique=True), transform)


def images(paths, transform=None, img_exts=["jpg", "jpeg", "png"], *, img_loader=None, img_autoclose=True, glob_recursive=False, sort_key=None, sort_reverse=False):
    from .utils import fill
    paths = fill(paths, ext=img_exts)

    from torchvision.transforms.functional import to_tensor
    transform = transform or to_tensor
    if isinstance(transform, (list, tuple)):
        from torchvision.transforms import Compose
        transform = Compose(transform)
    assert callable(transform)

    if not callable(img_loader):
        try:
            from PIL.Image import open as pil_loader
            img_loader = pil_loader
        except ModuleNotFoundError as e:
            from .utils import eprint
            eprint("Default image loader is pillow (PIL). Module 'PIL' not found! Try 'pip install pillow' or provide custom 'img_loader'")
            raise e

    def img_transform(path):
        img = img_loader(path)
        out = transform(img)
        if img_autoclose and callable(getattr(img, "close", None)):
            if img == out:
                from .utils import eprint
                eprint(f"Warning: Auto-closing image but image is unprocessed: {path}")
            img.close()
        return out

    from .utils import glob
    return files(paths, img_transform, glob_recursive=glob_recursive, sort_key=sort_key, sort_reverse=sort_reverse)


def tensors(paths, transform=None, *, tensor_loader=None, glob_recursive=False, sort_key=None, sort_reverse=False):
    transform = transform or identity_transform
    if isinstance(transform, (list, tuple)):
        from torchvision.transforms import Compose
        transform = Compose(transform)
    assert callable(transform)

    if not callable(tensor_loader):
        try:
            from torch import load as torch_loader
            tensor_loader = torch_loader
        except ModuleNotFoundError as e:
            from sys import stderr
            print("Default tensor loader is PyTorch (torch). Module 'torch' not found! Install PyTorch or provide custom 'tensor_loader'", file=stderr)
            raise e

    def tensor_transform(path):
        tensor = torch_loader(path)
        return transform(tensor)

    from .utils import glob
    return files(paths, tensor_transform, glob_recursive=glob_recursive, sort_key=sort_key, sort_reverse=sort_reverse)


#####################################################
# Cache Constructors
#####################################################

def cache_create(load_fn, save_fn, exist_fn):
    from .cache import LambdaCache
    return LambdaCache(save_fn=save_fn, load_fn=load_fn, exist_fn=exist_fn)


def cache_file(cache_dir, load_fn, save_fn, make_dir=True):

    path_fn = None
    error_msg = "cached_dir must be a string or a callable"

    if isinstance(cache_dir, str):
        def path_fn(idx):
            return cache_dir.format(idx=idx)
        error_msg = "The parameter 'cache_dir:str' must contain the token '{idx}' (e.g. 'cache/{idx:04}.pt') for string formatting"

    elif callable(cache_dir):
        path_fn = cache_dir
        error_msg = "The parameter 'cache_dir:Callable' must receive one argument of type 'int' and return value of type 'str'"

    try:
        sample_filepath = path_fn(0)
        assert isinstance(sample_filepath, str)
    except Exception as e:
        from .utils import eprint
        eprint(error_msg)
        raise e

    if make_dir:
        from os.path import dirname
        dirpath = dirname(sample_filepath)

        from os import makedirs
        makedirs(dirpath, exist_ok=True)

    from .cache import FileCache
    cache = FileCache(path_fn=path_fn, save_fn=save_fn, load_fn=load_fn)

    return cache


def cache_tensor(cache_dir, make_dir=True):
    from functools import wraps
    from torch import load, save

    @wraps(load)
    def load_pytorch_tensor(path):
        return load(path)

    @wraps(save)
    def save_pytorch_tensor(path, tensor):
        return save(tensor, path)

    return cache_file(cache_dir, load_fn=load_pytorch_tensor, save_fn=save_pytorch_tensor, make_dir=make_dir)


#####################################################
# Cache Dataset Macros
#####################################################

def dcache_file(dataset, cache_dir, load_fn, save_fn, make_dir=True):
    cache = cache_file(cache_dir, load_fn, save_fn, make_dir=make_dir)
    return dcache(dataset, cache)


def dcache_tensor(dataset, cache_dir, make_dir=True):
    cache = cache_tensor(cache_dir, make_dir=make_dir)
    return dcache(dataset, cache)
