from collections import Counter
from enum import Enum

import lib.oppnet.particles as particles
from lib.oppnet.routing import RoutingMap
from lib.swarm_sim_header import free_locations_within_hops, get_distance_from_coordinates
from . import _communication, _movement, _process_messages, _routing
from ...message_types import CardinalDirection
from ...mobility_model import MobilityModelMode


class ConsensusProtocol(Enum):
    SimpleAverage = 1
    MostCommon = 2
    RandomWeighted = 3


class Particle(particles.Particle, _communication.Mixin, _movement.Mixin, _process_messages.Mixin, _routing.Mixin):
    """
    Class for particles in consensus flocking solutions.
    """

    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 ):
        """
        Constructor. Initializes variables
        :param world: simulator world reference
        :param coordinates: particle coordinates
        :param color: particle color
        :param particle_counter: particle number
        :param csv_generator: csv generator object
        :param ms_size: size of the MessageStore
        :param ms_strategy: strategy of the MessageStore
        :param mm_mode: MobilityModelMode
        :param mm_length: length of a walk for specific MobilityModelModes
        :param mm_zone: zone for Zonal MobilityModelMode
        :param mm_starting_dir: starting direction of the particles MobilityModel
        """
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator, ms_size=ms_size, ms_strategy=ms_strategy, mm_mode=mm_mode,
                         mm_length=mm_length, mm_zone=mm_zone, mm_starting_dir=mm_starting_dir)

        self.contacts = RoutingMap()
        self.__neighborhood_direction_counter__ = Counter()
        # initialise with current_direction
        self.__neighborhood_direction_counter__[self.mobility_model.current_dir] += 1

        self.__received_queried_directions__ = {}
        self.relative_flock_location = None
        self.relative_cardinal_location = None
        self.__max_cardinal_direction_hops__ = {}
        self.flock_mode = particles.FlockMode.Flocking
        self.consensus_protocol = self.world.config_data.consensus_protocol
        self._use_weighted_choice = self.world.config_data.weighted_choice
        self._use_centralization_force = self.world.config_data.centralization_force

        self.recent_safe_location = (0, 0, 0)

    def reset_neighborhood_direction_counter(self):
        """
        Resets the neighborhood direction counter.
        :return: None
        """
        self.__neighborhood_direction_counter__ = Counter()

    def reset_max_cardinal_direction_hops(self):
        """
        Resets the maximum cardinal direction hops dictionary.
        :return: None
        """
        self.__max_cardinal_direction_hops__ = {}

    def get_particles_in_cardinal_direction_hop(self, cardinal_direction, hops):
        """
        Returns a list of particles that are surrounding the particle in the :param cardinal_direction with a maximum
        of :param hops.
        :param hops: maximum number of hops checked around the particle
        :param cardinal_direction: the cardinal direction (N, E, S, W) to check
        :type cardinal_direction: CardinalDirection
        :return: the list of particles that surround the particle in the given cardinal direction
        :rtype: [Particle]
        """
        neighbor_locations = CardinalDirection.get_locations_in_direction_hops(self.coordinates, cardinal_direction,
                                                                               hops)
        particle_list = []
        for location in neighbor_locations:
            try:
                particle_list.append(self.world.particle_map_coordinates[location])
            except KeyError:
                pass
        return particle_list

    def update_current_neighborhood(self):
        """
        Resets the current_neighborhood dictionary to only contain those particles within the scan radius
        and updates the previous neighborhood
        :return: the list of current neighbors
        """
        self.previous_neighborhood = self.current_neighborhood
        self.current_neighborhood = {}
        neighbors = self.scan_for_particles_within(self.routing_parameters.interaction_radius)
        for neighbor in neighbors:
            self.current_neighborhood[neighbor] = None
        return neighbors

    def get_free_surrounding_locations_within_hops(self, hops=1):
        """
        Returns the locations within the particles :param hops: neighborhood.
        :param hops: the maximum number of hops from the particle to consider.
        :return: a list free locations
        """
        return free_locations_within_hops(self.world.particle_map_coordinates, self.coordinates, hops, self.world.grid)

    def get_estimated_flock_ring(self):
        """
        Estimates the flock ring number, i.e. the hop distance to the center of the flock.
        :return: estimated flock ring number
        """
        try:
            ring = get_distance_from_coordinates(self.relative_flock_location, (0, 0, 0))
        except TypeError:
            ring = None
        return ring

    def get_next_direction(self):
        """
        Determines the next moving direction based on the particles flock_mode and surroundings such as predators
        and particles which may block a moving direction.
        :return:
        """
        predators_nearby = self.predators_nearby()
        if predators_nearby:
            return self.predators_detected_disperse(predators_nearby)
        if len(self.current_neighborhood) == 0 and self.flock_mode not in [particles.FlockMode.Dispersing,
                                                                           particles.FlockMode.Regrouping]:
            # return self.go_to_safe_location()
            return self.try_and_find_flock()
        if self.mobility_model.mode == MobilityModelMode.POI:
            return self.mobility_model.next_direction(self.coordinates, self.get_blocked_surrounding_locations())
        else:
            mm_next_direction = self.mobility_model.next_direction(self.coordinates)
        if self.flock_mode == particles.FlockMode.QueryingLocation:
            return None
        elif self.flock_mode == particles.FlockMode.FoundLocation:
            return self.try_and_fill_flock_holes()
        elif self.flock_mode == particles.FlockMode.Optimizing:
            return self._get_next_direction_optimising(mm_next_direction)
        elif self.flock_mode == particles.FlockMode.Flocking:
            if self.consensus_protocol == ConsensusProtocol.MostCommon:
                self.set_most_common_direction(self._use_weighted_choice, self._use_centralization_force)
            elif self.consensus_protocol == ConsensusProtocol.SimpleAverage:
                self.set_average_direction()
            elif self.consensus_protocol == ConsensusProtocol.RandomWeighted:
                self.set_random_weighted_direction()
            return self.mobility_model.current_dir
        elif self.flock_mode == particles.FlockMode.Dispersing:
            return self._get_next_direction_dispersing(mm_next_direction)
        elif self.flock_mode == particles.FlockMode.Searching:
            self.query_relative_location()
            return None
        elif self.flock_mode == particles.FlockMode.Regrouping:
            if mm_next_direction is None:
                self.query_relative_location()
            return mm_next_direction

    def _get_next_direction_optimising(self, mm_next_direction):
        """
        Gets the next moving direction for optimizing a particles position in a flock
        :param mm_next_direction: current moving direction
        :return: direction value or None for no movement
        """
        if mm_next_direction is None:
            self.set_flock_mode(particles.FlockMode.Flocking)
            return None
        else:
            self.query_relative_location()
        return mm_next_direction
