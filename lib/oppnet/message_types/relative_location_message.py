from enum import Enum

import numpy as np


def get_locations_north_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        x_range = np.arange(x - hop * 0.5, x + (hop + 1) * 0.5, 1.0)
        for x_coordinate in x_range:
            locations.append((x_coordinate, y + hop, z))
    return locations


def get_locations_south_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        x_range = np.arange(x - hop * 0.5, x + (hop + 1) * 0.5, 1.0)
        for x_coordinate in x_range:
            locations.append((x_coordinate, y - hop, z))
    return locations


def get_locations_east_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        locations.append((x + hop, y, z))
        locations.append((x + hop - 0.5, y + 1, z))
        locations.append((x + hop - 0.5, y - 1, z))
    return locations


def get_locations_west_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        locations.append((x - hop, y, z))
        locations.append((x - hop + 0.5, y + 1, z))
        locations.append((x - hop + 0.5, y - 1, z))
    return locations


class CardinalDirection(Enum):
    North = 0, 1,
    East = 1, 0,
    South = 0, -1,
    West = -1, 0

    @staticmethod
    def get_cardinal_directions_list():
        return [CardinalDirection.North, CardinalDirection.East, CardinalDirection.South, CardinalDirection.West]

    @staticmethod
    def get_locations_in_direction(location, cardinal_direction):
        (x, y, z) = location
        if cardinal_direction == CardinalDirection.North:
            return [(x + 0.5, y + 1, z), (x - 0.5, y + 1, z)]
        elif cardinal_direction == CardinalDirection.East:
            return [(x + 1, y, z), (x + 0.5, y + 1, z), (x + 0.5, y - 1, z)]
        elif cardinal_direction == CardinalDirection.South:
            return [(x + 0.5, y - 1, z), (x - 0.5, y - 1, z)]
        elif cardinal_direction == CardinalDirection.West:
            return [(x - 1, y, z), (x - 0.5, y + 1, z), (x - 0.5, y - 1, z)]

    @staticmethod
    def get_locations_in_direction_hops(location, cardinal_direction, hops=1):
        if cardinal_direction == CardinalDirection.North:
            return get_locations_north_by_hops(location, hops)
        elif cardinal_direction == CardinalDirection.East:
            return get_locations_east_by_hops(location, hops)
        elif cardinal_direction == CardinalDirection.South:
            return get_locations_south_by_hops(location, hops)
        else:
            return get_locations_west_by_hops(location, hops)

    @staticmethod
    def get_direction_between_locations(location_1, location_2):
        x_diff, y_diff = location_1[0] - location_2[0], location_1[1] - location_2[1]
        if abs(x_diff) > abs(y_diff):
            if x_diff > 0:
                return CardinalDirection.East
            else:
                return CardinalDirection.West
        else:
            if y_diff > 0:
                return CardinalDirection.South
            else:
                return CardinalDirection.North

    def get_opposite_direction(self):
        opposite_value = tuple(np.multiply(self.value, -1))
        return CardinalDirection(opposite_value)


class RelativeLocationMessageContent:
    def __init__(self, queried_directions: [CardinalDirection], is_response=False, hops_per_direction=None):
        self.queried_directions = queried_directions
        if hops_per_direction is not None:
            self.hops_per_direction = hops_per_direction
        else:
            self.hops_per_direction = {}
        self.is_response = is_response

    def set_direction_hops(self, cardinal_direction: CardinalDirection, hops):
        self.hops_per_direction[cardinal_direction] = hops

    @staticmethod
    def get_relative_location(hops_per_direction):
        try:
            x = hops_per_direction[CardinalDirection.West] - hops_per_direction[CardinalDirection.East]
            y = hops_per_direction[CardinalDirection.South] - hops_per_direction[CardinalDirection.North]
        except KeyError:
            return None
        return 1 / 2 * x, 1 / 2 * y, 0
