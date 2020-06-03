from enum import Enum

import numpy as np


def get_locations_north_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        x_range = np.append(
            np.arange(x - 0.5, x - 0.5 * (hop + 1), -0.5),
            np.arange(x + 0.5, x + 0.5 * (hop + 1), 0.5))
        for x_coordinate in x_range:
            locations.append((x_coordinate, y + hops, z))
    return locations


def get_locations_south_by_hops(location, hops=1):
    (x, y, z) = location
    locations = []
    for hop in range(1, hops + 1):
        x_range = np.append(
            np.arange(x - 0.5, x - 0.5 * (hop + 1), -0.5),
            np.arange(x + 0.5, x + 0.5 * (hop + 1), 0.5))
        for x_coordinate in x_range:
            locations.append((x_coordinate, y - hops, z))
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
    North = 0,
    East = 1,
    South = 2,
    West = 4

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
        if x_diff > y_diff:
            if x_diff > 0:
                return CardinalDirection.East
            else:
                return CardinalDirection.West
        else:
            if y_diff > 0:
                return CardinalDirection.South
            else:
                return CardinalDirection.North


class RelativeLocationMessageContent:
    def __init__(self, queried_directions: [CardinalDirection], is_response=False):
        self.queried_directions = queried_directions
        self.hops_per_direction = \
            {
                CardinalDirection.North: None,
                CardinalDirection.East: None,
                CardinalDirection.South: None,
                CardinalDirection.West: None
            }
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
