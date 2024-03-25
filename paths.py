def glob(
    *path_patterns,
    recursive=False,
    sort=True,
    sort_key=None,
    sort_reverse=False,
    **glob_kwds,
) -> list[str]:
    from glob import glob as _glob
    from collections import OrderedDict

    allpaths: list[str] = []
    for path_pattern in path_patterns:
        paths = _glob(str(path_pattern), recursive=recursive, **glob_kwds)
        allpaths.extend(paths)

    allpaths = list(OrderedDict.fromkeys(allpaths).keys())  # Ordered set, remove duplicates

    if sort:
        allpaths = sorted(allpaths, key=sort_key, reverse=sort_reverse)

    return allpaths
