class DirContext:

    def __init__(self, olddir, newdir):
        self.olddir = olddir
        self.newdir = newdir

    def __enter__(self):
        from os import chdir
        chdir(self.newdir)

    def __exit__(self, exc_type, exc_value, traceback):
        from os import chdir
        chdir(self.olddir)


class BaseDir:

    def __init__(self, dirpath):
        self.dirpath = dirpath

    def __call__(self, *args, **kwargs):
        raise NotImplementedError()

    def cwd(self):
        from os import getcwd
        return DirContext(getcwd(), self.dirpath)


class LogDir:

    def __init__(self, *paths):
        from os.path import join
        self.dirpath = join(*paths)

    def __call__(self, *paths, prepare=True, meta=None):
        from os.path import join, dirname, exists, isfile
        from os import makedirs

        path = join(self.dirpath, *paths)
        if meta is not None:
            path = path.format(**meta)

        if prepare:
            dirpath = dirname(path)
            if not exists(dirpath) or isfile(dirpath):
                makedirs(dirpath)

        return path


class MLDir(LogDir):

    def __init__(self, *paths, METAFILENAME=".meta"):
        from os.path import join
        self.METAFILENAME = METAFILENAME
        self.dirpath = join(*paths)
        self.meta = self.load_meta_file()

    def load_meta_file(self):
        from os.path import exists, isfile, join, isdir
        from os import makedirs
        from json import dump, load

        if not exists(self.dirpath) or isfile(self.dirpath):
            makedirs(self.dirpath)

        metapath = join(self.dirpath, self.METAFILENAME)

        if not exists(metapath) or isdir(metapath):
            with open(metapath, "w+") as f:
                dump({}, f)

        with open(metapath, "r") as f:
            try:
                meta = load(f)
            except:
                raise IOError(f"Failed to load meta file in {metapath}, try to delete the file and try again.")
        return meta

    def save_meta_file(self):
        from os.path import exists, isfile, join, isdir
        from os import makedirs
        from json import dump

        if not exists(self.dirpath) or isfile(self.dirpath):
            makedirs(self.dirpath)

        metapath = join(self.dirpath, self.METAFILENAME)

        if not hasattr(self, "meta") or self.meta is None:
            self.meta = {}

        with open(metapath, "w+") as f:
            dump(self.meta, f)

    def load_state(self):
        return {
            'ts': timestamp()
        }

    def __call__(self, *paths, prepare=True):
        from os import makedirs
        from os.path import join, dirname, exists, isfile

        path = join(self.dirpath, *paths)
        path = path.format(**self.meta, **self.load_state())

        if prepare:
            dirpath = dirname(path)
            if not exists(dirpath) or isfile(dirpath):
                makedirs(dirpath)

        return path


def timestamp(template="%Y-%m-%d %H-%M-%S"):
    from datetime import datetime
    now = datetime.now()
    path = now.strftime(template)
    return path
