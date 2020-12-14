
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
        from .dataset import ValueIterableDataset
        return ValueIterableDataset(values, transform)

    # If dataset[idx] and len(dataset) are available, use ValueDataset
    if callable(getattr(values, "__getitem__", None)) and callable(getattr(values, "__len__", None)):
        from .dataset import ValueDataset
        return ValueDataset(values, transform)

    # Fallback to IterableDataset
    from .dataset import ValueIterableDataset
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

        from .dataset import ZipIterableDataset
        return ZipIterableDataset(datasets, zip_transform)

    # Otherwise, use ZipDataset
    from .dataset import ZipDataset
    return ZipDataset(datasets, zip_transform)


def dcombine(*datasets, comb_transform=None, custom_indexer=None):
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

        from .dataset import CombineIterableDataset
        return CombineIterableDataset(datasets, comb_transform, indexer=custom_indexer)

    # Otherwise, use CombineDataset
    from .dataset import CombineDataset
    return CombineDataset(datasets, comb_transform, indexer=custom_indexer)


def daugment(dataset, aug_fn=None):
    if dataset is None:
        from functools import partial
        return partial(daugment, aug_fn=aug_fn)

    aug_fn = aug_fn or identity_transform
    if isinstance(aug_fn, (list, tuple)):
        from torchvision.transforms import Compose
        aug_fn = Compose(aug_fn)

    from .dataset import AugmentedDataset
    return AugmentedDataset(dataset, aug_fn)


def dcache(dataset=None, cache=None, enable=True):
    assert cache is not None

    if dataset is None:
        from functools import partial
        return partial(dcache, cache=cache, enable=enable)

    if enable:
        not_cache = any([
            getattr(cache, "__getitem__", None) is None,
            getattr(cache, "__setitem__", None) is None,
            getattr(cache, "__contains__", None) is None
        ])
        if callable(cache) and not_cache:
            cache = cache()

        from .dataset import CachedDataset
        return CachedDataset(dataset, cache)

    return dataset


#####################################################
# Dataset Constructors
#####################################################

def numbers(size, transform=None):
    return dmap(range(size), transform)


def glob_files(paths, transform=None, recursive=False, unique=True, sort=True, sort_key=None, sort_reverse=False):
    from .utils import glob
    return dmap(glob(paths, recursive=recursive, unique=unique, sort=sort, sort_key=sort_key, sort_reverse=sort_reverse), transform)


def index_files(pathquery, transform=None, maxsize=None):
    from os import walk
    from os.path import dirname

    def generate_path(idx):
        return pathquery.format(idx, idx=idx, index=idx)

    if maxsize is None:
        dirpath = dirname(generate_path(0))
        maxsize = len(next(walk(dirpath))[2])

    return numbers(maxsize, [
        generate_path,
        transform or identity_transform
    ])


def images(paths, transform=None, *, img_loader="pil", img_autoclose=True):

    from torchvision.transforms.functional import to_tensor
    transform = transform or to_tensor
    if isinstance(transform, (list, tuple)):
        from torchvision.transforms import Compose
        transform = Compose(transform)
    assert callable(transform)

    if isinstance(img_loader, str):
        if img_loader.lower() == "pil":
            from imageio import get_reader
            from PIL.Image import fromarray

            def img_loader(path):
                img_numpy = get_reader(path).get_next_data()
                return fromarray(img_numpy)

        elif img_loader.lower() == "imageio":
            from PIL.Image import open as pil_loader
            img_loader = pil_loader

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

    def img_transform(path):
        img = img_loader(path)
        out = transform(img)
        if img_autoclose and callable(getattr(img, "close", None)):
            if img == out:
                from .utils import eprint
                eprint(f"Warning: Auto-closing image but image is unprocessed: {path}")
            img.close()
        return out

    return dmap(paths, img_transform)


def glob_images(paths, transform=None, img_loader="pil", img_autoclose=True, glob_recursive=False, glob_unique=True, glob_sort=True, sort_key=None, sort_reverse=False):
    paths = glob_files(paths, recursive=glob_recursive, unique=glob_unique, sort=glob_sort, sort_key=sort_key, sort_reverse=sort_reverse)
    return images(paths, transform, img_loader=img_loader, img_autoclose=img_autoclose)


def index_images(pathquery, transform, img_loader="pil", img_autoclose=True, maxsize=None):
    paths = index_files(pathquery, maxsize=maxsize)
    return images(paths, transform, img_loader=img_loader, img_autoclose=img_autoclose)


def tensors(paths, transform=None, tensor_loader=None):
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

    return dmap(paths, transform=tensor_transform)


def glob_tensor(paths, transform=None, tensor_loader=None, glob_recursive=False, glob_unique=True, glob_sort=True, sort_key=None, sort_reverse=False):
    paths = glob_files(paths, recursive=glob_recursive, unique=glob_unique, sort=glob_sort, sort_key=sort_key, sort_reverse=sort_reverse)
    return tensors(paths, transform, tensor_loader=tensor_loader)


def index_tensor(pathquery, transform, tensor_loader=None, maxsize=None):
    paths = index_files(pathquery, maxsize=maxsize)
    return tensors(paths, transform, tensor_loader=tensor_loader)


#####################################################
# Cache Constructors
#####################################################

def cache_create(load_fn, save_fn, exist_fn):
    from .cache import LambdaCache
    return LambdaCache(save_fn=save_fn, load_fn=load_fn, exist_fn=exist_fn)


def cache_dict(preloaded_data=None):
    from .cache import DictCache
    return DictCache(preloaded_data)


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


def cache_text(cache_dir, as_array=False, make_dir=True):
    from os import linesep

    if as_array:
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

def dcache_dict(dataset, preloaded_data=None, enable=True):
    from functools import partial
    cache_gen = partial(cache_dict, preloaded_data=preloaded_data)
    return dcache(dataset, cache_gen, enable)


def dcache_file(dataset, cache_dir, load_fn, save_fn, make_dir=True, enable=True):
    from functools import partial
    cache_gen = partial(cache_file, cache_dir=cache_dir, load_fn=load_fn, save_fn=save_fn, make_dir=make_dir)
    return dcache(dataset, cache_gen, enable)


def dcache_tensor(dataset, cache_dir, make_dir=True, enable=True):
    from functools import partial
    cache_gen = partial(cache_tensor, cache_dir=cache_dir, make_dir=make_dir)
    return dcache(dataset, cache_gen, enable)


def dcache_text(dataset, cache_dir, as_array=False, make_dir=True, enable=True):
    from functools import partial
    cache_gen = partial(cache_text, cache_dir=cache_dir, array=as_array, make_dir=make_dir)
    return dcache(dataset, cache_gen, enable)


def dcache_json(dataset, cache_dir, load_kwds=None, save_kwds=None, make_dir=True, enable=True):
    from functools import partial
    cache_gen = partial(cache_json, cache_dir=cache_dir, load_kwds=load_kwds, save_kwds=save_kwds, make_dir=make_dir)
    return dcache(dataset, cache_gen, enable)
