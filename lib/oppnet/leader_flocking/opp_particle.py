import random
from enum import Enum

from lib.oppnet.communication import broadcast_message, send_message, Message
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel
from lib.oppnet.routing import RoutingMap, RoutingContact
from lib.particle import Particle
from solution.oppnet_flocking.leader_flocking.message_types.leader_message import LeaderMessageContent, \
    LeaderMessageType


class FlockMemberType(Enum):
    leader = 0
    follower = 1


class LeaderStateName(Enum):
    WaitingForCommits = 0,
    WaitingForDiscoverAck = 1,
    CommitedToPropose = 2,
    CommittedToInstruct = 3,
    PerformingInstruct = 4,
    SendInstruct = 5


class LeaderState:

    def __init__(self, leader_state_name: LeaderStateName, waiting_ids: set, start_round, expected_rounds=0):
        self.leader_state_name = leader_state_name
        self.waiting_ids = waiting_ids
        self.start_round = start_round
        self.end_round = start_round + expected_rounds

    def get_leader_state_name(self):
        return self.leader_state_name

    def add_to_waiting(self, id_to_add):
        self.waiting_ids.add(id_to_add)

    def remove_from_waiting(self, id_to_remove):
        self.waiting_ids.remove(id_to_remove)

    def get_waiting_ids(self):
        return self.waiting_ids

    def is_completed(self):
        if self.leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck,
                                      LeaderStateName.CommittedToInstruct, LeaderStateName.CommitedToPropose]:
            return len(self.waiting_ids) == 0
        else:
            return True

    def is_timed_out(self, current_round):
        if not self.leader_state_name == LeaderStateName.PerformingInstruct:
            return self.end_round <= current_round
        else:
            return False


