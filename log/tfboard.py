import tensorflow as tf
assert tf.__version__[0] == "2"


class TfScalarLogger:

    def __init__(self, rootdir):

        if isinstance(rootdir, str):
            self.rootdir = rootdir
            self.writer = tf.summary.create_file_writer(rootdir)

        if isinstance(rootdir, tf.summary.SummaryWriter):
            self.rootdir = None
            self.writer = rootdir

    def __call__(self, tag, step, value, description=None):
        with self.writer.as_default():
            tf.summary.scalar(tag, value, step, description)

    def close(self):
        try:
            self.writer.close()
        except:
            pass
