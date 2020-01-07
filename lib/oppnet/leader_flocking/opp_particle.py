import math
import random
from enum import Enum

from lib.oppnet.communication import broadcast_message
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel
from lib.particle import Particle
from solution.oppnet_flocking.leader_flocking.message_types.leader_message import LeaderMessageContent, \
    LeaderMessageType


class FlockMemberType(Enum):
    leader = 0
    follower = 1


class Particle(Particle):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 t_wait=None):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator)

        self.mobility_model = None
        self.routing_parameters = None

        if not ms_size:
            ms_size = world.particle_ms_size
        if not ms_strategy:
            ms_strategy = world.particle_ms_strategy

        if not mm_mode:
            mm_mode = world.particle_mm_mode
        if not mm_length:
            mm_length = world.particle_mm_length
        if not mm_zone:
            mm_zone = world.particle_mm_zone
        if not mm_starting_dir:
            mm_starting_dir = world.particle_mm_starting_dir

        self.__init_message_stores__(ms_size, ms_strategy)
        self.__init_mobility_model__(mm_mode, mm_length, mm_zone, mm_starting_dir)

        self.routing_parameters = world.routing_parameters

        self.signal_velocity = 1

        self.t_wait = t_wait
        self.chosen_direction = None
        self.proposed_direction = None

        self.__flock_member_type__ = FlockMemberType.follower

    def __init_message_stores__(self, ms_size, ms_strategy):
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

    def __init_mobility_model__(self, mm_mode, length, zone, starting_dir):
        m_model = MobilityModel(self.coordinates[0], self.coordinates[1], mm_mode, length, zone, starting_dir)
        self.mobility_model = m_model

    def set_mobility_model(self, mobility_model):
        self.mobility_model = mobility_model

    def set_routing_parameters(self, routing_parameters):
        self.routing_parameters = routing_parameters

    def set_t_wait(self, t_wait):
        self.t_wait = t_wait
        self.__update_directions__()

    def set_flock_member_type(self, flock_member_type):
        self.__flock_member_type__ = flock_member_type

    def set_chosen_direction(self, chosen_direction):
        self.chosen_direction = chosen_direction

    def get_all_received_messages(self):
        received = []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        return received

    def get_flock_member_type(self):
        return self.__flock_member_type__

    def __update_directions__(self):
        if self.t_wait == 0 and self.__flock_member_type__ == FlockMemberType.leader:
            self.chosen_direction = self.proposed_direction
            self.proposed_direction = None

    def decrement_t_wait(self):
        if self.t_wait:
            self.t_wait -= 1
            self.__update_directions__()

    def choose_direction(self):
        dirs = self.world.grid.get_directions_dictionary()
        self.proposed_direction = random.choice(list(dirs.values()))
        return self.proposed_direction

    def broadcast_direction_proposal(self, proposed_direction=None):
        if not proposed_direction:
            proposed_direction = self.choose_direction()

        max_hops = self.routing_parameters.scan_radius
        neighbours = self.scan_for_particles_in(hop=max_hops)

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)
            content = LeaderMessageContent(self, proposed_direction, receivers, self.t_wait - hop,
                                           LeaderMessageType.instruct)
            broadcast_message(self, neighbours, content)

    def broadcast_received_content(self, received):
        received_content = received.get_content()
        if isinstance(received_content, LeaderMessageContent):
            max_hops = self.routing_parameters.scan_radius
            neighbours = self.scan_for_particles_in(hop=max_hops)

            for hop in range(1, max_hops + 1):
                receivers = set(self.scan_for_particles_in(hop=hop)).difference({received.get_sender()})
                content = received_content.create_forward_copy(neighbours, hop)
                broadcast_message(self, receivers, content)

    def forward_received_messages(self, received_messages):
        for received_message in received_messages:
            self.broadcast_received_content(received_message)

    def next_instruct_from_messages(self, received_messages):
        if self.t_wait:
            min_t_wait = self.t_wait
        else:
            min_t_wait = math.inf

        next_direction = self.chosen_direction
        next_instruct_message = None

        for received_message in received_messages:
            next_instruct_message = self.__update_min_t_wait__(received_message, min_t_wait, next_direction)

        return next_instruct_message

    def __update_min_t_wait__(self, message, min_t_wait, next_direction):
        content = message.get_content()
        next_instruct_message = None
        if isinstance(content, LeaderMessageContent):
            if content.get_t_wait() < min_t_wait:
                self.set_t_wait(content.get_t_wait())
                self.set_chosen_direction(content.get_proposed_direction())
                next_instruct_message = message
        else:
            print("Particle {} received a message without LeaderMessageContent.".format(self.get_id()))
        return next_instruct_message

    def next_moving_direction(self):
        if self.t_wait == 0:
            return self.chosen_direction
        elif self.get_flock_member_type() == FlockMemberType.leader:
            if self.proposed_direction:
                return self.chosen_direction
        else:
            return None
