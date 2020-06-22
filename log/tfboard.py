from .core import Logger as _Logger

import tensorflow as tf
assert tf.__version__[0] == "2"


class TfScalarLogger(_Logger):

    def __init__(self, writer):
        if isinstance(writer, str):
            self.writer = tf.summary.create_file_writer(dirpath)
        else:
            self.writer = writer

    def __call__(self, _shared, tag, value, step=None, description=None):
        with self.writer.as_default():
            tf.summary.scalar(tag, value, step or getattr(_shared, "step", None), description)

    def close(self):
        try:
            self.writer.close()
        except:
            pass


del _Logger
