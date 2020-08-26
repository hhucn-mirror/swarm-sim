import logging
import math
import random

from lib.oppnet.communication import multicast_message_content
from lib.oppnet.message_types import CardinalDirection, PredatorSignal
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.particles import FlockMode
from lib.swarm_sim_header import get_direction_between_coordinates


class Mixin:
    def __update_predator_escape_direction(self, predator_coordinates, use_cardinal_location=False,
                                           use_relative_location=False):
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

        if not current_escape_direction or current_escape_direction == new_escape_direction:
            return new_escape_direction
        x_sum = new_escape_direction[0] + current_escape_direction[0]
        y_sum = new_escape_direction[1] + current_escape_direction[1]
        # x value will be equal for pairs (NE, SE) and (NW, SW) -> return E or W respectively
        if current_escape_direction[0] == new_escape_direction[0]:
            return math.copysign(1, current_escape_direction[0]), 0, 0
        elif current_escape_direction in [MobilityModel.E, MobilityModel.W] \
                and new_escape_direction in [MobilityModel.E, MobilityModel.W]:
            # E and W -> any of SE, SW, NE, SW, but prefer newer value
            return self.__weighted_direction_choice__(new_escape_direction)
        elif current_escape_direction[1] == 0 or new_escape_direction[1] == 0:
            # E and SE/NE or W and SW/NW -> E or W respectively
            if abs(x_sum) == 1.5:
                return math.copysign(1, x_sum), 0, 0
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
        location = self.relative_flock_location
        if not use_cardinal_location:
            approaching_direction = CardinalDirection.get_direction_between_locations(predator_coordinates, location)
            return CardinalDirection.get_opposite_direction(approaching_direction).value
        location = self.relative_flock_location
        approaching_direction = get_direction_between_coordinates(predator_coordinates, location)
        if not location:
            logging.debug('round {}: opp_particle -> __get_predator_escape_direction() relative_cardinal_location '
                          'of particle {} not set!'.format(self.world.get_actual_round(), self.number))
            return MobilityModel.random_direction()
        return MobilityModel.opposite_direction(approaching_direction)

    def __get_absolute_predator_escape_direction(self, predator_coordinates):
        approaching_direction = get_direction_between_coordinates(predator_coordinates, self.coordinates)
        if approaching_direction == (0, 0, 0):
            return MobilityModel.random_direction()
        opposite = MobilityModel.opposite_direction(approaching_direction)
        return opposite

    def predators_detected_disperse(self, predators):
        new_predator_ids = predator_ids = set([predator.get_id() for predator in predators])

        try:
            self.reset_routing_and_instructs()
        except AttributeError:
            pass

        self.set_flock_mode(FlockMode.Dispersing)
        self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        predator_coordinates = {}

        # take all predators into account
        for predator in predators:
            new_escape_direction = self.__update_predator_escape_direction(predator.coordinates, False, True)
            self.mobility_model.current_dir = new_escape_direction
            if predator.get_id() not in self.__detected_predator_ids__:
                predator_coordinates[predator.get_id()] = predator.coordinates
            else:
                predator_ids.remove(predator.get_id())
        if self.propagate_predator_signal and not predator_ids.issubset(self.__detected_predator_ids__):
            multicast_message_content(self, self.current_neighborhood, PredatorSignal(predator_coordinates))
        self.__detected_predator_ids__ = new_predator_ids
        return self.mobility_model.next_direction(self.coordinates)

    def _extract_escape_direction(self, predator_coordinates, use_cardinal_location=False, use_relative_location=False):
        # if it's a warning sent from a particle, process the list of predator coordinates
        for coordinates in predator_coordinates:
            self.mobility_model.current_dir = self.__update_predator_escape_direction(coordinates,
                                                                                      use_relative_location,
                                                                                      use_cardinal_location)
        return self.mobility_model.current_dir

    def go_to_safe_location(self):
        self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=self.get_a_safe_location()))
        self.set_flock_mode(FlockMode.Regrouping)
        self.instruct_round = None
        return self.mobility_model.next_direction(self.coordinates, self.get_blocked_surrounding_locations())

    def get_a_safe_location(self):
        if self.recent_safe_location is None:
            return self.coordinates
        else:
            return self.recent_safe_location
