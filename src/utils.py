# pylint: disable=missing-function-docstring
"""General Utility functions."""

from os import path
# import math
# from config import map_params

# from panda3d import Vec3


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

# def place(a, l):
#     return (round(a[0]/l), round(a[1]/l))
#
# def view(mypos, theta, phi, dist, get_tile):
#     length = map_params.unit_size
#     direction = (math.cos(theta)*math.cos(phi),math.sin(theta)*math.cos(phi),-math.sin(phi))
#     direction_length = (1+direction[2]**2)**0.5
#     direction_unit = (direction[0] * length / direction_length / 10 , direction[1] * length / direction_length / 10 , direction[2] * length / direction_length / 10 )
#     current = (mypos[0], mypos[1],mypos[2])
#     myplace = place(mypos, length)
#     for _ in range(dist*2):
#         current = ( current[0] + direction_unit[0] ,  current[1] + direction_unit[1] , current[2] + direction_unit[2])
#         if not myplace == place(current, length):
#             if get_tile(current).height < -1 :
#                 return None
#             elif current[2] < 0 :
#                 return None
#             elif current[2] < get_tile(current).height:
#                 return ( current[0] , current[1] , 0 )
#
#
