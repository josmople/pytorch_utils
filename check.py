def is_int_or_pair(i):
    if isinstance(i, int):
        i = i, i
    assert isinstance(i, (tuple, list))
    assert len(i) == 2
    return i
