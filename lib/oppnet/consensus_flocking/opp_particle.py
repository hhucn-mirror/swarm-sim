import collections
import logging
import random
from enum import Enum

import numpy as np

from lib.oppnet.communication import send_message, Message, multicast_message_content
from lib.oppnet.message_types.direction_message import DirectionMessageContent
from lib.oppnet.message_types.predator_signal import PredatorSignal
from lib.oppnet.message_types.relative_location_message import CardinalDirection, \
    RelativeLocationMessageContent
from lib.oppnet.message_types.safe_location_message import SafeLocationMessage
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.point import Point
from lib.oppnet.routing import RoutingMap
from lib.oppnet.util import get_direction_between_coordinates
from lib.particle import Particle
from lib.swarm_sim_header import vector_angle, free_locations_within_hops, scan_within, \
    get_distance_from_coordinates, get_surrounding_coordinates


class FlockMode(Enum):
    Searching = 0,
    QueryingLocation = 1,
    FoundLocation = 2
    Flocking = 3,
    Dispersing = 4,
    Regrouping = 5,
    Optimising = 6


class Particle(Particle):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 ):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator)
        if not ms_size:
            ms_size = world.config_data.message_store_size
        if not ms_strategy:
            ms_strategy = world.config_data.message_store_strategy

        if not mm_mode:
            mm_mode = world.config_data.mobility_model_mode
        if not mm_length:
            mm_length = world.config_data.mobility_model_length
        if not mm_zone:
            mm_zone = world.config_data.mobility_model_zone
        if not mm_starting_dir:
            if world.config_data.mobility_model_starting_dir == 'random':
                mm_starting_dir = MobilityModel.random_direction()
                logging.info(
                    "opp_particle -> initialised particle {} with direction {}".format(self.number, mm_starting_dir))
            else:
                mm_starting_dir = world.config_data.mobility_model_starting_dir

        self.mobility_model = MobilityModel(self.coordinates, mm_mode, mm_length, mm_zone, mm_starting_dir)

        self.__init_message_stores__(ms_size, ms_strategy)

        self.routing_parameters = world.config_data.routing_parameters
        self.signal_velocity = world.config_data.signal_velocity
        self.signal_range = world.config_data.signal_range

        self.contacts = RoutingMap()
        self.__previous_neighborhood__ = None
        self.__current_neighborhood__ = {}
        self.__neighbourhood_direction_counter__ = collections.Counter()
        # initialise with current_direction
        self.__neighbourhood_direction_counter__[self.mobility_model.current_dir] += 1

        self.__received_queried_directions__ = {}
        self.relative_flock_location = None
        self.relative_cardinal_location = None
        self.__max_cardinal_direction_hops__ = {}

        self.flock_mode = FlockMode.Searching
        self.__detected_predator_ids__ = set()
        self.safe_locations = [(0, 0, 0)]

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
        particles = []
        for location in neighbor_locations:
            try:
                particles.append(self.world.particle_map_coordinates[location])
            except KeyError:
                pass
        return particles

    def __init_message_stores__(self, ms_size, ms_strategy):
        """
        Initialises the particles two MessageStores for forwarding and receiving.
        :param ms_size: the size of the two stores
        :param ms_strategy: the strategy to implement for buffer-management.
        :return: nothing
        """
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

    def set_mobility_model(self, mobility_model):
        """
        Sets the mobility_model of the particle to :param mobility_model.
        :param mobility_model: the mobility model.
        :return: nothing
        """
        self.mobility_model = mobility_model

    def set_routing_parameters(self, routing_parameters):
        """
        Sets the routing_parameters of the particle to :param routing_parameters.
        :param routing_parameters: the routing parameters.
        :return: nothing
        """
        self.routing_parameters = routing_parameters

    def send_direction_message(self):
        """
        Sends a DirectionMessageContent with the current_dir of the particle's mobility_model and its current neighbours
        :return: nothing
        """
        self.__neighbourhood_direction_counter__ = collections.Counter([self.mobility_model.current_dir])
        content = DirectionMessageContent(self.mobility_model.current_dir, list(self.__current_neighborhood__.keys()))
        for neighbour in self.__current_neighborhood__.keys():
            message = Message(self, neighbour, self.world.get_actual_round(), content=content)
            send_message(self, neighbour, message)

    def send_all_to_forward(self):
        """
        Tries to forward each message in the send_store.
        :return: nothing
        """
        while len(self.send_store) > 0:
            self.forward_via_contact(self.send_store.pop())

    def update_current_neighborhood(self):
        """
        Resets the current_neighbourhood dictionary to only contain those particles within the scan radius
        and updates the previous neighbourhood
        :return: the list of current neighbours
        """
        self.__previous_neighborhood__ = self.__current_neighborhood__
        self.__current_neighborhood__ = {}
        neighbours = self.scan_for_particles_within(self.routing_parameters.scan_radius)
        for neighbour in neighbours:
            self.__current_neighborhood__[neighbour] = None
        return neighbours

    def predators_nearby(self):
        return self.scan_for_predators_within(self.routing_parameters.scan_radius)

    def scan_for_predators_within(self, hop):
        return scan_within(self.world.predator_map_coordinates, self.coordinates, hop, self.world.grid)

    def get_free_surrounding_locations_within_hops(self, hops=1):
        """
        Returns the locations within the particles :param hops: neighbourhood.
        :param hops: the maximum number of hops from the particle to consider.
        :return: a list free locations
        """
        return free_locations_within_hops(self.world.particle_map_coordinates, self.coordinates, hops, self.world.grid)

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
            self.flock_mode = FlockMode.Flocking
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
            self.flock_mode = FlockMode.Optimising
            self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=new_location))
            return self.mobility_model.next_direction(self.coordinates)
        else:
            self.flock_mode = FlockMode.Flocking
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
        self.flock_mode = FlockMode.Searching
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

    def __get_all_surrounding_locations__(self):
        """
        Gives all the 1-hop locations around the particle.
        :return: list of 1-hop locations around
        """
        get_surrounding_coordinates(self.coordinates)

    def __update_contacts__(self, message: Message):
        """
        Adds the sender of the :param message as contact for the message's original sender.
        :param message: the message.
        :return: nothing
        """
        self.contacts.add_contact(message.get_sender(), message.get_original_sender(), message.get_hops())
        self.world.update_flock_id_for_particles([message.get_sender(), message.get_original_sender(), self])

    def forward_via_contact(self, message: Message):
        """
        Tries to forward a :param message via the particle's RoutingMap contacts.
        :param message: the message.
        :return: nothing
        """
        try:
            for contact_particle in self.contacts[message.actual_receiver].keys():
                send_message(self, contact_particle, message)
        except KeyError:
            logging.debug("round {}: opp_particle -> no contact to forward message.")

    def process_received(self):
        """
        Processes each message in the rcv_store of the particle.
        :return: nothing.
        """
        while len(self.rcv_store) > 0:
            message = self.rcv_store.pop()
            content = message.get_content()
            self.__update_contacts__(message)
            if isinstance(content, DirectionMessageContent):
                self.__process_direction_message__(message, content)
            elif isinstance(content, RelativeLocationMessageContent):
                self.__process_relative_location_message(message, content)
            elif isinstance(content, PredatorSignal):
                self.__process_predator_signal(message, content)
            elif isinstance(content, SafeLocationMessage):
                self.__process_safe_location_added(message, content)
            else:
                logging.debug("round {}: opp_particle -> received an unknown content type.")

    def __process_direction_message__(self, message: Message, content: DirectionMessageContent):
        """
        Processes a :param message with :param content.
        :param message: the message to process.
        :param content: the content of the message.
        :return: nothing
        """
        if message.get_sender() not in self.__current_neighborhood__:
            logging.debug("round {}: opp_particle -> received direction from a non-neighbour.")
        self.__current_neighborhood__[message.get_sender()] = content
        self.__neighbourhood_direction_counter__[content.get_direction()] += 1

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
        neighbourhood_size = len(self.__neighbourhood_direction_counter__)
        choice = self.__neighbourhood_direction_counter__.most_common(1)[0][0]
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
        self.__neighbourhood_direction_counter__ = collections.Counter()
        # initialise with current direction
        self.__neighbourhood_direction_counter__[choice] += 1
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
        probabilities = [choice[1] / len(self.__neighbourhood_direction_counter__), abs(alpha) / np.pi]
        return random.choices(population, probabilities, k=1)[0]

    def set_random_weighted_direction(self):
        """
        Sets the current_dir value of the particle's MobilityModel to one of the values it received by interpreting it
        as weighted probability distribution. Weights are proportional to number of times the particle received a
        direction.
        :return: nothing
        """
        neighbourhood_size = len(self.__neighbourhood_direction_counter__)
        if neighbourhood_size > 0:
            weights = 1 / np.asarray(list(self.__neighbourhood_direction_counter__.values()))
            choice = random.choices(self.__neighbourhood_direction_counter__.keys(), weights)
            self.mobility_model.current_dir = choice[0]
            self.__neighbourhood_direction_counter__ = collections.Counter()

    def set_average_direction(self):
        """
        Sets the current_dir value of the particles MobilityModel to the average value it received from neighbours.
        :return: nothing
        """
        if len(self.__neighbourhood_direction_counter__) > 0:
            self.mobility_model.current_dir = self.__average_coordinates__(self.__neighbourhood_direction_counter__)
            self.__neighbourhood_direction_counter__ = collections.Counter()

    def __average_coordinates__(self, directions_counter: collections.Counter):
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
        shared_neighbours_directions = collections.Counter()
        for neighbours_neighbour in self.__current_neighborhood__[neighbour].get_neighbourhood():
            try:
                direction = self.__current_neighborhood__[neighbours_neighbour].get_direction()
                shared_neighbours_directions[direction] += 1
            except KeyError:
                pass
        return shared_neighbours_directions

    def query_relative_location(self):
        """
        Sends a message with RelativeLocationMessageContent to each surrounding particle, querying the amount of hops
        in each cardinal direction for a message to reach the outer ring of a flock.
        :return: nothing
        """
        self.flock_mode = FlockMode.QueryingLocation
        self.__max_cardinal_direction_hops__ = {}
        cardinal_directions = CardinalDirection.get_cardinal_directions_list()
        queried_directions_per_particle = {}
        for cardinal_direction in cardinal_directions:
            one_hop_particles = self.get_particles_in_cardinal_direction_hop(cardinal_direction, 1)
            if len(one_hop_particles) > 0:
                queried_directions_per_particle = self.__add_queried_direction__(cardinal_direction, one_hop_particles,
                                                                                 queried_directions_per_particle)
            # scan with maximum scan radius to detect whether the particle is actually at the edge of the flock
            elif len(self.get_particles_in_cardinal_direction_hop(cardinal_direction,
                                                                  self.routing_parameters.scan_radius)) == 0:
                self.__max_cardinal_direction_hops__[cardinal_direction] = 0
        self.__send_relative_location_queries__(queried_directions_per_particle)

    def __add_queried_direction__(self, cardinal_direction, particles, queried_directions_per_particle):
        """
        Adds :param particles to :param queried_directions_per_particle by appending :param cardinal_direction
        to its values.

        :param cardinal_direction: value to append
        :type cardinal_direction: CardinalDirection
        :param particles: list of particles
        :type particles: [Particle]
        :param queried_directions_per_particle: dictionary of particle, [CardinalDirection] pairs
        :type queried_directions_per_particle: dict
        :return: dictionary of particle, [CardinalDirection] pairs
        :rtype: dict
        """
        for particle in particles:
            if particle not in queried_directions_per_particle:
                queried_directions_per_particle[particle] = [cardinal_direction]
            else:
                queried_directions_per_particle[particle].append(cardinal_direction)
        return queried_directions_per_particle

    def __send_relative_location_queries__(self, queried_directions_per_particle: dict):
        """
        Sends RelativeMessageContent to each particle in the keys of :param queried_directions_per_particle.
        Expects queried_directions parameter of RelativeMessageContent as value of
        :param queried_directions_per_particle.

        :param queried_directions_per_particle: dict of particles to send a RelativeMessageContent message to
        :type queried_directions_per_particle: dict
        :return: nothing
        """
        for particle, queried_locations in queried_directions_per_particle.items():
            content = RelativeLocationMessageContent(queried_locations, False, self.__hops_per_direction_for_neighbor())
            send_message(self, particle, Message(self, particle, content=content))

    def __hops_per_direction_for_neighbor(self, queried_directions=None):
        """
        Creates a hops per direction dictionary for all directions in :param queried_directions. If that is None,
        it will create it for all entries in self.__max_cardinal_direction_hops__.
        :param queried_directions: list of directions to include in the dictionary
        :type queried_directions: list
        :return: dictionary of direction, hops
        :rtype: dict
        """
        hops_per_direction = {}
        if not queried_directions:
            for direction, hops in self.__max_cardinal_direction_hops__.items():
                hops_per_direction[direction] = hops + 1
        else:
            for direction in queried_directions:
                if direction in self.__max_cardinal_direction_hops__:
                    hops = self.__max_cardinal_direction_hops__[direction]
                    hops_per_direction[direction] = hops + 1
        return hops_per_direction

    def __process_relative_location_message(self, message, content):
        """
        Processes a RelativeLocationMessageContent. If it's a query, the particle will try to answer it immediately,
        otherwise store it to answer as soon as it receives a reply for the queried directions itself.
        :param message: the message to process
        :type message: Message
        :param content: the content of the message
        :type content: RelativeLocationMessageContent
        :return: nothing
        """

        for direction, hops in content.hops_per_direction.items():
            if direction not in self.__max_cardinal_direction_hops__:
                self.__max_cardinal_direction_hops__[direction] = hops
            elif self.__max_cardinal_direction_hops__[direction] > hops:
                logging.debug("round {}: particle #{} received non-queried hops for direction {}".format(
                    self.world.get_actual_round(), self.number, str(direction)
                ))

        if not content.is_response:
            self.__received_queried_directions__[message.get_original_sender()] = content.queried_directions

        self.__send_relative_location_response__()

        updated_location = RelativeLocationMessageContent.get_relative_location(self.__max_cardinal_direction_hops__)
        if updated_location:
            self.flock_mode = FlockMode.FoundLocation
            if self.relative_flock_location != updated_location:
                self.relative_flock_location = updated_location
                self.relative_cardinal_location = get_direction_between_coordinates(self.relative_flock_location,
                                                                                    (0, 0, 0))

    def __send_relative_location_response__(self):
        """
        Sends a RelativeLocationMessageContent response. This will set the hops inside
        the content to the maximum it knows itself + 1.
        :return: nothing
        """
        for receiver, queried_directions in list(self.__received_queried_directions__.items()):
            hops_per_direction = self.__hops_per_direction_for_neighbor(queried_directions)
            if hops_per_direction:
                content = RelativeLocationMessageContent([], True, hops_per_direction)
                send_message(self, receiver, Message(self, receiver, content=content))
                # remove the directions that are included in the response
                for queried_direction in content.hops_per_direction.keys():
                    self.__received_queried_directions__[receiver].remove(queried_direction)
                    if len(self.__received_queried_directions__[receiver]) == 0:
                        del self.__received_queried_directions__[receiver]

    def __process_predator_signal(self, message, content: PredatorSignal):
        """
        Processes a PredatorSignal message.
        :param message: the message to process
        :type message: Message
        :param content: the content of the message
        :type content: PredatorSignal
        """
        if self.__detected_predator_ids__ and self.__detected_predator_ids__.issuperset(content.predator_ids):
            return
        self.__detected_predator_ids__.update(content.predator_ids)
        escape_direction = self.__extract_escape_direction__(content.predator_coordinates, message)
        self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        self.mobility_model.current_dir = escape_direction
        self.flock_mode = FlockMode.Dispersing
        # forward to all neighbors not in the receiver list, if the message wasn't a broadcast
        if not message.is_broadcast:
            neighbors = set(self.__current_neighborhood__.keys()).union({self})
            new_receivers = content.receivers.symmetric_difference(neighbors)
            content.update_receivers(neighbors)
            if new_receivers:
                multicast_message_content(self, new_receivers, content)

    def __extract_escape_direction__(self, predator_coordinates, message):
        # if it's a warning sent from a particle, process the list of predator coordinates
        for coordinates in predator_coordinates:
            self.mobility_model.current_dir = self.__update_predator_escape_direction(coordinates)
        return self.mobility_model.current_dir

    def __update_predator_escape_direction(self, predator_coordinates, use_cardinal_location=False):
        """
        Calculates an updated escape direction depending on the current escape direction.
        :param predator_coordinates: the coordinates of the predator
        :param use_cardinal_location: boolean whether to use the particle's cardinal location for determining
        the escape direction.
        :return: an updated escape direction
        """
        current_escape_direction = self.mobility_model.current_dir
        new_escape_direction = self.__get_predator_escape_direction(predator_coordinates)
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

    @staticmethod
    def __weighted_direction_choice__(preferred_direction, weight_scale=0.5):
        population = [MobilityModel.NW, MobilityModel.SW, MobilityModel.NE, MobilityModel.SE]
        if preferred_direction == MobilityModel.W:
            weights = [0.25 * 1 + weight_scale, 0.25 * 1 + weight_scale, 0.25, 0.25]
        else:
            weights = [0.25, 0.25, 0.25 * 1 + weight_scale, 0.25 * 1 + weight_scale]
        return random.choices(population, weights, k=1)[0]

    def __get_predator_escape_direction(self, predator_coordinates, use_cardinal_location=False):
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

        approaching_direction = CardinalDirection.get_direction_between_locations(predator_coordinates,
                                                                                  self.coordinates)
        if not use_cardinal_location:
            return CardinalDirection.get_opposite_direction(approaching_direction).value
        if not self.relative_cardinal_location:
            logging.debug('round {}: opp_particle -> __get_predator_escape_direction() relative_cardinal_location '
                          'of particle {} not set!'.format(self.world.get_actual_round(), self.number))
            return MobilityModel.random_direction()
        if approaching_direction.value[0] != 0:
            if self.relative_cardinal_location[1] != 0:
                return approaching_direction.value[0] * -0.5, self.relative_cardinal_location[1], 0
            else:
                return approaching_direction.value[0] * -1, self.relative_cardinal_location[1], 0
        else:
            return np.copysign(0.5, self.relative_cardinal_location[0]), approaching_direction.value[1] * -1, 0

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

    def __process_safe_location_added(self, message, content):
        if content.coordinates not in self.safe_locations:
            self.safe_locations.append(content.coordinates)

    def get_next_direction(self):
        predators_nearby = self.predators_nearby()
        if predators_nearby:
            return self.__predators_detected__(predators_nearby)
        if len(self.__current_neighborhood__) == 0 and self.flock_mode != FlockMode.Dispersing:
            return self.go_to_safe_location()
        if self.mobility_model.mode == MobilityModelMode.POI:
            return self.mobility_model.next_direction(self.coordinates,
                                                      self.get_blocked_surrounding_locations())
        else:
            mm_next_direction = self.mobility_model.next_direction(self.coordinates)
        if self.flock_mode == FlockMode.QueryingLocation:
            return None
        elif self.flock_mode == FlockMode.FoundLocation:
            return self.try_and_fill_flock_holes()
        elif self.flock_mode == FlockMode.Optimising:
            if mm_next_direction is None:
                self.flock_mode = FlockMode.Flocking
                self.mobility_model.current_dir = MobilityModel.random_direction()
                return None
            else:
                self.query_relative_location()
            return mm_next_direction
        elif self.flock_mode == FlockMode.Flocking:
            return self.set_most_common_direction()
        elif self.flock_mode == FlockMode.Dispersing:
            # if the particle stopped moving, try and go to a safe_location
            if self.mobility_model.mode == MobilityModelMode.Manual:
                return self.go_to_safe_location()
            return mm_next_direction
        elif self.flock_mode == FlockMode.Searching:
            self.query_relative_location()
            return None
        elif self.flock_mode == FlockMode.Regrouping:
            if mm_next_direction is None:
                self.query_relative_location()
            return mm_next_direction

    def go_to_safe_location(self):
        self.mobility_model = MobilityModel(self.coordinates, MobilityModelMode.POI, poi=self.get_a_safe_location())
        self.flock_mode = FlockMode.Regrouping
        return self.mobility_model.next_direction(self.coordinates, self.get_blocked_surrounding_locations())

    def get_a_safe_location(self):
        return random.choice(self.safe_locations)

    def __predators_detected__(self, predators):
        predator_ids = set([predator.get_id() for predator in predators])
        if self.flock_mode == FlockMode.Dispersing:
            # reset number of steps
            if not predator_ids.issubset(self.__detected_predator_ids__):
                self.mobility_model.steps = 0
        else:
            self.flock_mode = FlockMode.Dispersing
            self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        if not predator_ids.issubset(self.__detected_predator_ids__):
            predator_coordinates = set()
            # take all predators into account
            for predator in predators:
                self.mobility_model.current_dir = self.__update_predator_escape_direction(predator.coordinates)
                predator_coordinates.add(predator.coordinates)
            multicast_message_content(self, self.current_neighborhood.keys(),
                                      PredatorSignal(predator_ids, predator_coordinates))
            self.__detected_predator_ids__.update(predator_ids)
        return self.mobility_model.next_direction(self.coordinates)

    def move_to(self, direction):
        super().move_to(direction)
        self.mobility_model.update_history(self.coordinates)

    def get_coordinates_as_point(self):
        """
        Converts the particle's coordinates as Point object.
        :return: coordinates as Point
        """
        return Point(self.coordinates[0], self.coordinates[1])

    @property
    def current_neighborhood(self):
        return self.__current_neighborhood__

    @property
    def previous_neighborhood(self):
        return self.__previous_neighborhood__
