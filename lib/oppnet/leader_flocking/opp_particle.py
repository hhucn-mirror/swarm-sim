import collections
import logging
import random

import numpy as np

from lib.oppnet.communication import multicast_message_content, send_message, Message, broadcast_message
from lib.oppnet.leader_flocking.helper_classes import FlockMemberType, LeaderStateName, LeaderState
from lib.oppnet.message_types import LeaderMessageContent, LeaderMessageType
from lib.oppnet.message_types import LostMessageContent, LostMessageType
from lib.oppnet.messagestore import MessageStore
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.point import Point
from lib.oppnet.routing import RoutingMap, RoutingContact
from lib.particle import Particle


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
            if world.config_data.mobility_model_starting_dir == 'random':
                mm_starting_dir = MobilityModel.random_direction()
                logging.debug("round {}: opp_particle -> initialised particle {} with direction {}".format(
                    self.world.get_actual_round(), self.number, mm_starting_dir))
            else:
                mm_starting_dir = world.config_data.mobility_model_starting_dir

        self.__init_message_stores__(ms_size, ms_strategy)
        self.mobility_model = MobilityModel(self.coordinates, mm_mode, mm_length, mm_zone,
                                            mm_starting_dir)

        self.routing_parameters = world.config_data.routing_parameters

        self.signal_velocity = world.config_data.signal_velocity

        self.t_wait = t_wait
        self.instruct_round = None
        self.__instruction_number__ = None
        self.proposed_direction = None

        self.current_instruct_message = None

        self.__flock_member_type__ = FlockMemberType.follower
        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

        self.next_direction_proposal_round = None
        self.__next_proposal_seed__ = 0
        self.__leader_states__ = dict()

        self.commit_quorum = self.world.config_data.commit_quorum

        self.__previous_neighbourhood__ = None

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

    def set_instruction_number(self, instruction_number):
        self.__instruction_number__ = instruction_number

    def reset_random_next_direction_proposal_round(self):
        self.__next_proposal_seed__ += random.randint(1, self.t_wait * 10)
        self.next_direction_proposal_round = self.__next_proposal_seed__ + self.world.get_actual_round()

    def set_flock_member_type(self, flock_member_type):
        self.__flock_member_type__ = flock_member_type

    def init_neighbourhood(self):
        neighbourhood = set(self.scan_for_particles_within(self.routing_parameters.scan_radius))
        self.__previous_neighbourhood__ = neighbourhood

    def get_all_received_messages(self):
        received = []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        while len(self.send_store) > 0:
            received.append(self.send_store.pop())
        return received

    def get_flock_member_type(self):
        return self.__flock_member_type__

    def get_current_instruct(self):
        return self.current_instruct_message

    def __add_route__(self, contact: Particle, target: Particle, hops, is_leader=False):
        if self.number == contact.number or self.number == target.number:
            return
        logging.debug("round {}: opp_particle -> route: {} via {} to {} with {} hops".format(
            self.world.get_actual_round(), self.number, contact.number, target.number, hops))
        if is_leader:
            self.leader_contacts.add_contact(contact, target, hops)
        else:
            self.follower_contacts.add_contact(contact, target, hops)

    def __delete_route__(self, contact: RoutingContact, is_leader=False):
        if is_leader:
            self.leader_contacts.remove_contact(contact)
        else:
            self.follower_contacts.remove_contact(contact)

    def __delete_target_routes__(self, target_id, is_leader=False):
        try:
            target_particle = self.world.get_particle_map_id()[target_id]
            if is_leader:
                self.leader_contacts.remove_target(target_particle)
            else:
                self.follower_contacts.remove_target(target_particle)
        except KeyError:
            logging.debug("round {}: opp_particle -> delete_target_routes() tried deleting non-existent target_id."
                          .format(self.world.get_actual_round()))

    def choose_direction(self):
        dirs = self.world.grid.get_directions_dictionary()
        self.proposed_direction = random.choice(list(dirs.values()))
        return self.proposed_direction

    def __add_leader_state__(self, state_name: LeaderStateName, waiting_particles: set, start_round, expected_rounds):
        if state_name not in self.__leader_states__ or self.__leader_states__[state_name] is None:
            self.__leader_states__[state_name] = LeaderState(state_name, waiting_particles, start_round,
                                                             expected_rounds)
        elif state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck]:
            self.__leader_states__[state_name].add_to_waiting(waiting_particles)
        else:
            logging.debug(
                "round {}: opp_particle -> __add_leader_state__() Tried adding LeaderState {} which is already set!"
                    .format(start_round, state_name.name))

    def __remove_particle_from_states__(self, waiting_particle, state_name):
        if state_name in self.__leader_states__:
            try:
                self.__leader_states__[state_name].remove_from_waiting(waiting_particle)
            except KeyError:
                del self.__leader_states__[state_name]

    def __is__waiting_for_commit__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForCommits)

    def __is_committed_to_instruct__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommittedToInstruct)

    def __is_committed_to_propose__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommittedToPropose)

    def __is__waiting_for_discover_ack__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForDiscoverAck)

    def __is_in_leader_states__(self, state_name: LeaderStateName):
        if state_name in self.__leader_states__:
            leader_state = self.__leader_states__[state_name]
            return not leader_state.is_completed()
        else:
            return False

    def multicast_leader_message(self, message_type: LeaderMessageType, neighbours=None):
        max_hops = self.routing_parameters.scan_radius
        if not neighbours:
            neighbours = self.scan_for_particles_within(hop=max_hops)

        if message_type == LeaderMessageType.instruct:
            self.instruct_round = self.t_wait + self.world.get_actual_round()
            self.__instruction_number__ = self.world.get_actual_round()

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)
            number = self.__instruction_number__ if self.__instruction_number__ is not None \
                else self.world.get_actual_round()
            content = LeaderMessageContent(self, self.proposed_direction, neighbours, self.t_wait - hop,
                                           message_type, number)
            multicast_message_content(self, receivers, content)

    def send_direction_proposal(self, proposed_direction=None):
        if not proposed_direction:
            proposed_direction = self.choose_direction()
        receiving_leaders = self.leader_contacts.keys()
        self.__instruction_number__ = self.world.get_actual_round()
        self.__send_proposal_to_leaders__(proposed_direction)
        if len(receiving_leaders) == 0:
            self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(),
                                      self.world.get_actual_round(), self.t_wait * 2)
            self.multicast_leader_message(LeaderMessageType.propose)

    def __send_proposal_to_leaders__(self, proposed_direction):
        self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(self.leader_contacts.keys()),
                                  self.world.get_actual_round(), self.t_wait * 2)
        for leader, contacts in self.leader_contacts.items():
            for contact_particle, contact in contacts.items():
                content = LeaderMessageContent(self, proposed_direction,
                                               set(self.leader_contacts.keys()),
                                               self.t_wait - contact.get_hops(),
                                               LeaderMessageType.propose,
                                               self.__instruction_number__)
                message = Message(self, leader, content=content)
                message.set_actual_receiver(leader)
                send_message(self, contact_particle, message)
                logging.debug("round {}: opp_particle -> particle {} send direction proposal # {} to {} via {}".format(
                    self.world.get_actual_round(), self.number, self.__instruction_number__, leader.number,
                    contact_particle.number))

    def flood_message_content(self, message_content):
        receivers = self.scan_for_particles_within(hop=self.routing_parameters.scan_radius)
        multicast_message_content(self, receivers, message_content)

    def send_message_content_via_contacts(self, receiver, message_content):
        for contact_particle in self.follower_contacts[receiver].keys():
            send_message(self, contact_particle, Message(self, receiver, content=message_content))

    def __flood_forward__(self, received_message):
        received_content = received_message.get_content()
        instruction_number = received_content.get_number()
        if instruction_number is not None and (self.world.get_actual_round() - instruction_number) > self.t_wait:
            # do not flood if the message is older than t_wait
            return
        max_hops = self.routing_parameters.scan_radius
        neighbours = self.scan_for_particles_within(hop=max_hops)
        exclude = {received_message.get_sender(), received_message.get_content().get_sending_leader(),
                   received_message.get_original_sender()}.union(received_content.get_receivers())
        all_receivers = set(neighbours).difference(exclude)
        for hop in range(1, max_hops + 1):
            receivers = set(self.scan_for_particles_in(hop=hop)).difference(exclude)
            if isinstance(received_content, LeaderMessageContent):
                content = received_content.create_forward_copy(all_receivers, hop)
            else:
                content = received_content
            received_message.set_content(content)
            for receiver in receivers:
                send_message(self, receiver, received_message)
                logging.debug("round {}: opp_particle -> particle {} forwarded {} #{} to {}".format(
                    self.world.get_actual_round(), self.number, content.get_message_type().name,
                    content.get_number(), receiver.number))

    def forward_to_leader_via_contacts(self, received_message, receiving_leader=None):
        received_content = received_message.get_content()
        if receiving_leader and receiving_leader not in self.leader_contacts:
            self.__flood_forward__(received_message)
        else:
            if receiving_leader:
                receivers = {receiving_leader}
            elif isinstance(received_content, LeaderMessageContent):
                receivers = set(received_content.get_receivers())
            else:
                receivers = set(self.leader_contacts.keys())
            receivers.difference_update(
                {
                    received_message.get_sender(),
                    received_message.get_original_sender()
                })
            self.__forward_via_all_contacts__(received_content, received_message, receivers)

    def __forward_via_all_contacts__(self, received_content, received_message, receivers):
        for leader_particle in receivers:
            for contact in self.leader_contacts.get_leader_contacts(leader_particle):
                hops = contact.get_hops()
                if isinstance(received_content, LeaderMessageContent):
                    content = received_content.create_forward_copy(receivers, hops)
                    received_message.set_content(content)
                else:
                    content = received_content
                received_message.set_actual_receiver(leader_particle)
                send_message(self, contact.get_contact_particle(), received_message)
                logging.debug("round {}: opp_particle -> particle {} forwarded {} to {} via {}".format(
                    self.world.get_actual_round(), self.number, content.get_message_type().name,
                    leader_particle.number, contact.get_contact_particle().number))

    def __send_content_to_leader_via_contacts__(self, sending_leader: Particle, receiving_leader: Particle,
                                                message_type: LeaderMessageType,
                                                contacts=None, proposed_direction=None):
        if not contacts:
            if receiving_leader in self.leader_contacts:
                contacts = self.leader_contacts[receiving_leader]
            else:
                logging.debug("round {}: opp_particle -> __send_content_to_leader_via_contacts__() "
                              .format(self.world.get_actual_round()) + "tried to send to unknown leader.")
                return
        if not contacts:
            self.flood_message_content(LeaderMessageContent(sending_leader, proposed_direction,
                                                            {receiving_leader}, self.t_wait, message_type,
                                                            self.__instruction_number__))
            return
        for _, contact in contacts.items():
            t_wait = self.__get_t_wait_value_for_leader_contact(receiving_leader, contact)
            content = LeaderMessageContent(sending_leader, proposed_direction, {receiving_leader}, t_wait, message_type,
                                           self.__instruction_number__)
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
            if leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.CommittedToPropose]:
                self.reset_random_next_direction_proposal_round()
            del self.__leader_states__[leader_state_name]

    def process_received_messages(self):
        all_messages = self.get_all_received_messages()
        if self.get_flock_member_type() == FlockMemberType.follower:
            self.__process_as_follower__(all_messages)
        elif self.get_flock_member_type() == FlockMemberType.leader:
            self.__process_as_leader__(all_messages)

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
            elif isinstance(content, LostMessageContent):
                self.__process_lost_message_as_leader__(message)

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
                if message.get_original_sender() not in self.leader_contacts:
                    self.__add_route__(message.get_sender(), message.get_original_sender(), message.get_hops(),
                                       is_leader=False)
            else:
                self.__add_route__(message.get_sender(), message.get_original_sender(), message.get_hops(),
                                   is_leader=False)
                remaining.append(message)
        return remaining

    def __new_leader_found__(self, message: Message, sending_leader: Particle):
        self.__add_route__(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)
        self.__send_content_to_leader_via_contacts__(self, sending_leader, LeaderMessageType.discover)
        logging.debug(
            "round {}: opp_particle -> particle #{} found a new leader #{} with {} hops."
                .format(self.world.get_actual_round(), self.number, sending_leader.number, message.get_hops()))
        self.__add_leader_state__(LeaderStateName.WaitingForDiscoverAck, {sending_leader},
                                  self.world.get_actual_round(), message.get_hops() * 2)

    def __process_instruct_as_leader__(self, message: Message):
        logging.debug("round {}: opp_particle -> particle {} received instruct # {}".format(
            self.world.get_actual_round(), self.number, message.get_content().get_number()))
        if not self.__is_committed_to_instruct__() and self.__update__instruct_round_as_leader__(message):
            sending_leader = message.get_content().get_sending_leader()
            self.__add_leader_state__(LeaderStateName.CommittedToInstruct, {sending_leader},
                                      self.world.get_actual_round(), message.get_hops() * 2)
            self.reset_random_next_direction_proposal_round()
            self.__flood_forward__(message)
            logging.debug("round {}: opp_particle -> particle {} committed to instruct # {}".format(
                self.world.get_actual_round(), self.number, self.__instruction_number__))

    def __process_commit_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver().number == self.number and self.__instruction_number__ == content.get_number():
            if self.__is_committed_to_propose__():
                return
            logging.debug("round {}: opp_particle -> particle {} received commit #{} from particle {}"
                          .format(self.world.get_actual_round(),
                                  self.number, content.get_number(), content.get_sending_leader().number))
            self.__remove_particle_from_states__(content.get_sending_leader(), LeaderStateName.WaitingForCommits)
            if self.__quorum_fulfilled__() and LeaderStateName.SendInstruct not in self.__leader_states__:
                self.__multicast_instruct__()
        else:
            self.forward_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())

    def __multicast_instruct__(self):
        self.reset_random_next_direction_proposal_round()
        self.multicast_leader_message(LeaderMessageType.instruct)
        self.__add_leader_state__(LeaderStateName.SendInstruct, set(), self.world.get_actual_round(),
                                  self.t_wait * 2)
        logging.debug("round {}: opp_particle -> particle {} broadcast instruct # {}".format(
            self.world.get_actual_round(),
            self.number,
            self.__instruction_number__))

    def __quorum_fulfilled__(self):
        if self.__is__waiting_for_commit__():
            waiting_count = self.__leader_states__[LeaderStateName.WaitingForCommits].waiting_count()
            leader_count = len(self.leader_contacts.keys())
            return (1 - waiting_count / leader_count) > self.commit_quorum
        else:
            return True

    def __process_discover_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__send_content_to_leader_via_contacts__(self, content.get_sending_leader(),
                                                         LeaderMessageType.discover_ack)

    def __process_discover_ack_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__remove_particle_from_states__(content.get_sending_leader(), LeaderStateName.WaitingForDiscoverAck)
        else:
            self.forward_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())

    def __process_propose_as_leader__(self, message: Message):
        content = message.get_content()
        sending_leader = content.get_sending_leader()
        logging.debug("round {}: opp_particle -> particle {} received propose # {} from #{}".format(
            self.world.get_actual_round(), self.number, self.__instruction_number__, sending_leader.number))
        self.forward_to_leader_via_contacts(message)
        if self.__is__waiting_for_commit__() or self.__is_committed_to_propose__() \
                or LeaderStateName.SendInstruct in self.__leader_states__:
            return
        self.next_direction_proposal_round = None
        self.__instruction_number__ = content.get_number()
        self.__add_leader_state__(LeaderStateName.CommittedToPropose, {sending_leader},
                                  self.world.get_actual_round(), self.t_wait * 2)
        self.__send_content_to_leader_via_contacts__(self, content.get_sending_leader(), LeaderMessageType.commit)
        logging.debug("round {}: opp_particle -> particle {} committed to proposal # {} from particle {}".format(
            self.world.get_actual_round(),
            self.number,
            content.get_number(),
            sending_leader.number))

    def __update__instruct_round_as_leader__(self, received_message: Message):
        instruct_round = self.world.get_actual_round() + received_message.get_content().get_t_wait()
        instruction_number = received_message.get_content().get_number()
        if self.__instruction_number__ and self.instruct_round \
                and self.__instruction_number__ == instruction_number \
                and self.instruct_round >= instruct_round:
            return False
        self.instruct_round = instruct_round
        self.proposed_direction = received_message.get_content().get_proposed_direction()
        self.current_instruct_message = received_message
        return True

    def __process_lost_message_as_leader__(self, message: Message):
        content = message.get_content()
        message_type = content.get_message_type()
        if message_type == LostMessageType.SeparationMessage:
            self.proposed_direction = None
            self.multicast_leader_message(LeaderMessageType.instruct)
            self.reset_random_next_direction_proposal_round()
            self.mobility_model.set_mode(MobilityModelMode.Manual)
            broadcast_message(self, Message(self, message.get_original_sender(),
                                            content=LostMessageContent(LostMessageType.RejoinMessage,
                                                                       self.__get_estimate_centre_from_leader_contacts__())))
        self.__process_lost_message_as_follower__(message)

    def __process_as_follower__(self, received_messages: [Message]):
        self.__add__new_contacts_as_follower__(received_messages)
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.get_message_type()
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_follower__(message)
                elif message_type == LeaderMessageType.discover:
                    self.forward_to_leader_via_contacts(message, content.get_receivers().pop())
                elif message_type in [LeaderMessageType.discover_ack, LeaderMessageType.commit]:
                    self.forward_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())
                else:
                    self.forward_to_leader_via_contacts(message)
            elif isinstance(content, LostMessageContent):
                self.__process_lost_message_as_follower__(message)

    def __add__new_contacts_as_follower__(self, received_messages):
        for message in received_messages:
            if isinstance(message.get_content(), LeaderMessageContent):
                sending_leader = message.get_content().get_sending_leader()
                if sending_leader not in self.leader_contacts:
                    self.__add_route__(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)
                    logging.debug(
                        "round {}: opp_particle -> particle #{} found a new leader #{} with {} hops."
                            .format(self.world.get_actual_round(), self.number, sending_leader.number,
                                    message.get_hops()))
                if message.get_original_sender() not in self.leader_contacts:
                    self.__add_route__(message.get_sender(), message.get_original_sender(), message.get_hops(),
                                       is_leader=True)
            else:
                self.__add_route__(message.get_sender(), message.get_original_sender(), message.get_hops(),
                                   is_leader=False)

    def __process_instruct_as_follower__(self, message: Message):
        self.__update__instruct_round_as_follower_(message)
        logging.debug("round {}: opp_particle -> particle {} received instruct # {}".format(
            self.world.get_actual_round(), self.number, self.__instruction_number__))
        self.__flood_forward__(message)

    def __update__instruct_round_as_follower_(self, received_message: Message):
        content = received_message.get_content()
        new_instruction_round = self.world.get_actual_round() + content.get_t_wait()
        instruction_number = content.get_number()
        if self.__instruction_number__ is None or (instruction_number > self.__instruction_number__):
            self.instruct_round = new_instruction_round
            self.proposed_direction = content.get_proposed_direction()
            self.current_instruct_message = received_message
            self.__instruction_number__ = instruction_number

    def __process_lost_message_as_follower__(self, message: Message):
        content = message.get_content()
        message_type = content.get_message_type()
        if message_type == LostMessageType.RejoinMessage and message.get_actual_receiver() == self:
            self.mobility_model = MobilityModel(self.coordinates, MobilityModelMode.POI,
                                                poi=content.get_current_location())
        elif message_type == LostMessageType.SeparationMessage:
            self.leader_contacts.remove_all_entries_with_particle(message.get_original_sender())
            self.follower_contacts.remove_all_entries_with_particle(message.get_original_sender())
        elif message_type == LostMessageType.QueryNewLocation:
            self.flood_message_content(content)
            self.__add_route__(message.get_sender(), message.get_original_sender(), message.hops, is_leader=False)
            free_locations = self.get_free_surrounding_locations()
            self.send_message_content_via_contacts(message.get_original_sender(),
                                                   LostMessageContent(LostMessageType.FreeLocations,
                                                                      free_locations=free_locations))
            setattr(self, 'query_location_round', self.world.get_actual_round())
        elif message_type == LostMessageType.FreeLocations and message.get_actual_receiver() == self:
            free_locations = getattr(self, 'free_locations', collections.Counter())
            for location in content.get_free_locations():
                free_locations[location] += 1
            setattr(self, 'free_locations', free_locations)

    def update_free_locations(self):
        if (self.world.get_actual_round() - getattr(self, 'query_location_round', np.inf)) >= self.t_wait * 2:
            free_locations = getattr(self, 'free_locations', collections.Counter())
            try:
                next_location = free_locations.most_common(1)[0][0]
                self.mobility_model = MobilityModel(self.coordinates, MobilityModelMode.POI, poi=next_location)
                delattr(self, 'query_location_round')
                delattr(self, 'free_locations')
            except IndexError:
                pass

    def next_moving_direction(self):
        if self.mobility_model.mode == MobilityModelMode.Manual:
            try:
                if self.__instruction_number__ >= self.instruct_round:
                    return self.mobility_model.current_dir
                if self.world.get_actual_round() >= self.instruct_round:
                    self.mobility_model.current_dir = self.proposed_direction
            except TypeError:
                self.mobility_model.current_dir = None
                return None
        elif self.mobility_model.mode == MobilityModelMode.POI:
            next_dir = self.mobility_model.next_direction(self.coordinates)
            if not next_dir:
                self.mobility_model.set_mode(MobilityModelMode.Manual)
                self.flood_message_content(LostMessageContent(LostMessageType.QueryNewLocation))
            return next_dir
        return self.mobility_model.next_direction(self.coordinates)

    def check_current_neighbourhood(self):
        lost, new = self.__neighbourhood_difference__()
        if len(lost) != 0 or len(new) != 0:
            self.leader_contacts.remove_all_entries_with_particles(lost)
            self.set_flock_member_type(FlockMemberType.follower)
            lost_message = Message(self, None, content=LostMessageContent(LostMessageType.SeparationMessage))
            broadcast_message(self, lost_message)
            logging.debug("round {}: opp_particle -> check_neighbourhood() neighbourhood for particle {} has changed."
                          .format(self.world.get_actual_round(), self.number))

    def __neighbourhood_difference__(self):
        neighbourhood = set(self.scan_for_particles_within(self.routing_parameters.scan_radius))
        lost_neighbours = neighbourhood.difference(self.__previous_neighbourhood__)
        new_neighbours = self.__previous_neighbourhood__.difference(neighbourhood)
        self.__previous_neighbourhood__ = neighbourhood
        return lost_neighbours, new_neighbours

    def __get_estimate_centre_from_leader_contacts__(self):
        if len(self.leader_contacts.keys()) > 0:
            x_sum, y_sum, _ = np.sum([leader.coordinates for leader in self.leader_contacts.keys()], axis=0)
            x_sum += self.coordinates[0]
            y_sum += self.coordinates[1]
            return round(x_sum / (len(self.leader_contacts) + 1)), round(y_sum / (len(self.leader_contacts) + 1))
        else:
            return self.coordinates[0], self.coordinates[1]

    def get_coordinates_as_point(self):
        return Point(self.coordinates[0], self.coordinates[1])
