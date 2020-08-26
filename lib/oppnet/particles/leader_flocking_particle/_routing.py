import logging

from lib.oppnet.message_types import LeaderMessageType, LeaderMessageContent
from lib.oppnet.particles.leader_flocking_particle._helper_classes import LeaderStateName
from lib.oppnet.routing import RoutingContact


class Mixin:
    def __add_route__(self, contact, target, hops, is_leader=False):
        """
        Adds a route from the particle to :param target particle over the :param contact particle with :param hops.
        :param contact: contact particle
        :param target: target particle
        :param hops: hops between this particle and the target
        :param is_leader: target is leader
        :return: None
        """
        if self.number == contact.number or self.number == target.number:
            return
        logging.debug("round {}: opp_particle -> route: {} via {} to {} with {} hops".format(
            self.world.get_actual_round(), self.number, contact.number, target.number, hops))
        if is_leader:
            self.leader_contacts.add_contact(contact, target, hops)
        else:
            self.follower_contacts.add_contact(contact, target, hops)

    def __delete_route__(self, contact, is_leader=False):
        """
        Deletes all routes to :param contact.
        :param contact: contact to delete
        :param is_leader: target is leader
        :return: None
        """
        if is_leader:
            self.leader_contacts.remove_contact(contact)
        else:
            self.follower_contacts.remove_contact(contact)

    def __delete_target_routes__(self, target_id, is_leader=False):
        """
        Tries to delete routes to a target with id :param target_id.
        :param target_id: id of the target particle
        :param is_leader: target is leader
        :return: None
        """
        try:
            target_particle = self.world.get_particle_map_id()[target_id]
            if is_leader:
                self.leader_contacts.remove_target(target_particle)
            else:
                self.follower_contacts.remove_target(target_particle)
        except KeyError:
            logging.debug("round {}: opp_particle -> delete_target_routes() tried deleting non-existent target_id."
                          .format(self.world.get_actual_round()))

    def __new_leader_found__(self, message, sending_leader):
        """
        Adds new route to a message sending leader via the sender/forwarder.
        :param message: message to use
        :param sending_leader: sending leader of the message
        :return: None
        """
        self.__add_route__(message.get_sender(), sending_leader, message.get_hops(), is_leader=True)
        self.__send_content_to_leader_via_contacts__(self, sending_leader, LeaderMessageType.discover)
        logging.debug(
            "round {}: opp_particle -> particle #{} found a new leader #{} with {} hops."
                .format(self.world.get_actual_round(), self.number, sending_leader.number, message.get_hops()))
        self.__add_leader_state__(LeaderStateName.WaitingForDiscoverAck, {sending_leader},
                                  self.world.get_actual_round(), message.get_hops() * 2)

    def __get_t_wait_value_for_leader_contact(self, leader, contact):
        """
        Gets the t_wait vale for a leader contact based on the route.
        :param leader: target particle
        :param contact: contact particle
        :return: int
        """
        if isinstance(contact, RoutingContact):
            contact = contact.get_contact_particle()
        try:
            t_wait = self.t_wait - self.leader_contacts.get_contact(leader, contact).get_hops()
        except KeyError:
            t_wait = self.t_wait
        return t_wait

    def __add_new_contacts_as_follower__(self, received_messages):
        """
        Adds routes to a follower ignoring broadcasts and using the sending leader as target. Will
        also use the original sender and sender of the messages received.
        :param received_messages: messages received.
        :return: None
        """
        for message in received_messages:
            if not message.is_broadcast:
                if isinstance(message.get_content(), LeaderMessageContent):
                    sending_leader = message.get_content().sending_leader
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
