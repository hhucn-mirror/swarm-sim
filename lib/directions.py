from enum import Enum


def directions_list(exceptions=[]):
    """
    A list of directions not containing :param exceptions:.
    :param exceptions: Iterable object of Directions
    :type exceptions: Iterable
    :return: List of directions excluding :param exceptions:.
    :rtype: list
    """
    return [direction for direction in Directions if direction not in exceptions]


class Directions(Enum):
    E = 0
    SE = 1
    SW = 2
    W = 3
    NW = 4
    NE = 5
    S = 6
