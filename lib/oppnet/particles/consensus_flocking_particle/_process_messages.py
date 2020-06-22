import logging

from lib.oppnet.communication import Message, multicast_message_content
from lib.oppnet.message_types import DirectionMessageContent, RelativeLocationMessageContent, PredatorSignal, \
    SafeLocationMessage
from lib.oppnet.mobility_model import MobilityModelMode
from lib.oppnet.particles import FlockMode
from lib.oppnet.util import get_direction_between_coordinates


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
                self.__process_predator_signal(message, content)
            elif isinstance(content, SafeLocationMessage):
                self.__process_safe_location_added(message, content)
            else:
                logging.debug("round {}: opp_particle -> received an unknown content type.")

    def __process_direction_message__(self, message: Message, content: DirectionMessageContent):
        """
        Processes a :param message with :param content.
        :param message: the message to process.
        :param content: the content of the message.
        :return: nothing
        """
        if message.get_sender() not in self.__current_neighborhood__:
            logging.debug("round {}: opp_particle -> received direction from a non-neighbour.")
        self.__current_neighborhood__[message.get_sender()] = content
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
            self.flock_mode = FlockMode.FoundLocation
            if self.relative_flock_location != updated_location:
                self.relative_flock_location = updated_location
                self.relative_cardinal_location = get_direction_between_coordinates(self.relative_flock_location,
                                                                                    (0, 0, 0))

    def __process_predator_signal(self, message, content: PredatorSignal):
        """
        Processes a PredatorSignal message.
        :param message: the message to process
        :type message: Message
        :param content: the content of the message
        :type content: PredatorSignal
        """
        if self.__detected_predator_ids__ and self.__detected_predator_ids__.issuperset(content.predator_ids):
            return
        self.__detected_predator_ids__.update(content.predator_ids)
        escape_direction = self.__extract_escape_direction__(content.predator_coordinates, message)
        self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        self.mobility_model.current_dir = escape_direction
        self.set_flock_mode(FlockMode.Dispersing)
        # forward to all neighbors not in the receiver list, if the message wasn't a broadcast
        if not message.is_broadcast:
            neighbors = set(self.__current_neighborhood__.keys()).union({self})
            new_receivers = content.receivers.symmetric_difference(neighbors)
            content.update_receivers(neighbors)
            if new_receivers:
                multicast_message_content(self, new_receivers, content)

    def __extract_escape_direction__(self, predator_coordinates, message):
        # if it's a warning sent from a particle, process the list of predator coordinates
        for coordinates in predator_coordinates:
            self.mobility_model.current_dir = self.__update_predator_escape_direction(coordinates)
        return self.mobility_model.current_dir

    def __process_safe_location_added(self, message, content):
        if content.coordinates not in self.safe_locations:
            self.safe_locations.append(content.coordinates)
