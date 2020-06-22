import logging

import lib.particle
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel
from ._helper_classes import *
from ..point import Point


class Particle(lib.particle.Particle):
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

    def move_to(self, direction):
        super().move_to(direction)
        self.mobility_model.update_history(self.coordinates)
