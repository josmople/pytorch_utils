from . import vals as V

vfn = V.LambdaValue
vconst = V.ConstValue
vglobal = V.GlobalValue
vitem = V.ProxyItemValue
vattr = V.ProxyAttrValue
vfile = V.FileValue


def vfile_text(path, str2obj=str, obj2str=str, allow_remove=True, autocreate=False, file_read_kwds=None, file_write_kwds=None):

    read_text = None
    if str2obj is not None:
        def read_text(path):
            with open(path, "r", **(file_read_kwds or {})) as f:
                text = f.read()
            return str2obj(text)

    write_text = None
    if obj2str is not None:
        def write_text(path, obj):
            text = obj2str(obj)
            with open(path, "w", **(file_write_kwds or {})) as f:
                f.write(text)

    from os import remove
    remove_text = remove if allow_remove else None

    return vfile(path, read_text, write_text, remove_text, autocreate)


def vfile_textlines(path, str2obj=str, obj2str=str, allow_remove=True, autocreate=False, strip=True, file_read_kwds=None, file_write_kwds=None):

    read_textlines = None
    if str2obj is not None:
        def read_textlines(path):
            with open(path, "r", **(file_read_kwds or {})) as f:
                texts = f.readlines()
            for i, text in enumerate(texts):
                text = text.strip() if strip else text
                texts[i] = str2obj(text)
            return tuple(texts)

    write_textlines = None
    if obj2str is not None:
        def write_textlines(path, objs):
            texts = []
            for obj in objs:
                texts.append(obj2str(obj))
            with open(path, "w", **(file_write_kwds or {})) as f:
                f.writelines(texts)

    from os import remove
    remove_textlines = remove if allow_remove else None

    return vfile(path, read_textlines, write_textlines, remove_textlines, autocreate)


def vfile_json(path, allow_read=True, allow_write=True, allow_remove=True, autocreate=False, file_read_kwds=None, file_write_kwds=None, json_load_kwds=None, json_dump_kwds=None):
    from json import dump

    read_json = None
    if allow_read:
        def read_json(path):
            from json import load
            with open(path, "r", **(file_read_kwds or {})) as f:
                return load(f, **(json_load_kwds or {}))

    write_json = None
    if allow_write:
        def write_json(path, obj):
            from json import dump
            with open(path, "w", **(file_write_kwds or {})) as f:
                dump(obj, f, **(json_dump_kwds or {}))

    from os import remove
    remove_json = remove if allow_remove else None

    return vfile(path, read_json, write_json, remove_json, autocreate)


del V
