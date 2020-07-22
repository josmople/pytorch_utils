from .decorator import logpath as _logpath


class PyTorchLogger:

    def __init__(self, directory=""):
        self.directory = directory

    @_logpath("path")
    def module(self, path, module, **kwds):
        from torch import save
        save(module.state_dict(), path, **kwds)

    @_logpath("path")
    def tensor(self, path, tensor, **kwds):
        from torch import save
        save(tensor, path, **kwds)

    @_logpath("path")
    def write(self, path, value, linesep="\n", mode="a+", **kwds):
        out = str(value) + linesep
        with open(path, mode, **kwds) as f:
            f.write(out)
        return out

    @_logpath("dstpath")
    def artifact(self, srcpath, dstpath, follow_symlinks=True):
        from shutil import copyfile
        copyfile(src=srcpath, dst=dstpath, follow_symlinks=follow_symlinks)

    @_logpath("path")
    def image(self, path, img):
        from torch import Tensor
        from torchvision.utils import save_image
        from PIL.Image import Image

        if isinstance(img, Tensor):
            tensor = img.cpu()
            if tensor.dim() == 3:
                tensor = tensor.unsqueeze(0)
            if tensor.dim() == 4:
                save_image(tensor.cpu(), path, nrow=nrow, **kwargs)
                return path

            raise NotImplementedError("Supported `torch.Tensor` formats: 4-dim (NxCxHxW), 3-dim (CxHxW)")

        if isinstance(img, Image):
            img.save(path, **kwargs)
            return path

        raise NotImplementedError("Supported image formats: `torch.Tensor`, `PIL.Image`")


del _logpath
