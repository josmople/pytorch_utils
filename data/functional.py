
#####################################################
# Basic Functions
#####################################################


def identity_transform(x):
    return x


#####################################################
# Dataset Operations
#####################################################

def dpipe(dataset=None, operators=[]):
    if dataset is None:
        from functools import partial
        return partial(dpipe, operators=operators)

    if callable(operators):
        return operators(dataset)

    for operator in operators:
        dataset = operator(dataset)
    return dataset


def dmap(values=None, transform=None, force_iter=False):
    if values is None:
        from functools import partial
        return partial(dmap, transform=transform, force_iter=force_iter)

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
    if len(datasets) <= 0:
        from functools import partial
        return partial(dzip, zip_transform=zip_transform)

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
    if len(datasets) <= 0:
        from functools import partial
        return partial(dcombine, comb_transform=comb_transform)

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
    if dataset is None:
        from functools import partial
        return partial(daugment, aug_fn=aug_fn)

    aug_fn = aug_fn or identity_transform
    if isinstance(aug_fn, (list, tuple)):
        from torchvision.transforms import Compose
        aug_fn = Compose(aug_fn)

    from .model import AugmentedDataset
    return AugmentedDataset(dataset, aug_fn)


def dcache(dataset=None, cache=None):
    assert cache is not None

    if dataset is None:
        from functools import partial
        return partial(dcache, cache=cache)

    from .model import CachedDataset
    return CachedDataset(dataset, cache)


#####################################################
# Dataset Constructors
#####################################################

def files(paths, transform=None, *, use_glob=True, glob_recursive=False, sort_key=None, sort_reverse=False):
    from .utils import glob
    if use_glob:
        return dmap(glob(paths, recursive=glob_recursive, key=sort_key, reverse=sort_reverse, unique=True), transform)
    else:
        return dmap(paths, transform)


def images(paths, transform=None, img_exts=["jpg", "jpeg", "png"], *, img_loader=None, img_autoclose=True, use_glob=True, glob_recursive=False, sort_key=None, sort_reverse=False):
    from .utils import fill
    paths = fill(paths, ext=img_exts)

    from torchvision.transforms.functional import to_tensor
    transform = transform or to_tensor
    if isinstance(transform, (list, tuple)):
        from torchvision.transforms import Compose
        transform = Compose(transform)
    assert callable(transform)

    if not callable(img_loader):
        from importlib.util import find_spec as module_exists

        if module_exists("imageio"):
            from imageio import get_reader
            from PIL.Image import fromarray

            def img_loader(path):
                img_numpy = get_reader(path).get_next_data()
                return fromarray(img_numpy)
        elif module_exists("PIL"):
            from PIL.Image import open as pil_loader
            img_loader = pil_loader
        else:
            from .utils import eprint
            eprint(
                "Default image loader is imageio and/or pillow (PIL).",
                "Module 'imageio' or 'PIL' not found!",
                "Try 'pip install imageio' or 'pip install pillow' or provide custom 'img_loader'")
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
    return files(paths, img_transform, use_glob=use_glob, glob_recursive=glob_recursive, sort_key=sort_key, sort_reverse=sort_reverse)


def tensors(paths, transform=None, *, tensor_loader=None, use_glob=True, glob_recursive=False, sort_key=None, sort_reverse=False):
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
            from .utils import eprint
            eprint("Default tensor loader is PyTorch (torch). Module 'torch' not found! Install PyTorch or provide custom 'tensor_loader'")
            raise e

    def tensor_transform(path):
        tensor = torch_loader(path)
        return transform(tensor)

    from .utils import glob
    return files(paths, tensor_transform, use_glob=use_glob, glob_recursive=glob_recursive, sort_key=sort_key, sort_reverse=sort_reverse)


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


def cache_text(cache_dir, array=False, make_dir=True):
    from os import linesep

    if array:
        def load_text(path):
            with open(path, "r") as f:
                lines = f.readlines()
            return list(filter(lambda x: x.strip(linesep), lines))

        def save_text(path, lines):
            text = str.join(linesep, lines)
            with open(path, "w+") as f:
                f.write(text)
    else:
        def load_text(path):
            with open(path, "r") as f:
                return f.read()

        def save_text(path, text):
            with open(path, "w+") as f:
                f.write(text)

    return cache_file(cache_dir, load_fn=load_text, save_fn=save_text, make_dir=make_dir)


def cache_json(cache_dir, load_kwds=None, save_kwds=None, make_dir=True):
    from json import load, dump

    def load_json(path):
        with open(path, "r") as f:
            return load(f, **(load_kwds or {}))

    def save_json(path, obj):
        with open(path, "w+") as f:
            return dump(obj, **(save_kwds or {}))

    return cache_file(cache_dir, load_fn=load_json, save_fn=save_json, make_dir=make_dir)


#####################################################
# Cache Dataset Macros
#####################################################

def dcache_file(dataset, cache_dir, load_fn, save_fn, make_dir=True):
    cache = cache_file(cache_dir, load_fn, save_fn, make_dir=make_dir)
    return dcache(dataset, cache)


def dcache_tensor(dataset, cache_dir, make_dir=True):
    cache = cache_tensor(cache_dir, make_dir=make_dir)
    return dcache(dataset, cache)


def dcache_text(dataset, cache_dir, array=False, make_dir=True):
    cache = cache_text(cache_dir, array=array, make_dir=make_dir)
    return dcache(dataset, cache)


def dcache_json(dataset, cache_dir, load_kwds=None, save_kwds=None, make_dir=True):
    cache = cache_json(cache_dir, load_kwds=load_kwds, save_kwds=save_kwds, make_dir=make_dir)
    return dcache(dataset, cache)
