import typing as T


def collate_items(col):
    from torch.utils.data._utils import collate
    return collate.default_collate(col)


def generate_collate_batch(concat_dict: T.Dict[T.Tuple[int, type], T.Callable[[T.List], T.Any]] = dict(), concat_default: T.Callable[[T.List], T.Any] = collate_items):

    def collate_batch(batch):
        db: T.Dict[int, T.List] = {}

        for row_idx, row in enumerate(batch):
            for col_idx, cell in enumerate(row):
                if col_idx not in db:
                    db[col_idx] = []
                db[col_idx].append(cell)

        cols = []

        for col_idx, col in db.items():
            if col_idx in concat_dict:
                fn = concat_dict[col_idx]
            elif type(col[0]) in concat_dict:
                fn = concat_dict[type(col[0])]
            else:
                fn = concat_default
            col = fn(col)
            cols.append(col)

        return cols

    return collate_batch
