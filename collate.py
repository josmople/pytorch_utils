import typing as T


def collate_items(col):
    from torch.utils.data._utils import collate
    return collate.default_collate(col)


def generate_collate_batch(concat_dict: T.Dict[T.Union[int, type], T.Callable[[T.List], T.Any]] = dict(), concat_default: T.Callable[[T.List], T.Any] = collate_items):
    concat_dict = concat_dict.copy()

    def collate_column(items: list, *keys) -> T.Any:
        for key in keys:
            if key in concat_dict:
                return concat_dict[key](items)
        return concat_default(items)

    def collate_batch(batch: T.Union[T.Mapping, T.NamedTuple, T.Sequence]) -> T.Any:
        row = batch[0]
        row_type = type(row)

        if isinstance(row, T.Mapping):
            return {key: collate_column([d[key] for d in batch], key, type(row[key])) for key in row}

        if isinstance(row, tuple) and hasattr(row, "_fields"):  # namedtuple
            transposed = zip(*batch)
            return row_type(*(collate_column(samples, idx, key, type(samples[0])) for samples, idx, key in zip(transposed, range(len(row), row._fields))))

        if isinstance(row, T.Sequence):
            # check to make sure that the elements in batch have consistent size
            it = iter(batch)
            elem_size = len(next(it))
            if not all(len(elem) == elem_size for elem in it):
                raise RuntimeError("each element in list of batch should be of equal size")
            transposed = zip(*batch)
            return [collate_column(samples, idx, type(samples[0])) for idx, samples in enumerate(transposed)]

        raise TypeError(f"Collation method not found for type {row_type}")

    return collate_batch
