import tensorflow as tf

assert tf.__version__[0] == "2"


class ScalarLogger:

    def __init__(self, writer):
        if isinstance(writer, str):
            self.writer = tf.summary.create_file_writer(dirpath)
        else:
            self.writer = writer

    def __call__(self, tag, value, step=None, description=None):
        with self.writer.as_default():
            tf.summary.scalar(tag, value, step, description)
