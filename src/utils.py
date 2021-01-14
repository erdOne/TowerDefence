# pylint: disable=missing-function-docstring
"""General Utility functions."""

from os import path


def generate_2d_array(x_size, y_size=None, default=None):
    """Init a 2d array."""
    if y_size is None:
        y_size = x_size
    return [[default for _ in range(y_size)] for _ in range(x_size)]


class Object:
    """Mimic JS behavior."""

    def __init__(self, **kwargs):
        self.__keys = []
        for i in kwargs:
            self.__dict__[i] = kwargs[i]
            self.__keys.append(i)

    @staticmethod
    def items(obj):
        # pylint: disable=protected-access
        return [(key, obj.__dict__[key]) for key in obj._Object__keys]

    @staticmethod
    def keys(obj):
        return obj.__dict__["__keys"].copy()

    @staticmethod
    def values(obj):
        # pylint: disable=protected-access
        return [obj.__dict__[key] for key in obj._Object__keys]

    def __iter__(self):
        return iter(Object.items(self))


directions = Object(
    forward=(0, 1),
    backward=(0, -1),
    left=(-1, 0),
    right=(1, 0)
)


def color(hex_col):
    """Hex to rgb triple."""
    return (
        int(hex_col[0:2], 16)/255.0,
        int(hex_col[2:4], 16)/255.0,
        int(hex_col[4:6], 16)/255.0,
        1
    )

def abspath(paths):
    return path.splitdrive(path.abspath(paths))[1].replace('\\', '/')
