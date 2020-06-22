import logging

from lib.oppnet.communication import send_message


class Mixin:

    def __update_contacts__(self, message):
        """
        Adds the sender of the :param message as contact for the message's original sender.
        :param message: the message.
        :return: nothing
        """
        self.contacts.add_contact(message.get_sender(), message.get_original_sender(), message.get_hops())
        self.world.update_flock_id_for_particles([message.get_sender(), message.get_original_sender(), self])

    def __hops_per_direction_for_neighbor(self, queried_directions=None):
        """
        Creates a hops per direction dictionary for all directions in :param queried_directions. If that is None,
        it will create it for all entries in self.__max_cardinal_direction_hops__.
        :param queried_directions: list of directions to include in the dictionary
        :type queried_directions: list
        :return: dictionary of direction, hops
        :rtype: dict
        """
        hops_per_direction = {}
        if not queried_directions:
            for direction, hops in self.__max_cardinal_direction_hops__.items():
                hops_per_direction[direction] = hops + 1
        else:
            for direction in queried_directions:
                if direction in self.__max_cardinal_direction_hops__:
                    hops = self.__max_cardinal_direction_hops__[direction]
                    hops_per_direction[direction] = hops + 1
        return hops_per_direction

    def forward_via_contact(self, message):
        """
        Tries to forward a :param message via the particle's RoutingMap contacts.
        :param message: the message.
        :return: nothing
        """
        try:
            for contact_particle in self.contacts[message.actual_receiver].keys():
                send_message(self, contact_particle, message)
        except KeyError:
            logging.debug("round {}: opp_particle -> no contact to forward message.")
