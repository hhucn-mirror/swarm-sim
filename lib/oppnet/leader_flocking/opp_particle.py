import random
from enum import Enum

from lib.oppnet.communication import broadcast_message, send_message, Message
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel
from lib.oppnet.routing import RoutingMap
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
            mm_starting_dir = world.config_data.mobility_model_starting_dir

        self.__init_message_stores__(ms_size, ms_strategy)
        self.mobility_model = MobilityModel(self.coordinates[0], self.coordinates[1], mm_mode, mm_length, mm_zone,
                                            mm_starting_dir)

        self.routing_parameters = world.config_data.routing_parameters

        self.signal_velocity = world.config_data.signal_velocity

        self.t_wait = t_wait
        self.instruct_round = None
        self.__instruction__number = 1
        self.current_direction = None
        self.proposed_direction = None

        self.current_instruct_message = None

        self.__flock_member_type__ = FlockMemberType.follower
        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

        self.next_direction_proposal_round = None

    def __init_message_stores__(self, ms_size, ms_strategy):
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

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

    def add_route(self, contact: Particle, target: Particle, hops, is_leader=False):
        if is_leader:
            self.leader_contacts.add_contact(contact.get_id(), target.get_id(), hops)
        else:
            self.follower_contacts.add_contact(contact.get_id(), target.get_id(), hops)

    def delete_route(self, contact, target, is_leader=False):
        if is_leader:
            self.leader_contacts.remove_contact(contact)
        else:
            self.follower_contacts.remove_contact(contact)

    def choose_direction(self):
        dirs = self.world.grid.get_directions_dictionary()
        self.proposed_direction = random.choice(list(dirs.values()))
        return self.proposed_direction

    def broadcast_direction_instruct(self, proposed_direction=None):
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

    def sent_direction_proposal_to_leaders(self, proposed_direction=None):
        if not proposed_direction:
            proposed_direction = self.choose_direction()
        if not self.leader_contacts:
            receivers = self.scan_for_particles_in(self.routing_parameters.scan_radius)
        else:
            receivers = self.leader_contacts.keys()
        for leader_id, contacts in self.leader_contacts.items():
            # if no contacts are available, sent to all neighbours
            if not contacts:
                contacts = receivers
            self.__sent__direction_proposal_to_contacts__(leader_id, contacts, proposed_direction)
        self.__instruction__number += 1

    def __sent__direction_proposal_to_contacts__(self, leader_id, contacts, proposed_direction):
        try:
            leader = self.world.get_particle_map_id()[leader_id]
            for contact in contacts:
                t_wait = self.t_wait - self.follower_contacts.get_contact(leader.get_id(), contact.get_id()).get_hops()
                content = LeaderMessageContent(self, proposed_direction, contacts, t_wait, LeaderMessageType.instruct,
                                               self.__instruction__number)
                send_message(self, contact, Message(self, leader, content=content))
        except KeyError:
            print("opp_particle -> particle with id {} no longer exists in the world.".format(leader_id))

    def process_received_messages(self):
        received_messages = self.get_all_received_messages()
        if self.get_flock_member_type() == FlockMemberType.follower:
            self.__process_as_follower__(received_messages)
        elif self.get_flock_member_type() == FlockMemberType.leader:
            self.__process_as_leader__(received_messages)

    def __process_as_leader__(self, received_messages):
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_leader__(message)
                elif message_type == LeaderMessageType.commit:
                    self.__process_commit_as_leader__(message)
                elif message_type == LeaderMessageType.discover:
                    self.__process_discover_as_leader__(message)
                elif message_type == LeaderMessageType.discover_ack:
                    self.__process_discover_ack_as_leader__(message)
                elif message_type == LeaderMessageType.propose:
                    self.__process_propose_as_leader__(message)

    def __process_instruct_as_leader__(self, message):
        content = message.get_content()
        sending_leader = content.get_leader()
        if sending_leader not in self.leader_contacts:
            self.add_route(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)
            self.__sent_discover__(sending_leader)
            self.next_direction_proposal_round = None
        else:
            # TODO:
            self.__process_instructs_as_follower__(message)

    def __sent_discover__(self, receiving_leader):
        receivers = self.scan_for_particles_in(self.routing_parameters.scan_radius)
        message_content = LeaderMessageContent(self, None, receivers, None, LeaderMessageType.discover, None)
        broadcast_message(self, receivers, message_content)

    def __process_commit_as_leader__(self, message):
        raise NotImplementedError

    def __process_discover_as_leader__(self, message):
        raise NotImplementedError

    def __process_discover_ack_as_leader__(self, message):
        raise NotImplementedError

    def __process_propose_as_leader__(self, message):
        raise NotImplementedError

    def __process_as_follower__(self, received_messages):
        remaining = self.__process_instructs_as_follower__(received_messages)
        for message in remaining:
            content = message.get_content()
            message_type = content.get_message_type()
            if message_type == LeaderMessageType.commit:
                self.__process_commit_as_follower__(message)
            elif message_type == LeaderMessageType.discover:
                self.__process_discover_as_follower__(message)
            elif message_type == LeaderMessageType.discover_ack:
                self.__process_discover_ack_as_follower__(message)
            elif message_type == LeaderMessageType.propose:
                self.__process_propose_as_follower__(message)

    def __process_instructs_as_follower__(self, received_messages):
        remaining = []
        received_new_instruct = False
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                if message_type == LeaderMessageType.instruct:
                    if received_new_instruct is False:
                        received_new_instruct = self.__update__instruct_round__(message)
                else:
                    remaining.append(message)
        if received_new_instruct:
            self.broadcast_received_content(self.current_instruct_message)
        return remaining

    def __process_commit_as_follower__(self, message):
        raise NotImplementedError

    def __process_discover_as_follower__(self, message):
        raise NotImplementedError

    def __process_discover_ack_as_follower__(self, message):
        raise NotImplementedError

    def __process_propose_as_follower__(self, message):
        raise NotImplementedError

    def __update__instruct_round__(self, received_message):
        highest_number = received_message.get_content().get_number()
        if self.current_instruct_message:
            current_number = self.current_instruct_message.get_content().get_number()
        else:
            current_number = 0
        if highest_number > current_number:
            self.instruct_round = self.world.get_actual_round() + received_message.get_content().get_t_wait()
            self.proposed_direction = received_message.get_content().get_proposed_direction()
            self.current_instruct_message = received_message
            return True
        else:
            return False

    def next_moving_direction(self):
        try:
            if self.world.get_actual_round() >= self.instruct_round:
                self.current_direction = self.proposed_direction
        except TypeError:
            pass
        return self.current_direction
