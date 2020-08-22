import tensorflow as tf
assert tf.__version__[0] == "2"


class TfScalarLogger:

    def __init__(self, directory):

        if isinstance(directory, str):
            self.directory = directory
            self.writer = tf.summary.create_file_writer(directory)

        if isinstance(directory, tf.summary.SummaryWriter):
            self.directory = None
            self.writer = directory

    def __call__(self, tag, step, value, description=None):
        with self.writer.as_default():
            tf.summary.scalar(tag, value, step, description)

    def close(self):
        try:
            self.writer.close()
        except:
            pass
