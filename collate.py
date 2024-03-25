import typing as T

from torch.utils.data._utils.collate import default_collate


def generate_collate_batch(
    concat_dict: T.Dict[int | str | type, T.Callable[[list[T.Any]], T.Any]] | None = None,
    concat_default: T.Callable[[list], T.Any] = default_collate,
):
    concat_dict = {} if concat_dict is None else {**concat_dict}

    def collate_column(items: list[T.Any], *keys: int | str | type) -> T.Any:
        for key in keys:
            if key in concat_dict:
                return concat_dict[key](items)
        return concat_default(items)

    def collate_batch(batch: T.Sequence[T.Any] | T.Mapping[T.Any, T.Any] | T.NamedTuple) -> T.Any:
        row = batch[0]
        row_type = type(row)

        if isinstance(row, T.Mapping):
            return {dictkey: collate_column([d[dictkey] for d in batch], dictkey, type(row[dictkey])) for dictkey in row}

        if isinstance(row, tuple) and hasattr(row, "_fields"):  # namedtuple
            transposed = zip(*batch)
            namedtuple_fields = getattr(row, "_fields")
            return row_type(*(collate_column(samples, index, fieldname, type(samples[0])) for samples, index, fieldname in zip(transposed, range(len(row)), namedtuple_fields)))

        if isinstance(row, T.Sequence):  # lists and tuples
            it = iter(batch)  # check to make sure that the elements in batch have consistent size
            elem_size = len(next(it))
            if not all(len(elem) == elem_size for elem in it):
                raise RuntimeError("each element in list of batch should be of equal size")

            transposed = zip(*batch)
            return row_type([collate_column(samples, index, type(samples[0])) for index, samples in enumerate(transposed)])

        raise TypeError(f"Collation method not found for row type '{row_type}'")

    return collate_batch
