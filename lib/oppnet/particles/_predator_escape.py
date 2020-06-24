import logging
import random

from lib.oppnet.message_types import CardinalDirection
from lib.oppnet.mobility_model import MobilityModel
from lib.swarm_sim_header import get_direction_between_coordinates


class Mixin:
    def __update_predator_escape_direction(self, predator_coordinates, use_cardinal_location=False,
                                           use_relative_location=True):
        """
        Calculates an updated escape direction depending on the current escape direction.
        :param predator_coordinates: the coordinates of the predator
        :param use_cardinal_location: boolean whether to use the particle's cardinal location for determining
        the escape direction.
        :return: an updated escape direction
        """
        current_escape_direction = self.mobility_model.current_dir
        if use_relative_location:
            new_escape_direction = self.__get_relative_predator_escape_direction(predator_coordinates,
                                                                                 use_cardinal_location)
        else:
            new_escape_direction = self.__get_absolute_predator_escape_direction(predator_coordinates)

        if not current_escape_direction:
            return new_escape_direction
        if current_escape_direction == new_escape_direction:
            return current_escape_direction
        x_sum = new_escape_direction[0] + current_escape_direction[0]
        y_sum = new_escape_direction[1] + current_escape_direction[1]
        # x value will be equal for pairs (NE, SE) and (NW, SW) -> return E or W respectively
        if current_escape_direction[0] == new_escape_direction[0]:
            return current_escape_direction[0] * 2, 0, 0
        elif current_escape_direction[1] == 0 and new_escape_direction[1] == 0:
            # E and W -> any of SE, SW, NE, SW, but prefer newer value
            return self.__weighted_direction_choice__(new_escape_direction)
        elif current_escape_direction[1] == 0 or new_escape_direction[1] == 0:
            # E and SE/NE or W and SW/NW -> E or W respectively
            if abs(x_sum) == 1.5:
                return x_sum % 1 * 2, 0, 0
            # E and SW/NW or W and SE/NE
            else:
                return random.choice([(x_sum, -y_sum, 0), (-x_sum, y_sum, 0)])
        # NE and NW or SE and SW -> E/W
        elif current_escape_direction[1] == new_escape_direction[1]:
            return random.choice([MobilityModel.E, MobilityModel.W])
        # SE and NW or SW and NE -> E/W/SW/NE or E/W/SE/NW
        else:
            return MobilityModel.random_direction(exclude=[current_escape_direction, new_escape_direction])

    def __get_relative_predator_escape_direction(self, predator_coordinates, use_cardinal_location=False):
        """
        Returns a escape direction from a Predator approaching from :param approaching_direction. This will
        be close to a 180 degree angle from the approaching_direction.
        If :param use_cardinal_location is set, this will try to account for the particle's cardinal location
        in the flock, i.e. northern particles will try to move in a northern direction.
        In such case, if the particles's relative cardinal location in the flock is not set,
        it will return a random direction.
        :param predator_coordinates: coordinates of the predator
        :param use_cardinal_location:
        :return: escape direction
        :rtype: tuple
        """
        location = self.relative_location
        if not use_cardinal_location:
            approaching_direction = CardinalDirection.get_direction_between_locations(predator_coordinates, location)
            return CardinalDirection.get_opposite_direction(approaching_direction).value
        location = self.relative_location
        approaching_direction = get_direction_between_coordinates(predator_coordinates, location)
        if not location:
            logging.debug('round {}: opp_particle -> __get_predator_escape_direction() relative_cardinal_location '
                          'of particle {} not set!'.format(self.world.get_actual_round(), self.number))
            return MobilityModel.random_direction()
        return MobilityModel.opposite_direction(approaching_direction)

    def __get_absolute_predator_escape_direction(self, predator_coordinates):
        approaching_direction = get_direction_between_coordinates(predator_coordinates, self.coordinates)
        return MobilityModel.opposite_direction(approaching_direction)
