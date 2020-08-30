import math
import random
from enum import Enum

from lib.oppnet.communication import broadcast_message, Message
from lib.oppnet.message_types.predator_signal import PredatorSignal
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.particles import FlockMemberType
from lib.particle import Particle
from lib.swarm_sim_header import scan_within_per_hop, get_coordinates_in_direction


class PursuitMode(Enum):
    """
    Enum to distinguish predator pursuit modes.
    """
    FocusFlock = 1
    FocusParticle = 2


class Predator(Particle):
    """
    Predator class that preys on flocks.
    """

    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, mm_mode=None):
        """
        Constructor. Initializes variables.
        :param world: simulator world reference
        :param coordinates: particle coordinates
        :param color: particle color
        :param particle_counter: particle number
        :param csv_generator: csv generator object
        :param mm_mode: MobilityModelMode
        """
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator)
        self.interaction_radius = self.world.config_data.predator_interaction_radius
        self.pursuit_mode = self.world.config_data.predator_pursuit_mode
        if not mm_mode:
            mm_mode = MobilityModelMode.POI
        self.mobility_model = MobilityModel(self.coordinates, mm_mode)
        self.signal_velocity = world.config_data.signal_velocity
        self.signal_range = world.config_data.signal_range
        self.__init_message_stores__(world.config_data.message_store_size, world.config_data.message_store_strategy)
        self._pursuit_rounds = self.world.config_data.predator_pursuit_rounds
        self.max_pursuit = self._pursuit_rounds
        self._pause_rounds = int(self._pursuit_rounds / 2)
        self._deactivated_rounds = math.inf

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
            if direction_coord in self.world.particle_map_coordinates:
                self.catch_particle(self.world.particle_map_coordinates[direction_coord])
            self.coordinates = direction_coord
            self.world.predator_map_coordinates[self.coordinates] = self
            if self.world.vis:
                self.world.vis.predator_changed(self)
            # logging.info("round {} predator {} successfully moved to {}"
            #            .format(self.world.get_actual_round(), self.number, direction))
            return True

        return False

    @NotImplemented
    def set_color(self, color):
        return

    def __init_message_stores__(self, ms_size, ms_strategy):
        """
        Initialises the particles two MessageStores for forwarding and receiving.
        :param ms_size: the size of the two stores
        :param ms_strategy: the strategy to implement for buffer-management.
        :return: None
        """
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

    def pursuit(self):
        """
        Moves the predator depending on pursuit_mode.
        :return: the result of move_to()
        """
        # if the pursuit is paused, simply move by mobility model
        if self.world.get_actual_round() == self.max_pursuit:
            return self.deactivate_pursuit()
        elif self._deactivated_rounds == self._pause_rounds:
            self.activate_pursuit()
        elif self._deactivated_rounds < self._pause_rounds:
            self._deactivated_rounds += 1
            return

        # else execute the pursuit mode by scanning for nearby particles/flocks
        if self.pursuit_mode == PursuitMode.FocusParticle:
            next_direction = self.pursuit_nearest_particle()
        else:
            next_direction = self.pursuit_nearby_flock()

        if next_direction:
            return self.move_to(next_direction)
        else:
            return self.move_to(MobilityModel.random_direction())

    def catch_particle(self, caught_particle):
        """
        Removes the caught particle from the world. Sets a new particle as leader if the removed particle was a leader.
        :param caught_particle: particle caught by the predator
        :return: None
        """
        self.world.remove_particle(caught_particle.get_id())
        if caught_particle.get_flock_member_type() == FlockMemberType.Leader:
            remaining_particles = self.world.get_particle_list()
            particle = random.choice(remaining_particles)
            particle.set_flock_member_type(FlockMemberType.Leader)
            self.world.add_leaders([particle])
        self.world.csv_round.update_metrics(particles_caught=1)

    def activate_pursuit(self):
        """
        Resets the max_pursuit field to the maximum number of rounds to pursuit + the current simulator round.
        """
        self.max_pursuit = self._pursuit_rounds + self.world.get_actual_round()
        self.mobility_model.set_mode(MobilityModelMode.POI)
        self._deactivated_rounds = math.inf

    def deactivate_pursuit(self):
        self._deactivated_rounds = 1
        self.mobility_model.set_mode(MobilityModelMode.Static)

    def pursuit_nearest_particle(self):
        """
        Returns the nearest particle within the predator's interaction_radius or None if no particle is close enough.
        :return: nearest particle or None
        :rtype: Particle
        """
        nearest_particles = scan_within_per_hop(self.world.particle_map_coordinates, self.coordinates,
                                                self.interaction_radius, self.world.grid)
        if nearest_particles:
            if len(nearest_particles[0]) > 0:
                self.mobility_model.poi = random.choice(nearest_particles[0]).coordinates
            else:
                self.mobility_model.poi = nearest_particles[0][0].coordinates
            return self.mobility_model.next_direction(self.coordinates)
        else:
            return self.mobility_model.random_direction()

    def pursuit_nearby_flock(self):
        """
        Tries to find a nearby flock within the interaction_radius of the predator and move towards its center.
        :return: the next direction to move to
        """
        try:
            self.mobility_model.poi = self.world.get_nearby_flock_center_by_coordinates(self.coordinates,
                                                                                        self.interaction_radius)
            return self.mobility_model.next_direction(self.coordinates)
        except IndexError:
            return None
        except ValueError:
            return None

    def broadcast_warning(self):
        """
        Broadcasts a message which warns particles about the predator.
        :return: None
        """
        message = Message(self, None, content=PredatorSignal({self.get_id(): self.coordinates}),
                          ttl=self.world.config_data.predator_pursuit_rounds)
        broadcast_message(self, message)
