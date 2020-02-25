import collections
import logging
import random

import numpy as np

from lib.oppnet.communication import send_message, Message
from lib.oppnet.consensus_flocking.message_types.direction_message import DirectionMessageContent
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel
from lib.oppnet.routing import RoutingMap
from lib.particle import Particle


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
                print("opp_particle -> initialised particle {} with direction {}".format(self.number, mm_starting_dir))
            else:
                mm_starting_dir = world.config_data.mobility_model_starting_dir

        self.mobility_model = MobilityModel(self.coordinates, mm_mode, mm_length, mm_zone, mm_starting_dir)

        self.__init_message_stores__(ms_size, ms_strategy)

        self.routing_parameters = world.config_data.routing_parameters
        self.signal_velocity = world.config_data.signal_velocity

        self.current_instruct_message = None
        self.contacts = RoutingMap()
        self.__previous_neighbourhood__ = None
        self.__current_neighbourhood__ = {}
        self.__neighbourhood_direction_counter__ = collections.Counter()

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
        content = DirectionMessageContent(self.mobility_model.current_dir, list(self.__current_neighbourhood__.keys()))
        for neighbour in self.__current_neighbourhood__.keys():
            message = Message(self, neighbour, self.world.get_actual_round(), content=content)
            send_message(self, neighbour, message)

    def send_all_to_forward(self):
        """
        Tries to forward each message in the send_store.
        :return: nothing
        """
        while len(self.send_store) > 0:
            self.forward_via_contact(self.send_store.pop())

    def check_current_neighbourhood(self):
        """
        Resets the current_neighbourhood dictionary to only contain those particles within the scan radius.
        :return: the list of current neighbours
        """
        self.__current_neighbourhood__ = {}
        neighbours = self.scan_for_particles_in(self.routing_parameters.scan_radius)
        for neighbour in neighbours:
            self.__current_neighbourhood__[neighbour] = None
        return neighbours

    def __update_contacts__(self, message: Message):
        """
        Adds the sender of the :param message as contact for the message's original sender.
        :param message: the message.
        :return: nothing
        """
        self.contacts.add_contact(message.get_sender(), message.get_original_sender(), message.get_hops())

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
            else:
                logging.debug("round {}: opp_particle -> received an unknown content type.")

    def __process_direction_message__(self, message: Message, content: DirectionMessageContent):
        """
        Processes a :param message with :param content.
        :param message: the message to process.
        :param content: the content of the message.
        :return: nothing
        """
        if message.get_sender() not in self.__current_neighbourhood__:
            logging.debug("round {}: opp_particle -> received direction from a non-neighbour.")
        self.__current_neighbourhood__[message.get_sender()] = content
        self.__neighbourhood_direction_counter__[content.get_direction()] += 1

    def set_most_common_direction(self, weighted_choice=False):
        """
        Sets the current_dir value of the particle's MobilityModel to the most common value it received from neighbours,
        with a weighted probability of 1/neighbourhood_size, i.e. the size of the current neighbourhood it received
        directions from. The other possibility is for the direction not to change with the inverse probability.
        :param weighted_choice: boolean whether to use weighted choice or not.
        :return: nothing
        """
        neighbourhood_size = len(self.__neighbourhood_direction_counter__)
        if neighbourhood_size > 0:
            most_common = self.__neighbourhood_direction_counter__.most_common(1)[0][0]
            if weighted_choice:
                choice = random.choices([most_common, self.mobility_model.current_dir],
                                        [1 / neighbourhood_size, 1 - 1 / neighbourhood_size])
            else:
                choice = most_common
            self.mobility_model.current_dir = choice[0]
            self.__neighbourhood_direction_counter__ = collections.Counter()

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
        for neighbours_neighbour in self.__current_neighbourhood__[neighbour].get_neighbourhood():
            try:
                direction = self.__current_neighbourhood__[neighbours_neighbour].get_direction()
                shared_neighbours_directions[direction] += 1
            except KeyError:
                pass
        return shared_neighbours_directions
