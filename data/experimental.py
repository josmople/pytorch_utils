

def imgsequences(
        seq_paths, img_paths="{path}/*.{ext}", *,
        seq_transform=None, seq_glob_recursive=False, seq_sort_key=None, seq_sort_reverse=False,
        img_transform=None, img_loader=None, img_autoclose=True, img_exts=["jpg", "jpeg", "png"],
        img_glob_recursive=False, img_sort_key=None, img_sort_reverse=False):

    seq_transform = seq_transform or (lambda x: x)
    assert callable(seq_transform)

    img_transform = img_transform or (lambda x: x)
    assert callable(img_transform)

    if isinstance(img_path, str):
        img_path = [img_path]

    from .search import fill

    def load_sequence(p):
        paths = fill(img_paths, path=p, ext=img_exts)
        seq = images(
            paths, img_transform,
            img_loader=img_loader,
            img_autoclose=img_autoclose,
            img_exts=[],
            glob_recursive=img_glob_recursive,
            sort_key=img_sort_key,
            sort_reverse=img_sort_reverse)
        return seq_transform(seq)

    return files(seq_paths, load_sequence, glob_recursive=seq_glob_recursive, sort_key=seq_sort_key, sort_reverse=seq_sort_reverse)
