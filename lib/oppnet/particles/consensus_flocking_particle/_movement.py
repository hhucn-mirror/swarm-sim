import logging
import random
from collections import Counter

import numpy as np

from lib.oppnet.message_types import CardinalDirection
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.particles import FlockMode
from lib.swarm_sim_header import vector_angle, get_distance_from_coordinates


class Mixin:

    def set_most_common_direction(self, weighted_choice=False, centralisation_force=False):
        """
        Sets the current_dir value of the particle's MobilityModel to the most common value it received from neighbours,
        with a weighted probability of 1/neighbourhood_size, i.e. the size of the current neighbourhood it received
        directions from. The other possibility is for the direction not to change with the inverse probability.
        Furthermore, if :param centralisation_force is set, then the angle between the vector pointing from the particle
        to the flock's relative centre and the most common direction vector will be used as "countering-force"
        to pull the particle towards the centre.

        :param weighted_choice: whether to use weighted choice or not.
        :type weighted_choice: bool
        :param centralisation_force: whether to use a centralisation force or not
        :type centralisation_force: bool
        :return: the most common direction
        """
        neighbourhood_size = len(self.__neighborhood_direction_counter__)
        choice = self.__neighborhood_direction_counter__.most_common(1)[0][0]
        if weighted_choice:
            choice = random.choices([choice, self.mobility_model.current_dir],
                                    [1 / neighbourhood_size, 1 - 1 / neighbourhood_size])[0]
        logging.info("round {}: particle #{} most common: {}".format(self.world.get_actual_round(),
                                                                     self.number, choice))
        if centralisation_force and self.relative_flock_location:
            choice = self.__get_choice_from_consensus_and_centralisation_force(choice)
            if choice and self.mobility_model.current_dir != choice:
                logging.info("round {}: particle #{} changing direction from {} to {}"
                             .format(self.world.get_actual_round(), self.number,
                                     self.mobility_model.current_dir, choice))
        self.reset_neighborhood_direction_counter()
        # initialise with current direction
        self.__neighborhood_direction_counter__[choice] += 1
        return choice

    def __get_choice_from_consensus_and_centralisation_force(self, choice: tuple):
        """
        Takes the choice tuple and combines it with a no movement vector as population in random.choices. Takes the
        inverse of the angle between the particles relative location vector and :param choice as a probability for
        no movement and the relative number of picks for :param choice
        :param choice: a tuple of direction vector and the number of times it was picked
        :type choice: tuple
        :return: a random weighted choice
        :rtype: tuple
        """
        try:
            u, v = np.asarray(self.relative_flock_location[0:2]), np.asarray(choice[0][0:2])
        except TypeError:
            return None
        alpha = vector_angle(u, v)
        population = [choice[0], False]
        probabilities = [choice[1] / len(self.__neighborhood_direction_counter__), abs(alpha) / np.pi]
        return random.choices(population, probabilities, k=1)[0]

    def set_random_weighted_direction(self):
        """
        Sets the current_dir value of the particle's MobilityModel to one of the values it received by interpreting it
        as weighted probability distribution. Weights are proportional to number of times the particle received a
        direction.
        :return: nothing
        """
        neighbourhood_size = len(self.__neighborhood_direction_counter__)
        if neighbourhood_size > 0:
            weights = 1 / np.asarray(list(self.__neighborhood_direction_counter__.values()))
            choice = random.choices(self.__neighborhood_direction_counter__.keys(), weights)
            self.mobility_model.current_dir = choice[0]
            self.reset_neighborhood_direction_counter()

    def set_average_direction(self):
        """
        Sets the current_dir value of the particles MobilityModel to the average value it received from neighbours.
        :return: nothing
        """
        if len(self.__neighborhood_direction_counter__) > 0:
            self.mobility_model.current_dir = self.__average_coordinates__(self.__neighborhood_direction_counter__)
            self.reset_neighborhood_direction_counter()

    def __average_coordinates__(self, directions_counter: Counter):
        """
        Returns the nearest valid coordinates to the average of the collections.Counter variable
        :param directions_counter.

        :param directions_counter: the directions collections.Counter object
        :return: average direction
        """
        total_x, total_y, total_z, total_count = 0, 0, 0, 0
        for (x, y, z), count in directions_counter.items():
            total_x += x * count
            total_y += y * count
            total_z += z * count
            total_count += count
        average_coordinates = total_x / total_count, total_y / total_count, total_z / total_count
        return self.world.grid.get_nearest_valid_coordinates(average_coordinates)

    def __shared_neighbours_directions__(self, neighbour):
        """
        Creates a collections.Counter of the directions of particles that are shared neighbours with :param neighbour.
        :param neighbour: the neighbour to check.
        :return: a collections.Counter of shared neighbour directions.
        """
        shared_neighbours_directions = Counter()
        for neighbours_neighbour in self.__current_neighborhood__[neighbour].get_neighbourhood():
            try:
                direction = self.__current_neighborhood__[neighbours_neighbour].get_direction()
                shared_neighbours_directions[direction] += 1
            except KeyError:
                pass
        return shared_neighbours_directions

    def try_and_fill_flock_holes(self, hops=2):
        """
        Tries to find a free location within the surrounding neighbourhood with maximum :param hops,
        which is closer to the estimated centre of the flock, and move there afterwards
        :param hops: number of hops to scan within for free locations
        :return: the next direction for the particle to move to
        """
        is_edge = self._is_edge_of_flock_()
        free_neighbour_locations = self.get_free_surrounding_locations_within_hops(hops=hops)
        new_ring = self.get_estimated_flock_ring()
        if new_ring is None:
            return self.try_and_find_flock()
        if new_ring == 0:
            self.set_flock_mode(FlockMode.Flocking)
            self.mobility_model.current_dir = MobilityModel.random_direction()
            return None
        new_location = None
        for free_location in free_neighbour_locations:
            tmp = get_distance_from_coordinates(free_location, (0, 0, 0))
            if tmp < new_ring:
                new_ring = tmp
                new_location = free_location
            elif not is_edge and tmp == new_ring:
                new_location = free_location
                new_ring = tmp
        if new_location:
            self.set_flock_mode(FlockMode.Optimising)
            self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=new_location))
            return self.mobility_model.next_direction(self.coordinates)
        else:
            self.set_flock_mode(FlockMode.Flocking)
            self.mobility_model.current_dir = MobilityModel.random_direction()
            return None

    def _is_edge_of_flock_(self):
        for cardinal_direction in CardinalDirection.get_cardinal_directions_list():
            if len(self.get_particles_in_cardinal_direction_hop(
                    cardinal_direction, self.routing_parameters.scan_radius)) == 0:
                return True
        return False

    def try_and_find_flock(self):
        """
        Called if relative location could not be determined. If the particle was previously connected to other
        particles, return in the opposite direction. Else move randomly.
        :return: the next direction for the particle to move to
        """
        self.set_flock_mode(FlockMode.Searching)
        if len(self.__current_neighborhood__) < len(self.__previous_neighborhood__):
            # if the particle had neighbours previously and now less, go in the opposite direction
            self.mobility_model.turn_around()
        elif len(self.__current_neighborhood__) == 0:
            # scan with max scan radius if the particle hasn't had a neighbour
            surrounding = self.scan_for_locations_within(self.routing_parameters.scan_radius)
            if not surrounding:
                self.mobility_model.set_mode(MobilityModelMode.Random)
            else:
                # if other particles found, move towards the first one found
                self.mobility_model.set_mode(MobilityModelMode.POI)
                self.mobility_model.poi = surrounding[0].coordinates
        return self.mobility_model.next_direction(self.coordinates)
