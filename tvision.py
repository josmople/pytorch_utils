from .lazy import lazyload as _lazyload, DUMMY_TRUE as _DUMMY_TRUE

from torchvision.transforms import *

functional = _lazyload("torchvision.transforms.functional")
if _DUMMY_TRUE:
    import torchvision.transforms.functional as functional


class ComposeZip:

    def __init__(self, *transforms):
        self.transforms = []
        for transform in transforms:
            if not callable(transform):
                transform = Compose(transform)
            self.transforms.append(transform)

    def __call__(self, *args):
        if len(args) == 1 and len(self.transforms) > 1:
            args = tuple(args[0])
        outs = []
        for arg, transform in zip(args, self.transforms):
            out = transform(arg)
            outs.append(out)
        return tuple(outs)

    def __repr__(self):
        format_string = self.__class__.__name__ + '('
        for i, t in enumerate(self.transforms):
            format_string += '\n'
            format_string += '    Arg{0}={1}'.format(i, t)
        format_string += '\n)'
        return format_string


del _lazyload
