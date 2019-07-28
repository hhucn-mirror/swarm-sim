from enum import Enum


def directions_list(exceptions=[]):
    direction_list=[]
    for direction in Directions:
        if direction not in exceptions:
            direction_list.append(direction)
    return direction_list


class Directions(Enum):
    E = 0
    SE = 1
    SW = 2
    W = 3
    NW = 4
    NE = 5
    S = 6

