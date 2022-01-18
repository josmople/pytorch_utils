
def tag(name, directory: str = None, params: dict = None, desc: str = None, delete_similar=False, ext="tag.metadata"):
    if directory is None:
        directory = ""
    if callable(directory):
        directory = directory()
    directory = str(directory)

    if delete_similar:
        from glob import glob
        from os.path import join
        from os import remove
        hits = glob(join(directory, f"{name}*.{ext}"))
        for hit in hits:
            remove(hit)

    if params is None:
        params_text = ""
    else:
        import re
        WHITESPACE_FINDER = re.compile(r"\s+")

        params_text = ""
        for k, v in params.items():
            v = WHITESPACE_FINDER.sub(" ", str(v)).strip()  # Replace any whitespace with single space
            params_text += f"{k}={v}"
        params_text = f"({params_text})"

    from os.path import join
    filename = join(directory, f"{name}{params_text}.{ext}")

    with open(filename, "w+") as f:
        if desc is not None:
            f.write(str(desc))

    return filename
