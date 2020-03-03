from enum import Enum


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
