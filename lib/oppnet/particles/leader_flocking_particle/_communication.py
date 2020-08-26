import logging

from lib.oppnet.communication import multicast_message_content, send_message, Message
from lib.oppnet.message_types import LeaderMessageContent, LeaderMessageType
from lib.oppnet.message_types.safe_location_message import SafeLocationMessage, SafeLocationMessageType
from lib.oppnet.particles import FlockMode
from lib.oppnet.particles.leader_flocking_particle._helper_classes import LeaderStateName
from lib.particle import Particle


class Mixin:
    def multicast_leader_message(self, message_type: LeaderMessageType, neighbors=None, instruct_override=False):
        """
        Multicast for a LeaderMessageContent of type :param message_type to :param neighbors.
        :param message_type: LeaderMessageType
        :param neighbors: receiving neighbors
        :param instruct_override: indicate an important instruction
        :return:
        """
        max_hops = self.routing_parameters.interaction_radius
        if not neighbors:
            neighbors = self.scan_for_particles_within(hop=max_hops)

        if message_type == LeaderMessageType.instruct:
            if self.__is_in_leader_states__(LeaderStateName.WaitingForRejoin):
                return
            self.instruct_round = self.t_wait + self.world.get_actual_round()
            number = self._instruction_number_ = self.world.get_actual_round()
        elif message_type == LeaderMessageType.discover:
            number = self._instruction_number_ = None
        elif self._instruction_number_ is not None:
            number = self._instruction_number_
        else:
            number = self.world.get_actual_round()

        for hop in range(1, max_hops + 1):
            receivers = self.scan_for_particles_in(hop=hop)

            content = LeaderMessageContent(self, self.proposed_direction, neighbors, self.t_wait - hop,
                                           message_type, number, instruct_override)
            multicast_message_content(self, receivers, content)

    def send_safe_location_proposal(self, safe_location=None):
        """
        Sends a safe location proposal message
        :param safe_location: proposed safe location coordinates
        :return: None
        """
        if safe_location is None:
            safe_location = self.get_a_safe_location()
        content = SafeLocationMessage(safe_location, self.leader_contacts.keys(), SafeLocationMessageType.Proposal)
        receivers = self.leader_contacts.keys()
        self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(receivers), self.world.get_actual_round(),
                                  self.t_wait * 2)
        self._send_via_all_contacts__(content, receivers)

    def send_direction_proposal(self, proposed_direction=None):
        """
        Sends a direction proposal to neighbors but prefers sending to leaders of the RoutingMap
        :param proposed_direction: the direction to propose
        :return: None
        """
        if proposed_direction is None:
            proposed_direction = self.choose_direction()
        if self.__is_committed_to_propose__() or self.__is_committed_to_instruct__():
            self.reset_random_next_direction_proposal_round()
            return
        receiving_leaders = self.leader_contacts.keys()
        self._instruction_number_ = self.world.get_actual_round()
        self.__send_proposal_to_leaders__(proposed_direction)
        if len(receiving_leaders) == 0:
            self.multicast_leader_message(LeaderMessageType.propose)
        self.reset_random_next_direction_proposal_round()

    def __send_proposal_to_leaders__(self, proposed_direction):
        """
        Sends a proposal to leaders in the particles RoutingMap.
        :param proposed_direction: the direction to propose
        :return: None
        """
        self.__add_leader_state__(LeaderStateName.WaitingForCommits, set(self.leader_contacts.keys()),
                                  self.world.get_actual_round(), self.t_wait * 2 + 1)
        for leader, contacts in self.leader_contacts.items():
            for contact_particle, contact in contacts.items():
                content = LeaderMessageContent(self, proposed_direction,
                                               self.current_neighborhood,
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
        """
        Multicast a message with :param message_content to all neighbors with the maximum particle interaction radius.
        :param message_content: content of the message
        :return: None
        """
        receivers = self.scan_for_particles_within(hop=self.routing_parameters.interaction_radius)
        multicast_message_content(self, receivers, message_content)

    def send_message_content_via_contacts(self, receiver, message_content):
        """
        Sends a message via contacts of the particles routing maps.
        :param receiver: the receiver of the message
        :param message_content: content of the message to send
        :return: None
        """
        if receiver in self.leader_contacts:
            receivers = self.leader_contacts[receiver].keys()
        elif receiver in self.follower_contacts:
            receivers = self.follower_contacts[receiver].keys()
        else:
            receivers = self.current_neighborhood
        for contact_particle in receivers:
            send_message(self, contact_particle, Message(self, receiver, content=message_content))

    def __flood_forward__(self, received_message):
        """
        Forwards a message using flooding but will exclude receivers that are already set inside the
        content of the message and will also exclude the sender and original sender.
        :param received_message: Message to forward
        :return: None
        """
        received_content = received_message.get_content()
        if isinstance(received_content, LeaderMessageContent):
            exclude = {received_message.get_sender(), received_message.get_content().sending_leader,
                       received_message.get_original_sender()}.union(received_content.receivers)
            message_type = received_content.message_type
            try:
                instruction_number = received_content.number
                if instruction_number is not None and self.world.get_actual_round() >= self.instruct_round:
                    return
            except TypeError:
                pass
        else:
            message_type = received_content.__class__
            exclude = {received_message.get_sender(), received_message.get_original_sender()}
        max_hops = self.routing_parameters.interaction_radius
        neighbors = self.scan_for_particles_within(hop=max_hops)

        all_receivers = set(neighbors).union(exclude)
        for hop in range(1, max_hops + 1):
            receivers = set(self.scan_for_particles_in(hop=hop)).difference(exclude)
            if isinstance(received_content, LeaderMessageContent):
                content = received_content.create_forward_copy(all_receivers, hop)
            else:
                content = received_content
            received_message.set_content(content)
            for receiver in receivers:
                received_message.set_actual_receiver(receiver)
                send_message(self, receiver, received_message)
                logging.debug("round {}: opp_particle -> particle {} forwarded {} to {}".format(
                    self.world.get_actual_round(), self.number, message_type, receiver.number))

    def send_to_leader_via_contacts(self, message, receiving_leader=None):
        """
        Tries to send a message to a leader via the particles routing maps. If the receiving leader is not set,
        it will be send to all leaders that the particle is aware of.
        :param message: message to send
        :param receiving_leader: the receiving leader
        :return: None
        """
        received_content = message.get_content()
        if receiving_leader and receiving_leader not in self.leader_contacts:
            return self.__flood_forward__(message)

        if receiving_leader:
            receivers = {receiving_leader}
        elif isinstance(received_content, LeaderMessageContent):
            receivers = set(received_content.receivers)
        else:
            receivers = set(self.leader_contacts.keys())
        receivers.difference_update(
            {
                message.get_sender(),
                message.get_original_sender()
            })
        for receiver in receivers:
            if receiver not in self.leader_contacts and self.flock_mode != FlockMode.Flocking:
                self.__flood_forward__(message)
                break
        self._send_via_all_contacts__(received_content, receivers)

    def _send_via_all_contacts__(self, message_content, receivers):
        """
        Sends a message with :param message_content to a list of :param receivers.
        :param message_content: the content of the message
        :param receivers: the receivers of the message
        :return: None
        """
        message = Message(self, None)
        for leader_particle in receivers:
            for contact in self.leader_contacts.get_leader_contacts(leader_particle):
                hops = contact.get_hops()
                if isinstance(message_content, LeaderMessageContent):
                    content = message_content.create_forward_copy(receivers, hops)
                    message_type = message_content.message_type
                else:
                    message_type = message_content.__class__
                    content = message_content
                message.set_content(content)
                message.set_actual_receiver(leader_particle)
                send_message(self, contact.get_contact_particle(), message)
                logging.debug("round {}: opp_particle -> particle {} forwarded {} to {} via {}".format(
                    self.world.get_actual_round(), self.number, message_type, leader_particle.number,
                    contact.get_contact_particle().number))
        self.send_store.remove(message)

    def __send_content_to_leader_via_contacts__(self, sending_leader: Particle, receiving_leader: Particle,
                                                message_type: LeaderMessageType,
                                                contacts=None, proposed_direction=None):
        """
        Tries to send a new LeaderMessageContent message to :param receiving_leader as :param sending_leader. This
        will prefer using leader contacts. If the neither :param contacts nor :param receiving_leader are set, this
        will cancel. If the particle has no entry for :param receiving_leader, it will flood the message.
        :param sending_leader: sending leader to use
        :param receiving_leader: leader to receive the message
        :param message_type: type of LeaderMessageContent to create
        :param contacts: RoutingMap to use
        :param proposed_direction: proposed direction of the content
        :return: None
        """
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

    def __multicast_instruct__(self, instruct_override=False):
        """
        Multicast an instruct LeaderMessageContent message.
        :param instruct_override: boolean
        :return: None
        """
        self.multicast_leader_message(LeaderMessageType.instruct, instruct_override=instruct_override)
        self.__add_leader_state__(LeaderStateName.SendInstruct, set(), self.world.get_actual_round(),
                                  self.t_wait * 2)
        self.reset_random_next_direction_proposal_round()
        logging.debug("round {}: opp_particle -> particle {} broadcast instruct # {}".format(
            self.world.get_actual_round(),
            self.number,
            self._instruction_number_))
