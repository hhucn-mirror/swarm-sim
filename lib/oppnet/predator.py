import logging
import random
from enum import Enum

from lib.oppnet.communication import broadcast_message, Message
from lib.oppnet.message_types.predator_signal import PredatorSignal
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.particle import Particle
from lib.swarm_sim_header import scan_within_per_hop, get_coordinates_in_direction


class ChaseMode(Enum):
    FocusFlock = 1
    FocusParticle = 2


class Predator(Particle):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, mm_mode=None):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator)
        self.scan_radius = self.world.config_data.predator_scan_radius
        self.chase_mode = self.world.config_data.predator_chase_mode
        self.max_chase = None
        if not mm_mode:
            mm_mode = MobilityModelMode.POI
        self.mobility_model = MobilityModel(self.coordinates, mm_mode)
        self.signal_velocity = world.config_data.signal_velocity
        self.__init_message_stores__(world.config_data.message_store_size, world.config_data.message_store_strategy)

    def move_to(self, direction):
        """
        Moves the predator to the given direction

        :param direction: The direction is defined by loaded grid class
        :return: True: Success Moving;  False: Non moving
        """
        direction_coord = get_coordinates_in_direction(self.coordinates, direction)
        direction, direction_coord = self.check_within_border(direction, direction_coord)
        if self.world.grid.are_valid_coordinates(direction_coord) \
                and direction_coord not in self.world.predator_map_coordinates:
            if self.coordinates in self.world.predator_map_coordinates:
                del self.world.predator_map_coordinates[self.coordinates]
            self.coordinates = direction_coord
            self.world.predator_map_coordinates[self.coordinates] = self
            if self.world.vis:
                self.world.vis.predator_changed(self)
            logging.info("predator %s successfully moved to %s", str(self.get_id()), direction)
            return True

        return False

    def set_color(self, color):
        return

    def __init_message_stores__(self, ms_size, ms_strategy):
        """
        Initialises the particles two MessageStores for forwarding and receiving.
        :param ms_size: the size of the two stores
        :param ms_strategy: the strategy to implement for buffer-management.
        :return: nothing
        """
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

    def chase(self):
        """
        Moves the predator depending on chase_mode.
        :return: the result of move_to()
        """
        self.catch_particles()
        # if the chase is paused, simply move by mobility model
        if self.mobility_model.mode != MobilityModelMode.POI:
            self.move_to(self.mobility_model.next_direction(self.coordinates))
            return None
        if not self.max_chase:
            self.max_chase = self.world.get_actual_round() + self.world.config_data.predator_chase_rounds
        # else execute the chase mode by scanning for nearby particles/flocks
        if self.chase_mode == ChaseMode.FocusParticle:
            next_direction = self.chase_nearest_particle()
        else:
            next_direction = self.chase_nearby_flock()

        if next_direction is not None:
            return self.move_to(next_direction)
        # if maximum number of rounds for a chase is reached, use random_walk mobility model
        elif self.world.get_actual_round() > self.max_chase:
            self.deactivate_chase()
            return None
        else:
            return self.move_to(MobilityModel.random_direction())

    def catch_particles(self):
        one_hop_particles = self.scan_for_particles_within(1)
        for particle in one_hop_particles:
            self.world.remove_particle(particle.get_id())
        self.world.csv_round.update_metrics(particles_caught=len(one_hop_particles))

    def activate_chase(self):
        """
        Resets the max_chase field to the maximum number of rounds to chase + the current simulator round.
        """
        self.max_chase = self.world.config_data.predator_chase_rounds + self.world.get_actual_round()
        self.mobility_model.set_mode(MobilityModelMode.POI)

    def deactivate_chase(self):
        self.mobility_model.set_mode(MobilityModelMode.Random_Walk)
        self.move_to(self.mobility_model.next_direction(self.coordinates))

    def chase_nearest_particle(self):
        """
        Returns the nearest particle within the predator's scan_radius or None if no particle is close enough.
        :return: nearest particle or None
        :rtype: Particle
        """
        nearest_particles = scan_within_per_hop(self.world.particle_map_coordinates, self.coordinates,
                                                self.scan_radius, self.world.grid)
        if nearest_particles:
            if len(nearest_particles[0]) > 0:
                self.mobility_model.poi = random.choice(nearest_particles[0]).coordinates
            else:
                self.mobility_model.poi = nearest_particles[0][0].coordinates
            return self.mobility_model.next_direction(self.coordinates)
        else:
            return None

    def chase_nearby_flock(self):
        """
        Tries to find a nearby flock within the scan_radius of the predator and move towards its center.
        :return: the next direction to move to
        """
        try:
            self.mobility_model.poi = self.world.get_nearby_flock_center_by_coordinates(self.coordinates,
                                                                                        self.scan_radius)
            return self.mobility_model.next_direction(self.coordinates)
        except IndexError:
            return None
        except ValueError:
            return None

    def broadcast_warning(self):
        """
        Broadcasts a message which warns particles about the predator.
        :return: nothing
        """
        message = Message(self, None, content=PredatorSignal(),
                          ttl=self.world.config_data.predator_chase_rounds)
        broadcast_message(self, message)
