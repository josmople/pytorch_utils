class Logger:

    def __call__(self, ctx, *args, **kwds):
        raise NotImplementedError()

    def close(self):
        pass


def bind_logger(ctx, logger_gen):
    logger = logger_gen(ctx)

    def __bounded_call__(logger_self, *args, **kwds):
        return super(logger_self.__class__, logger_self).__call__(ctx, *args, **kwds)

    newcls = type(
        f"{logger.__class__.__name__}_Bounded_{id(ctx)}",
        (logger.__class__,),
        {"__call__": __bounded_call__}
    )

    logger.__class__ = newcls
    return logger


# class LogMaster:

#     def __setattr__(self, key, val):
#         if isinstance(val, Logger) and not val.__class__.__name__.endswith(f"_Bounded_{id(self.ctx)}"):
#             from copy import deepcopy
#             val = bind_logger(self.ctx, lambda ctx: deepcopy(val))
#         object.__setattr__(self, key, val)
