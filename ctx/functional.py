def create_context(data=None):
    data = data or {}

    from .core import Context

    def create_internal_context(k):
        return Context(data={}, default=create_internal_context)

    c = Context(data=data, default=create_internal_context)

    from datetime import datetime

    starttime = datetime.now()

    def get_start_timestamp():
        ts = starttime.strftime(c.ts_template)
        return ts

    def get_timestamp():
        now = datetime.now()
        ts = now.strftime(c.ts_template)
        return ts

    c.ts_template = c.ts_template or "%Y-%m-%d %H-%M-%S.%f"
    c.start_ts = c.start_ts or vlambda_nk(get_start_timestamp)
    c.ts = c.ts or vlambda_nk(get_timestamp)

    from os import getcwd
    c.cwd = c.cwd or vlambda_nk(getcwd)

    return c


def vlambda(getter=None, setter=None):
    from .values import LambdaValue
    return LambdaValue(getter, setter)


def vlambda_nk(getter=None, setter=None):
    from functools import wraps

    if getter is not None:
        old_getter = getter
        @wraps(old_getter)
        def getter(k):
            return old_getter()

    if setter is not None:
        old_setter = setter
        @wraps(old_setter)
        def getter(k, v):
            return old_setter(v)

    return vlambda(getter, setter)


def vconst(val, error_msg=None):
    from .values import ConstantValue
    return ConstantValue(val, error=error_msg)


def vproxy(db, readonly=False):
    if readonly:
        DatabaseValue(db, True, False, None, "Data at index `{key}` is read-only")
    return DatabaseValue(db, True, True, None, None)


def vglobals(readonly=False):
    from inspect import stack
    db = stack()[1][0].f_globals

    from .values import DatabaseValue

    if readonly:
        DatabaseValue(db, True, False, None, "Cannot change the value of globals[{key}]")
    return DatabaseValue(db, True, True, None, None)


def vwatch(val, pre_get=None, post_get=None, pre_set=None, post_set=None):
    from .values import EventValue
    v = EventValue(val)

    if pre_get is not None:
        assert callable(pre_get)
        v.pre_get += [pre_get]

    if post_get is not None:
        assert callable(post_get)
        v.post_get += [post_get]

    if pre_set is not None:
        assert callable(pre_set)
        v.pre_set += [pre_set]

    if post_set is not None:
        assert callable(post_set)
        v.post_set += [post_set]

    return v, v
