import logging
import random

from lib.oppnet.communication import multicast_message_content, send_message, Message, broadcast_message
from lib.oppnet.message_types import LeaderMessageContent, LeaderMessageType
from lib.oppnet.message_types.safe_location_message import SafeLocationMessage, SafeLocationMessageType
from lib.oppnet.particles.leader_flocking_particle._helper_classes import LeaderStateName
from lib.particle import Particle


class Mixin:
    def multicast_leader_message(self, message_type: LeaderMessageType, neighbors=None):
        max_hops = self.routing_parameters.scan_radius
        if not neighbors:
            neighbors = self.scan_for_particles_within(hop=max_hops)

        if message_type == LeaderMessageType.instruct:
            self.instruct_round = self.t_wait + self.world.get_actual_round()
            self._instruction_number_ = self.world.get_actual_round()

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)
            number = self._instruction_number_ if self._instruction_number_ is not None \
                else self.world.get_actual_round()
            content = LeaderMessageContent(self, self.proposed_direction, neighbors, self.t_wait - hop,
                                           message_type, number)
            multicast_message_content(self, receivers, content)

    def broadcast_safe_location(self, safe_location=None):
        if not safe_location:
            safe_location = self._get_a_safe_location()
        message = Message(self, None, content=SafeLocationMessage(safe_location))
        broadcast_message(self, message)

    def _get_a_safe_location(self):
        if not self.safe_locations:
            return self.coordinates
        else:
            return random.choice(self.safe_locations)

    def send_safe_location_proposal(self, safe_location=None):
        if safe_location is None:
            safe_location = self._get_a_safe_location()
        content = SafeLocationMessage(safe_location, self.leader_contacts.keys(), SafeLocationMessageType.Proposal)
        receivers = self.leader_contacts.keys()
        self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(receivers), self.world.get_actual_round(),
                                  self.t_wait * 2)
        multicast_message_content(self, receivers, content)

    def send_direction_proposal(self, proposed_direction=None):
        if proposed_direction is None:
            proposed_direction = self.choose_direction()
        receiving_leaders = self.leader_contacts.keys()
        self._instruction_number_ = self.world.get_actual_round()
        self.__send_proposal_to_leaders__(proposed_direction)
        if len(receiving_leaders) == 0:
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
                                               self._instruction_number_)
                message = Message(self, leader, content=content)
                message.set_actual_receiver(leader)
                send_message(self, contact_particle, message)
                logging.debug("round {}: opp_particle -> particle {} send direction proposal # {} to {} via {}".format(
                    self.world.get_actual_round(), self.number, self._instruction_number_, leader.number,
                    contact_particle.number))

    def flood_message_content(self, message_content):
        receivers = self.scan_for_particles_within(hop=self.routing_parameters.scan_radius)
        multicast_message_content(self, receivers, message_content)

    def send_message_content_via_contacts(self, receiver, message_content):
        if receiver not in self.follower_contacts:
            receivers = self.__previous_neighborhood__
        else:
            receivers = self.follower_contacts[receiver].keys()
        for contact_particle in receivers:
            send_message(self, contact_particle, Message(self, receiver, content=message_content))

    def __flood_forward__(self, received_message):
        received_content = received_message.get_content()
        instruction_number = received_content.number
        try:
            if instruction_number is not None and self.world.get_actual_round() >= self.instruct_round:
                return
        except TypeError:
            pass
        max_hops = self.routing_parameters.scan_radius
        neighbors = self.scan_for_particles_within(hop=max_hops)
        exclude = {received_message.get_sender(), received_message.get_content().sending_leader,
                   received_message.get_original_sender()}.union(received_content.receivers)
        all_receivers = set(neighbors).difference(exclude)
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
                    self.world.get_actual_round(), self.number, content.message_type.name,
                    content.number, receiver.number))

    def forward_to_leader_via_contacts(self, received_message, receiving_leader=None):
        received_content = received_message.get_content()
        if receiving_leader and receiving_leader not in self.leader_contacts:
            self.__flood_forward__(received_message)
        else:
            if receiving_leader:
                receivers = {receiving_leader}
            elif isinstance(received_content, LeaderMessageContent):
                receivers = set(received_content.receivers)
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
                    self.world.get_actual_round(), self.number, content.message_type.name,
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
                                                            self._instruction_number_))
            return
        for _, contact in contacts.items():
            t_wait = self.__get_t_wait_value_for_leader_contact(receiving_leader, contact)
            content = LeaderMessageContent(sending_leader, proposed_direction, {receiving_leader}, t_wait, message_type,
                                           self._instruction_number_)
            send_message(self, contact.get_contact_particle(), Message(self, receiving_leader, content=content))

    def __multicast_instruct__(self):
        self.reset_random_next_direction_proposal_round()
        self.multicast_leader_message(LeaderMessageType.instruct)
        self.__add_leader_state__(LeaderStateName.SendInstruct, set(), self.world.get_actual_round(),
                                  self.t_wait * 2)
        logging.debug("round {}: opp_particle -> particle {} broadcast instruct # {}".format(
            self.world.get_actual_round(),
            self.number,
            self._instruction_number_))
