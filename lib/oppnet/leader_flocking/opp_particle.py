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

        self.signal_velocity = 2

        self.t_wait = t_wait
        self.instruct_round = None
        self.__instruction__number = 1
        self.current_direction = None
        self.proposed_direction = None

        self.current_instruct_message = None

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

    def set_flock_member_type(self, flock_member_type):
        self.__flock_member_type__ = flock_member_type

    def get_all_received_messages(self):
        received = []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        return received

    def get_flock_member_type(self):
        return self.__flock_member_type__

    def get_current_instruct(self):
        return self.current_instruct_message

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
            content = LeaderMessageContent(self, proposed_direction, neighbours, self.t_wait - hop,
                                           LeaderMessageType.instruct, self.__instruction__number)
            broadcast_message(self, receivers, content)
        self.instruct_round = self.t_wait + self.world.get_actual_round()
        self.__instruction__number += 1

    def broadcast_received_content(self, received):
        received_content = received.get_content()
        if isinstance(received_content, LeaderMessageContent):
            max_hops = self.routing_parameters.scan_radius
            neighbours = self.scan_for_particles_in(hop=max_hops)

            for hop in range(1, max_hops + 1):
                exclude = set(received_content.get_receivers()).union({received.get_sender()})
                receivers = set(self.scan_for_particles_in(hop=hop)).difference(exclude)
                content = received_content.create_forward_copy(neighbours, hop)
                broadcast_message(self, receivers, content)

    def process_received_messages(self):
        received_messages = self.get_all_received_messages()
        if received_messages:
            highest_number_message = self.__find_highest_number_message__(received_messages)
            self.__update__instruct_round__(highest_number_message)

    def __find_highest_number_message__(self, received_messages):
        highest_number_message = None
        highest_number = -1
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                if content.get_number() > highest_number:
                    highest_number = content.get_number()
                    highest_number_message = message
            else:
                print("opp_particle -> Particle {} received none LeaderMessageContent".format(self.number))
        return highest_number_message

    def __update__instruct_round__(self, highest_number_message):
        highest_number = highest_number_message.get_content().get_number()
        if self.current_instruct_message:
            current_number = self.current_instruct_message.get_content().get_number()
        else:
            current_number = 0
        if highest_number > current_number:
            self.instruct_round = self.world.get_actual_round() + highest_number_message.get_content().get_t_wait()
            self.proposed_direction = highest_number_message.get_content().get_proposed_direction()
            self.current_instruct_message = highest_number_message

    def next_moving_direction(self):
        try:
            if self.world.get_actual_round() >= self.instruct_round:
                self.current_direction = self.proposed_direction
        except TypeError:
            pass
        return self.current_direction