class Particle(Particle):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 t_wait=0):
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
        self.__instruction_number__ = None
        self.current_direction = None
        self.proposed_direction = None

        self.current_instruct_message = None

        self.__flock_member_type__ = FlockMemberType.follower
        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

        self.next_direction_proposal_round = None
        self.__next_proposal_seed__ = 0
        self.__leader_states__ = dict()

    def __init_message_stores__(self, ms_size, ms_strategy):
        self.send_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)
        self.rcv_store = MessageStore(maxlen=ms_size, strategy=ms_strategy)

    def set_mobility_model(self, mobility_model):
        self.mobility_model = mobility_model

    def set_routing_parameters(self, routing_parameters):
        self.routing_parameters = routing_parameters

    def set_t_wait(self, t_wait):
        self.t_wait = t_wait

    def set_next_direction_proposal_round(self, next_round):
        self.next_direction_proposal_round = next_round
        self.__next_proposal_seed__ = next_round
        random.seed(next_round)

    def reset_random_next_direction_proposal_round(self):
        self.__next_proposal_seed__ += random.randint(1, self.t_wait * 10)
        self.next_direction_proposal_round = self.__next_proposal_seed__ + self.world.get_actual_round()

    def set_flock_member_type(self, flock_member_type):
        self.__flock_member_type__ = flock_member_type

    def get_all_received_messages(self):
        received = []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        while len(self.send_store) > 0:
            received.append(self.send_store.pop())
        return received

    def get_all_to_forward(self):
        to_forward = []
        while len(self.send_store) > 0:
            to_forward.append(self.send_store.pop())
        return to_forward

    def get_flock_member_type(self):
        return self.__flock_member_type__

    def get_current_instruct(self):
        return self.current_instruct_message

    def add_route(self, contact: Particle, target: Particle, hops, is_leader=False):
        if is_leader:
            self.leader_contacts.add_contact(contact, target, hops)
        else:
            self.follower_contacts.add_contact(contact, target, hops)

    def delete_route(self, contact: RoutingContact, is_leader=False):
        if is_leader:
            self.leader_contacts.remove_contact(contact)
        else:
            self.follower_contacts.remove_contact(contact)

    def delete_target_routes(self, target_id, is_leader=False):
        try:
            target_particle = self.world.get_particle_map_id()[target_id]
            if is_leader:
                self.leader_contacts.remove_target(target_particle)
            else:
                self.follower_contacts.remove_target(target_particle)
        except KeyError:
            print("round {}: opp_particle -> delete_target_routes() tried deleting non-existent target_id.".format(
                self.world.get_actual_round()
            ))

    def choose_direction(self):
        dirs = self.world.grid.get_directions_dictionary()
        self.proposed_direction = random.choice(list(dirs.values()))
        return self.proposed_direction

    def __add_leader_state__(self, state_name: LeaderStateName, waiting_ids: set, start_round, expected_rounds):
        if state_name not in self.__leader_states__ or self.__leader_states__[state_name] is None:
            self.__leader_states__[state_name] = LeaderState(state_name, waiting_ids, start_round, expected_rounds)
        elif state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck]:
            for waiting_id in waiting_ids:
                self.__leader_states__[state_name].add_to_waiting(waiting_id)
        else:
            print("round {}: opp_particle -> __add_leader_state__() Tried adding LeaderState {} which is already set!"
                  .format(start_round, state_name.name))

    def __remove_id_from_states__(self, waiting_id, state_name):
        if state_name in self.__leader_states__:
            try:
                self.__leader_states__[state_name].remove_from_waiting(waiting_id)
            except KeyError:
                del self.__leader_states__[state_name]

    def __is__waiting_for_commit__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForCommits)

    def __is_committed_to_instruct__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommittedToInstruct)

    def __is_committed_to_propose__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommitedToPropose)

    def __is__waiting_for_discover_ack__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForDiscoverAck)

    def __is_in_leader_states__(self, state_name: LeaderStateName):
        if state_name in self.__leader_states__:
            leader_state = self.__leader_states__[state_name]
            return not leader_state.is_completed()
        else:
            return False

    def broadcast_direction_instruct(self, proposed_direction=None):
        if not proposed_direction:
            proposed_direction = self.choose_direction()

        max_hops = self.routing_parameters.scan_radius
        neighbours = self.scan_for_particles_in(hop=max_hops)

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)
            content = LeaderMessageContent(self, proposed_direction, neighbours, self.t_wait - hop,
                                           LeaderMessageType.instruct, self.__instruction_number__)
            broadcast_message(self, receivers, content)
        self.instruct_round = self.t_wait + self.world.get_actual_round()

    def broadcast_leader_message(self, message_type: LeaderMessageType, neighbours=None, proposed_direction=None):
        max_hops = self.routing_parameters.scan_radius
        if not neighbours:
            neighbours = self.scan_for_particles_in(hop=max_hops)

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)
            content = LeaderMessageContent(self, proposed_direction, neighbours, self.t_wait - hop,
                                           message_type, self.__instruction_number__)
            broadcast_message(self, receivers, content)

    def send_direction_proposal(self, proposed_direction=None):
        if not proposed_direction:
            proposed_direction = self.choose_direction()
        max_hops = self.routing_parameters.scan_radius
        neighbours = set(self.scan_for_particles_in(hop=max_hops))
        receiving_leaders = self.leader_contacts.keys()
        self.__send_proposal_to_leaders__(proposed_direction)
        if len(receiving_leaders) == 0:
            self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(),
                                      self.world.get_actual_round(), self.t_wait * 2)
            self.broadcast_leader_message(LeaderMessageType.propose, neighbours)
        print("round {}: opp_particle -> particle {} send direction proposal # {}".format(self.world.get_actual_round(),
                                                                                          self.number,
                                                                                          self.__instruction_number__))
        self.instruct_round = 0

    def __send_proposal_to_leaders__(self, proposed_direction):
        for leader, contacts in self.leader_contacts.items():
            for contact_particle, contact in contacts.items():
                self.__add_leader_state__(LeaderStateName.WaitingForCommits, {leader.get_id()},
                                          self.world.get_actual_round(), self.t_wait * 2)
                message = Message(self, leader, content=LeaderMessageContent(self, proposed_direction,
                                                                             self.leader_contacts.keys(),
                                                                             self.t_wait - contact.get_hops(),
                                                                             LeaderMessageType.propose,
                                                                             self.world.get_actual_round()))
                send_message(self, contact_particle, message)
        self.__instruction_number__ = self.world.get_actual_round()

    def broadcast_received_content(self, received_message):
        received_content = received_message.get_content()
        max_hops = self.routing_parameters.scan_radius
        neighbours = self.scan_for_particles_in(hop=max_hops)
        exclude = set(received_content.get_receivers()).union({received_message.get_sender(),
                                                               received_message.get_content().get_sending_leader(),
                                                               received_message.get_original_sender()})
        all_receivers = set(neighbours).difference(exclude)
        for hop in range(1, max_hops + 1):
            receivers = set(self.scan_for_particles_in(hop=hop)).difference(exclude)
            content = received_content.create_forward_copy(all_receivers, hop)
            received_message.set_content(content)
            for receiver in receivers:
                send_message(self, receiver, received_message)

    def forward_to_leader_via_contacts(self, received_message, receiving_leader=None):
        received_content = received_message.get_content()
        if not receiving_leader:
            receiving_leader = received_message.get_actual_receiver()
        if receiving_leader not in self.leader_contacts:
            self.broadcast_received_content(received_message)
        else:
            contacts = set(self.leader_contacts[receiving_leader].keys())
            contacts = contacts.difference(
                {
                    received_content.get_sending_leader(),
                    received_message.get_sender(),
                    received_message.get_original_sender()
                })
            for contact in contacts:
                hops = self.__get_t_wait_value_for_leader_contact(receiving_leader, contact)
                content = received_content.create_forward_copy(contacts, hops)
                received_message.set_content(content)
                received_message.set_actual_receiver(receiving_leader)
                send_message(self, contact, received_message)

    def __send_content_to_leader_via_contacts__(self, sending_leader: Particle, receiving_leader: Particle,
                                                message_type: LeaderMessageType,
                                                contacts=None, proposed_direction=None):
        if not contacts:
            if receiving_leader in self.leader_contacts:
                contacts = self.leader_contacts[receiving_leader]
            else:
                print("round {}: opp_particle -> __send_content_to_leader_via_contacts__() "
                      .format(self.world.get_actual_round()) + "tried to send to unknown leader.")
        for _, contact in contacts.items():
            t_wait = self.__get_t_wait_value_for_leader_contact(receiving_leader, contact)
            content = LeaderMessageContent(sending_leader, proposed_direction, contacts.values(), t_wait, message_type,
                                           self.world.get_actual_round())
            send_message(self, contact.get_contact_particle(), Message(self, receiving_leader, content=content))

    def __get_t_wait_value_for_leader_contact(self, leader: Particle, contact):
        if isinstance(contact, RoutingContact):
            contact = contact.get_contact_particle()
        try:
            t_wait = self.t_wait - self.leader_contacts.get_contact(leader, contact).get_hops()
        except KeyError:
            t_wait = self.t_wait
        return t_wait

    def update_leader_states(self):
        keys_to_delete = []
        for leader_state_name, leader_state in self.__leader_states__.items():
            if leader_state.is_timed_out(self.world.get_actual_round()):
                keys_to_delete.append(leader_state_name)
        for leader_state_name in keys_to_delete:
            if leader_state_name == LeaderStateName.WaitingForCommits:
                self.reset_random_next_direction_proposal_round()
            del self.__leader_states__[leader_state_name]

    def process_received_messages(self):
        all_messages = self.get_all_received_messages()
        if self.get_flock_member_type() == FlockMemberType.follower:
            self.__process_as_follower__(all_messages)
        elif self.get_flock_member_type() == FlockMemberType.leader:
            self.__process_as_leader__(all_messages)

    def __forward_messages__(self):
        for to_forward in list(self.send_store):
            send_message(self, to_forward.get_actual_receiver(), to_forward)

    def __process_as_leader__(self, received_messages: [Message]):
        remaining = self.__process_commit_and_ack__(received_messages)
        for message in remaining:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_leader__(message)
                elif message_type == LeaderMessageType.discover:
                    self.__process_discover_as_leader__(message)
                elif message_type == LeaderMessageType.propose:
                    self.__process_propose_as_leader__(message)

    def __process_commit_and_ack__(self, received_messages: [Message]):
        remaining = []
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                sending_leader = content.get_sending_leader()
                if (sending_leader not in self.leader_contacts) and sending_leader.get_id() != self.get_id():
                    self.__new_leader_found__(message, sending_leader)
                if message_type == LeaderMessageType.commit:
                    self.__process_commit_as_leader__(message)
                elif message_type == LeaderMessageType.discover_ack:
                    self.__process_discover_ack_as_leader__(message)
                elif self.get_id() not in [sending_leader.get_id(), message.get_original_sender()]:
                    remaining.append(message)
        return remaining

    def __new_leader_found__(self, message: Message, sending_leader: Particle):
        self.add_route(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)
        self.__send_content_to_leader_via_contacts__(self, sending_leader, LeaderMessageType.discover)
        self.__add_leader_state__(LeaderStateName.WaitingForDiscoverAck, set(sending_leader.get_id()),
                                  self.world.get_actual_round(), message.get_hops() * 2)

    def __process_instruct_as_leader__(self, message: Message):
        if not self.__is_committed_to_instruct__() and self.__update__instruct_round_as_leader__(message):
            sending_leader = message.get_content().get_sending_leader()
            self.__add_leader_state__(LeaderStateName.CommittedToInstruct, {sending_leader.get_id},
                                      self.world.get_actual_round(), message.get_hops() * 2)
            self.reset_random_next_direction_proposal_round()
            print("round {}: opp_particle -> particle {} committed to instruct # {}".format(
                self.world.get_actual_round(), self.number, self.__instruction_number__))
        else:
            print("round {}: opp_particle -> particle {} ignored instruct # {}".format(
                self.world.get_actual_round(), self.number, self.__instruction_number__))
        self.broadcast_received_content(message)

    def __process_commit_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__remove_id_from_states__(content.get_sending_leader().get_id(), LeaderStateName.WaitingForCommits)
            if not self.__is__waiting_for_commit__() and LeaderStateName.SendInstruct not in self.__leader_states__:
                self.reset_random_next_direction_proposal_round()
                self.broadcast_direction_instruct()
                self.__add_leader_state__(LeaderStateName.SendInstruct, set(), self.world.get_actual_round(),
                                          self.t_wait * 2)
                print("round {}: opp_particle -> particle {} broadcast instruct # {}".format(
                    self.world.get_actual_round(),
                    self.number,
                    self.__instruction_number__))
        else:
            self.__process_commit_as_follower__(message)

    def __process_discover_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__send_content_to_leader_via_contacts__(self, content.get_sending_leader(),
                                                         LeaderMessageType.discover_ack)
        if message.get_hops() < self.t_wait * 2:
            self.__process_discover_as_follower__(message)

    def __process_discover_ack_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__remove_id_from_states__(content.get_sending_leader().get_id(), LeaderStateName.WaitingForDiscoverAck)
        else:
            self.__process_discover_ack_as_follower__(message)

    def __process_propose_as_leader__(self, message: Message):
        content = message.get_content()
        sending_leader = content.get_sending_leader()
        self.__process_propose_as_follower__(message)
        if self.__is__waiting_for_commit__() or self.__is_committed_to_propose__():
            print("round {}: opp_particle -> particle {} ignored propose # {}".format(
                self.world.get_actual_round(), self.number, self.__instruction_number__))
            return
        self.next_direction_proposal_round = None
        self.__add_leader_state__(LeaderStateName.CommitedToPropose, {sending_leader.get_id()},
                                  self.world.get_actual_round(), self.t_wait * 2)
        self.__send_content_to_leader_via_contacts__(self, content.get_sending_leader(), LeaderMessageType.commit)
        self.__instruction_number__ = content.get_number()
        print("round {}: opp_particle -> particle {} committed to proposal # {} from particle {}".format(
            self.world.get_actual_round(),
            self.number,
            content.get_number(),
            sending_leader.number))

    def __process_as_follower__(self, received_messages: [Message]):
        self.__add__new_contacts_as_follower__(received_messages)
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_follower__(message)
                elif message_type == LeaderMessageType.commit:
                    self.__process_commit_as_follower__(message)
                elif message_type == LeaderMessageType.discover:
                    self.__process_discover_as_follower__(message)
                elif message_type == LeaderMessageType.discover_ack:
                    self.__process_discover_ack_as_follower__(message)
                elif message_type == LeaderMessageType.propose:
                    self.__process_propose_as_follower__(message)

    def __add__new_contacts_as_follower__(self, received_messages):
        for message in received_messages:
            sending_leader = message.get_content().get_sending_leader()
            if sending_leader not in self.leader_contacts:
                self.add_route(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)

    def __process_instruct_as_follower__(self, message: Message):
        if self.__update__instruct_round_as_follower_(message):
            self.broadcast_received_content(self.current_instruct_message)

    def __process_commit_as_follower__(self, message: Message):
        self.forward_to_leader_via_contacts(message)

    def __process_discover_as_follower__(self, message: Message):
        self.broadcast_received_content(message)

    def __process_discover_ack_as_follower__(self, message: Message):
        self.forward_to_leader_via_contacts(message)

    def __process_propose_as_follower__(self, message: Message):
        self.forward_to_leader_via_contacts(message)

    def __update__instruct_round_as_leader__(self, received_message: Message):
        new_number = received_message.get_content().get_number()
        if new_number == self.__instruction_number__:
            instruct_round = self.world.get_actual_round() + received_message.get_content().get_t_wait()
            if self.instruct_round is not None and instruct_round <= self.instruct_round:
                return False
            self.instruct_round = instruct_round
            self.proposed_direction = received_message.get_content().get_proposed_direction()
            self.current_instruct_message = received_message
            return True
        else:
            return False

    def __update__instruct_round_as_follower_(self, received_message: Message):
        content = received_message.get_content()
        new_instruction_round = self.world.get_actual_round() + content.get_t_wait()
        instruction_number = content.get_number()
        if self.__instruction_number__ is None or (instruction_number > self.__instruction_number__):
            self.instruct_round = new_instruction_round
            self.proposed_direction = content.get_proposed_direction()
            self.current_instruct_message = received_message
            self.__instruction_number__ = instruction_number
            return True
        else:
            return False

    def next_moving_direction(self):
        try:
            if self.instruct_round != 0 and self.world.get_actual_round() >= self.instruct_round:
                self.current_direction = self.proposed_direction
        except TypeError:
            pass
        return self.current_direction
