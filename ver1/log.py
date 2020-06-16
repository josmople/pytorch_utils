from abc import ABC as _ABC, abstractmethod as _abstractmethod
import string as _string


class Context:

    def __init__(self, **kwds):
        object.__setattr__(self, "data", kwds)

    def __invert__(self):
        return object.__getattribute__(self, "data")

    def __getattr__(self, k):
        v = (~self)[k]
        if callable(v):
            return v()
        return v

    def __setattr__(self, k, v):
        (~self)[k] = v

    def __len__(self):
        return len(~self)

    def __getitem__(self, k):
        return (~self)[k]

    def __setitem__(self, k, v):
        (~self)[k] = v

    def __delitem__(self, v):
        del (~self)[v]

    def __contains__(self, k):
        return k in ~self

    def __iter__(self):
        return iter(~self)

    def __str__(self):
        return str(~self)

    def __repr__(self):
        return f"Context(data={str(~self)})"


class _DefaultStrFormatter(_string.Formatter):
    def __init__(self, default_fn=lambda k: f"{{{k}}}"):
        self.default_fn = default_fn

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default_fn(key))

        if key >= 0 and key < len(args):
            return args[key]

        return self.default_fn(key)


_formatter = _DefaultStrFormatter(default_fn=lambda k: f"{{{k}}}")


class PathResolution:

    def __init__(self, *paths, default_prepare=True, default_meta=None):
        from os.path import join
        self.dirpath = join(*paths, "")
        self.default_prepare = default_prepare
        self.default_meta = default_meta

    def resolve_path(path, vals):
        return _formatter.vformat(path, args=[], kwargs=vals)

    def prepare_path(path):
        dirpath = dirname(path)
        if not exists(dirpath) or isfile(dirpath):
            makedirs(dirpath)

    def __call__(self, *paths, prepare=None, meta=None):
        from os.path import join, dirname, exists, isfile, normpath
        from os import makedirs

        path = join(self.dirpath, *paths)

        if self.default_meta is not None:
            path = self.resolve_path(path, self.default_meta)
        if meta is not None:
            path = self.resolve_path(path, meta)

        if self.default_prepare if prepare is None else prepare:
            self.prepare_path(path)

        return normpath(path)


def timestamp(template="%Y-%m-%d %H-%M-%S.%f"):
    from datetime import datetime
    now = datetime.now()
    path = now.strftime(template)
    return path


def create_logdir(dirpath="logs/{start_ts}", **configs):
    start_ts = timestamp()

    def default_meta():
        meta = {
            'start_ts': start_ts,
            'ts': timestamp(),
        }
        for key in configs:
            val = configs[key]
            if callable(val):
                val = val()
            meta[key] = val
        return meta

    return LogDir(
        dirpath.format(**default_meta()),
        default_prepare=True,
        default_meta=default_meta
    )


class PytorchLogger:

    def __init__(self, logdir="logs/{start_ts}", tbpath="tensorboard", msgpath="logs.txt"):

        if isinstance(logdir, str):
            self.logdir = create_logdir(
                logdir,
                tbpath=tbpath,
                msgpath=msgpath
            )
        elif isinstance(logdir, PathResolution):
            self.logdir = logdir
        else:
            raise ValueError("Param `logdir` must be <str> or <PathResolution>")

        self.tbpath = tbpath
        self.msgpath = msgpath

        self.tbwriter = None
        self.tbwriterpath = None

    def log_pytorch(self, path, obj):
        from torch import save
        save(obj, self.logdir(path))

    def log_module(self, path, module):
        from torch.nn import Module
        from torch import save
        assert isinstance(module, Module)
        save(module.state_dict(), self.logdir(path))

    def log_artifact(self, destpath, srcpath, follow_symlinks=True):
        from shutil import copyfile
        copyfile(srcpath, self.logdir(destpath))

    def log_scalar(self, tag, value, step):
        import tensorflow as tf
        assert tf.__version__[0] == '2'

        if self.tbwriter is None:
            if self.tbpath is None:
                raise ValueError("Attribute `tbpath` is <None>")

            self.tbwriterpath = self.logdir(self.tbpath)
            self.tbwriter = tf.summary.create_file_writer(self.tbwriterpath)

        with self.tbwriter.as_default():
            tf.summary.scalar(tag, value, step)

    def log_image(self, path, img, nrow=8, **kwargs):
        from torch import Tensor
        from torchvision.utils import save_image
        from PIL.Image import Image

        path = self.logdir(path)

        if isinstance(img, Tensor):
            tensor = img.cpu()
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
            if tensor.dim() == 4:
                save_image(tensor.cpu(), path, nrow=nrow, **kwargs)
            else:
                raise NotImplementedError("Supported `torch.Tensor` formats: 4-dim (NxCxHxW), 3-dim (CxHxW)")
        elif isinstance(img, Image):
            img.save(path, **kwargs)
        else:
            raise NotImplementedError("Supported image formats: `torch.Tensor`, `PIL.Image`")

    def log_json(self, path, obj, indent=4, **kwargs):
        from json import dump
        with open(self.logdir(path), "w") as f:
            dump(obj, f, indent=indent, **kwargs)

    def log_msg(self, msg, path=None, template="[%Y-%m-%d %H:%M:%S.%f][{fname}:{lineno:05}] {msg}\n"):
        from datetime import datetime
        from inspect import getframeinfo, currentframe

        template_timestamp = datetime.now().strftime(template)

        prevframe = getframeinfo(currentframe().f_back)
        fname, lineno = prevframe.filename, prevframe.lineno

        output = template_timestamp.format(fname=fname, lineno=lineno, msg=str(msg))

        if path is None:
            path = self.msgpath
        if path is None:
            return output

        with open(self.logdir(path), "a") as f:
            f.write(output)

        return output
