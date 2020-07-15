import logging
import random

import lib.particle
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from ._helper_classes import *
from ._predator_escape import Mixin
from ..communication import broadcast_message, Message, multicast_message_content
from ..message_types import PredatorSignal, SafeLocationMessage
from ..point import Point
from ...swarm_sim_header import scan_within


class Particle(lib.particle.Particle, Mixin):
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
                    "Particle -> initialised particle {} with direction {}".format(self.number, mm_starting_dir))
            else:
                mm_starting_dir = world.config_data.mobility_model_starting_dir

        self.mobility_model = MobilityModel(self.coordinates, mm_mode, mm_length, mm_zone, mm_starting_dir)
        self._init_message_stores__(ms_size, ms_strategy)
        self.routing_parameters = world.config_data.routing_parameters
        self.signal_velocity = world.config_data.signal_velocity
        self.signal_range = world.config_data.signal_range
        self.flock_mode = None
        self.__detected_predator_ids__ = set()
        self.recent_safe_location = None
        self.previous_neighborhood = None
        self.current_neighborhood = {}
        self._flock_member_type = FlockMemberType.follower
        self.propagate_predator_signal = world.config_data.propagate_predator_signal

    def _init_message_stores__(self, ms_size, ms_strategy):
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

    def get_coordinates_as_point(self):
        """
        Converts the particle's coordinates as Point object.
        :return: coordinates as Point
        """
        return Point(self.coordinates[0], self.coordinates[1])

    def set_flock_mode(self, flock_mode):
        self.flock_mode = flock_mode

    def scan_for_predators_within(self, hop):
        return scan_within(self.world.predator_map_coordinates, self.coordinates, hop, self.world.grid)

    def predators_nearby(self):
        return self.scan_for_predators_within(self.routing_parameters.interaction_radius * 5)

    def move_to(self, direction):
        _, within_border = super().move_to(direction)
        if not within_border and self._flock_member_type == FlockMemberType.leader:
            self.broadcast_safe_location(self.coordinates)
        self.mobility_model.update_history(self.coordinates)

    def broadcast_safe_location(self, safe_location=None):
        if not safe_location:
            safe_location = self.get_a_safe_location()
        message = Message(self, None, content=SafeLocationMessage(safe_location))
        broadcast_message(self, message)
        logging.debug("round {}: leader sent new SafeLocationMessage".format(self.world.get_actual_round()))
        return safe_location

    def process_predator_signal(self, message, content: PredatorSignal, use_cardinal_location=False,
                                use_relative_location=False):
        """
        Processes a PredatorSignal message.
        :param message: the message to process
        :type message: Message
        :param content: the content of the message
        :type content: PredatorSignal
        :param use_relative_location: Whether to use the particles relative location in a flock
        :param use_cardinal_location: Whether to use the particles relative cardinal location in a flock
        """
        predator_ids = set(content.predator_coordinates.keys())
        self.__detected_predator_ids__.update(predator_ids)
        escape_direction = self._extract_escape_direction(content.predator_coordinates.values(), use_cardinal_location,
                                                          use_relative_location)
        self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        self.mobility_model.current_dir = escape_direction
        self.set_flock_mode(FlockMode.Dispersing)
        logging.debug("round {}: particle {} applied PredatorSignal. escape direction: {}"
                      .format(self.world.get_actual_round(), self.number, escape_direction))
        # forward to all neighbors not in the receiver list, if the message wasn't a broadcast
        if self.propagate_predator_signal:
            if self.current_neighborhood is dict:
                neighbors = set(self.current_neighborhood.keys()).union({self})
            else:
                neighbors = set(self.current_neighborhood).union({self})
            new_receivers = content.receivers.symmetric_difference(neighbors)
            content.update_receivers(neighbors)
            if new_receivers:
                multicast_message_content(self, new_receivers, content)

    def _get_next_direction_dispersing(self, mm_next_direction):
        # if the particle stopped moving, try and go to a safe_location
        if self.mobility_model.mode == MobilityModelMode.Manual:
            return self.go_to_safe_location()
        return mm_next_direction

    @staticmethod
    def __weighted_direction_choice__(preferred_direction, weight_scale=0.5):
        population = [MobilityModel.NW, MobilityModel.SW, MobilityModel.NE, MobilityModel.SE]
        if preferred_direction == MobilityModel.W:
            weights = [0.25 * 1 + weight_scale, 0.25 * 1 + weight_scale, 0.25, 0.25]
        else:
            weights = [0.25, 0.25, 0.25 * 1 + weight_scale, 0.25 * 1 + weight_scale]
        return random.choices(population, weights, k=1)[0]

    def set_flock_member_type(self, flock_member_type):
        self._flock_member_type = flock_member_type

    def get_flock_member_type(self):
        return self._flock_member_type
