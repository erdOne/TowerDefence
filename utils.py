"""General Utility functions."""


def generate_2d_array(x_size, y_size=None, default=None):
    """Init a 2d array."""
    if y_size is None:
        y_size = x_size
    return [[default for _ in range(y_size)] for _ in range(x_size)]


class Object:
    """Mimic JS behavior."""

    def __init__(self, **kwargs):
        """Init the object with dict."""
        self.__keys = []
        for i in kwargs:
            self.__dict__[i] = kwargs[i]
            self.__keys.append(i)
