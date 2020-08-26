import collections
import logging

from lib.oppnet.communication import Message
from lib.oppnet.message_types import LeaderMessageType, LeaderMessageContent, SafeLocationMessage, LostMessageContent, \
    LostMessageType, PredatorSignal
from lib.oppnet.mobility_model import MobilityModelMode, MobilityModel
from lib.oppnet.particles import FlockMode


class Mixin:
    def __process_as_follower__(self, received_messages: [Message]):
        """
        Processes messages as a follower. Calls the specific methods depending on content.
        :param received_messages: list of received messages
        :return: None
        """
        self.__add_new_contacts_as_follower__(received_messages)
        for message in received_messages:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.message_type
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_follower__(message)
                elif message_type == LeaderMessageType.discover:
                    self.__flood_forward__(message)
                elif message_type in [LeaderMessageType.discover_ack, LeaderMessageType.commit,
                                      LeaderMessageType.propose]:
                    self.send_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())
                else:
                    self.send_to_leader_via_contacts(message)
            elif isinstance(content, LostMessageContent):
                self.__process_lost_message_as_follower__(message)
            elif isinstance(content, SafeLocationMessage):
                self.__process_safe_location_message_as_follower(message)
            elif isinstance(content, PredatorSignal):
                self.process_predator_signal(message, content)

    def __process_instruct_as_follower__(self, message: Message):
        """
        Updates the particles instruct message if its a new instruct. Will then also flood this message to neighbors.
        :param message: the instruct message received
        :return: None
        """
        message_content = message.get_content()
        if self._instruction_number_ is None or (message_content.number > self._instruction_number_) \
                or message_content.instruct_override:
            self.set_flock_mode(FlockMode.Flocking)
            self.__update__instruct_round_as_follower_(message)
            self.__flood_forward__(message)
            logging.debug("round {}: follower {} updated instruct # {}, proposed direction: {} instruct round:{}"
                          .format(self.world.get_actual_round(), self.number, self._instruction_number_,
                                  self.proposed_direction, self.instruct_round))

    def __update__instruct_round_as_follower_(self, received_message: Message):
        """
        Updates the instruct variables of the particle. Determining the round to move and setting the mobility model.
        :param received_message: the instruct message received
        :return: None
        """
        content = received_message.get_content()
        new_instruction_round = self.world.get_actual_round() + content.t_wait
        instruction_number = content.number
        self.instruct_round = new_instruction_round
        self.proposed_direction = content.proposed_direction
        self._current_instruct_message = received_message
        self._instruction_number_ = instruction_number
        self.t_wait = content.t_wait
        self.mobility_model.set_mode(MobilityModelMode.Manual)

    def __process_lost_message_as_follower__(self, message: Message):
        """
        Processes a lost message and responds accordingly. Will use a rejoin message to determine a location to regroup
        with the flock, remove a particle from its contacts if it separated from the flock, respond with a
        free surrounding locations if queried or apply a counter of free locations as coordinates to move to.
        :param message: received lost message
        :return:
        """
        content = message.get_content()
        message_type = content.message_type
        if message_type == LostMessageType.RejoinMessage:
            self.recent_safe_location = content.get_current_location()
            if message.get_actual_receiver() == self:
                self.set_flock_mode(FlockMode.Regrouping)
                self.mobility_model = MobilityModel(self.coordinates, MobilityModelMode.POI,
                                                    poi=content.get_current_location())
                logging.debug("round {}: follower {} received RejoinMessage for location: {}"
                              .format(self.world.get_actual_round(), self.number, content.get_current_location()))
        elif message_type == LostMessageType.SeparationMessage:
            self.leader_contacts.remove_all_entries_with_particle(message.get_original_sender())
            self.follower_contacts.remove_all_entries_with_particle(message.get_original_sender())
            if not message.is_broadcast:
                self.send_to_leader_via_contacts(message)
            logging.debug("round {}: follower {} received SeparationMessage from {}"
                          .format(self.world.get_actual_round(), self.number, message.get_original_sender().number))
        elif message_type == LostMessageType.QueryNewLocation and self.flock_mode == FlockMode.Flocking:
            free_locations = self.get_free_surrounding_locations()
            self.send_message_content_via_contacts(message.get_original_sender(),
                                                   LostMessageContent(LostMessageType.FreeLocations,
                                                                      free_locations=free_locations))
            setattr(self, 'query_location_round', self.world.get_actual_round())
            logging.debug("round {}: follower {} received QueryNewLocation from {}"
                          .format(self.world.get_actual_round(), self.number, message.get_original_sender().number))
            self.__flood_forward__(message)
        elif message_type == LostMessageType.FreeLocations and message.get_actual_receiver() == self:
            free_locations = getattr(self, 'free_locations', collections.Counter())
            for location in content.get_free_locations():
                free_locations[location] += 1
            setattr(self, 'free_locations', free_locations)
            if free_locations.most_common(1):
                next_location = free_locations.most_common(1)[0][0]
                self.mobility_model.set_mode(MobilityModelMode.POI)
                self.mobility_model.poi = next_location
                self.set_flock_mode(FlockMode.Flocking)

    def __process_safe_location_message_as_follower(self, message):
        """
        Applies the safe location in the message as POI to move to.
        :param message: the received safe location message
        :return: None
        """
        content = message.get_content()
        self.recent_safe_location = content.coordinates
        self.set_flock_mode(FlockMode.Searching)
        self.mobility_model.set_mode(MobilityModelMode.POI)
        self.mobility_model.poi = content.coordinates
        self.proposed_direction = self.mobility_model.next_direction(self.coordinates)
        logging.debug("round {}: particle {} applied SafeLocationMessage as POI to coordinates: {}"
                      .format(self.world.get_actual_round(), self.number, content.coordinates))
