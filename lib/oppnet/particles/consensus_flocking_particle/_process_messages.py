import logging

from lib.oppnet.communication import Message
from lib.oppnet.message_types import DirectionMessageContent, RelativeLocationMessageContent, PredatorSignal, \
    SafeLocationMessage
from lib.oppnet.particles import FlockMode
from lib.swarm_sim_header import get_direction_between_coordinates


class Mixin:
    def process_received(self):
        """
        Processes each message in the rcv_store of the particle.
        :return: nothing.
        """
        while len(self.rcv_store) > 0:
            message = self.rcv_store.pop()
            content = message.get_content()
            self.__update_contacts__(message)
            if isinstance(content, DirectionMessageContent):
                self.__process_direction_message__(message, content)
            elif isinstance(content, RelativeLocationMessageContent):
                self.__process_relative_location_message(message, content)
            elif isinstance(content, PredatorSignal):
                self.process_predator_signal(message, content, use_relative_location=True)
            elif isinstance(content, SafeLocationMessage):
                self.__process_safe_location_added(content)
            else:
                logging.debug("round {}: opp_particle -> received an unknown content type.")

    def __process_direction_message__(self, message: Message, content: DirectionMessageContent):
        """
        Processes a :param message with :param content.
        :param message: the message to process.
        :param content: the content of the message.
        :return: nothing
        """
        if message.get_sender() not in self.current_neighborhood:
            logging.debug("round {}: opp_particle -> received direction from a non-neighbour.")
        self.current_neighborhood[message.get_sender()] = content
        self.__neighborhood_direction_counter__[content.get_direction()] += 1

    def __process_relative_location_message(self, message, content):
        """
        Processes a RelativeLocationMessageContent. If it's a query, the particle will try to answer it immediately,
        otherwise store it to answer as soon as it receives a reply for the queried directions itself.
        :param message: the message to process
        :type message: Message
        :param content: the content of the message
        :type content: RelativeLocationMessageContent
        :return: nothing
        """

        for direction, hops in content.hops_per_direction.items():
            if direction not in self.__max_cardinal_direction_hops__:
                self.__max_cardinal_direction_hops__[direction] = hops
            elif self.__max_cardinal_direction_hops__[direction] > hops:
                logging.debug("round {}: particle #{} received non-queried hops for direction {}".format(
                    self.world.get_actual_round(), self.number, str(direction)
                ))

        if not content.is_response:
            self.__received_queried_directions__[message.get_original_sender()] = content.queried_directions

        self.__send_relative_location_response__()

        updated_location = RelativeLocationMessageContent.get_relative_location(self.__max_cardinal_direction_hops__)
        if updated_location:
            self.set_flock_mode(FlockMode.FoundLocation)
            if self.relative_flock_location != updated_location:
                self.relative_flock_location = updated_location
                self.relative_cardinal_location = get_direction_between_coordinates(self.relative_flock_location,
                                                                                    (0, 0, 0))

    def __process_safe_location_added(self, content):
        self.recent_safe_location = content.coordinates
