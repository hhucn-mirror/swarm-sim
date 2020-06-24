import logging

from lib.oppnet.communication import Message, broadcast_message
from lib.oppnet.message_types import LostMessageType, LeaderMessageType, LostMessageContent, SafeLocationMessageType, \
    SafeLocationMessage, LeaderMessageContent, PredatorSignal
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.particles import FlockMode
from lib.oppnet.particles.leader_flocking_particle._helper_classes import LeaderStateName
from lib.swarm_sim_header import get_distance_from_coordinates


class Mixin:
    def __process_as_leader__(self, received_messages: [Message]):
        remaining = self.__process_commit_and_ack__(received_messages)
        for message in remaining:
            content = message.get_content()
            if isinstance(content, LeaderMessageContent):
                message_type = content.message_type
                if message_type == LeaderMessageType.instruct:
                    self.__process_instruct_as_leader__(message)
                elif message_type == LeaderMessageType.discover:
                    self.__process_discover_as_leader__(message)
                elif message_type == LeaderMessageType.propose:
                    self.__process_propose_as_leader__(message)
            elif isinstance(content, LostMessageContent):
                self.__process_lost_message_as_leader__(message)
            elif isinstance(content, SafeLocationMessage):
                self.__process_safe_location_message_as_leader(message)
            elif isinstance(content, PredatorSignal):
                self.__process_predator_signal_message_as_leader(message)

    def __process_commit_and_ack__(self, received_messages: [Message]):
        remaining = []
        for message in received_messages:
            content = message.get_content()

            if isinstance(content, LeaderMessageContent):
                message_type = content.message_type
                sending_leader = content.sending_leader
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
            elif isinstance(content, SafeLocationMessage) and message.get_actual_receiver() == self:
                message_type = content.message_type
                if message_type == SafeLocationMessageType.Ack:
                    self.__remove_particle_from_states__(message.get_original_sender(),
                                                         LeaderStateName.WaitingForCommits)
                    if not self.__is__waiting_for_commit__():
                        distance = get_distance_from_coordinates(self.coordinates, content.coordinates)
                        self.__add_leader_state__(LeaderStateName.CommittedToInstruct, set(),
                                                  self.world.get_actual_round(), distance * 2)
                        self.flood_message_content(content.coordinates)
                        self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI,
                                                              poi=content.coordinates))
                else:
                    remaining.append(message)
            else:
                self.__add_route__(message.get_sender(), message.get_original_sender(), message.get_hops(),
                                   is_leader=False)
                remaining.append(message)
        return remaining

    def __process_instruct_as_leader__(self, message: Message):
        logging.debug("round {}: opp_particle -> particle {} received instruct # {}".format(
            self.world.get_actual_round(), self.number, message.get_content().number))
        content = message.get_content()
        if (not self.__is_committed_to_instruct__() and self._is_new_instruct(message)) or content.instruct_override:
            self.__update__instruct_round_as_leader__(message)
            sending_leader = content.sending_leader
            self.__add_leader_state__(LeaderStateName.CommittedToInstruct, {sending_leader},
                                      self.world.get_actual_round(), message.get_hops() * 2)
            self.reset_random_next_direction_proposal_round()
            self.__flood_forward__(message)
            logging.debug("round {}: opp_particle -> particle {} committed to instruct # {}".format(
                self.world.get_actual_round(), self.number, self._instruction_number_))

    def __process_commit_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver().number == self.number and self._instruction_number_ == content.number:
            if self.__is_committed_to_propose__():
                return
            logging.debug("round {}: opp_particle -> particle {} received commit #{} from particle {}"
                          .format(self.world.get_actual_round(),
                                  self.number, content.number, content.sending_leader.number))
            self.__remove_particle_from_states__(content.sending_leader, LeaderStateName.WaitingForCommits)
            if self.__quorum_fulfilled__() and LeaderStateName.SendInstruct not in self.__leader_states__:
                self.__multicast_instruct__()
        else:
            self.send_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())

    def __process_discover_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__send_content_to_leader_via_contacts__(self, content.sending_leader,
                                                         LeaderMessageType.discover_ack)

    def __process_discover_ack_as_leader__(self, message: Message):
        content = message.get_content()
        if message.get_actual_receiver() == self:
            self.__remove_particle_from_states__(content.sending_leader, LeaderStateName.WaitingForDiscoverAck)
        else:
            self.send_to_leader_via_contacts(message, receiving_leader=message.get_actual_receiver())

    def __process_propose_as_leader__(self, message: Message):
        content = message.get_content()
        sending_leader = content.sending_leader
        logging.debug("round {}: opp_particle -> particle {} received propose # {} from #{}".format(
            self.world.get_actual_round(), self.number, self._instruction_number_, sending_leader.number))
        # self.send_to_leader_via_contacts(message)
        if self.__is__waiting_for_commit__() or self.__is_committed_to_propose__() \
                or LeaderStateName.SendInstruct in self.__leader_states__:
            return
        self.next_direction_proposal_round = None
        self._instruction_number_ = content.number
        self.__add_leader_state__(LeaderStateName.CommittedToPropose, {sending_leader},
                                  self.world.get_actual_round(), self.t_wait * 2)
        self.__send_content_to_leader_via_contacts__(self, content.sending_leader, LeaderMessageType.commit)
        logging.debug("round {}: opp_particle -> particle {} committed to proposal # {} from particle {}".format(
            self.world.get_actual_round(),
            self.number,
            content.number,
            sending_leader.number))

    def __process_lost_message_as_leader__(self, message: Message):
        content = message.get_content()
        message_type = content.message_type
        if message_type == LostMessageType.SeparationMessage:
            if not self.__is_in_leader_states__(LeaderStateName.WaitingForRejoin):
                if len(self.leader_contacts) == 0:
                    self.proposed_direction = None
                    self.multicast_leader_message(LeaderMessageType.instruct)
                else:
                    self.send_direction_proposal(False)
            self.__add_leader_state__(LeaderStateName.WaitingForRejoin, {message.get_original_sender()},
                                      self.world.get_actual_round(), self.t_wait * 10)
            self.reset_random_next_direction_proposal_round()
            broadcast_message(self, Message(self, message.get_original_sender(), content=LostMessageContent(
                LostMessageType.RejoinMessage, self.__get_estimate_centre_from_leader_contacts__())))
        elif message_type == LostMessageType.QueryNewLocation:
            self.__remove_particle_from_states__(message.get_original_sender(), LeaderStateName.WaitingForRejoin)
        self.__process_lost_message_as_follower__(message)

    def __process_safe_location_message_as_leader(self, message):
        content = message.get_content()
        if content.message_type == SafeLocationMessageType.TileAdded:
            self.safe_locations.append(content.coordinates)
            if self.flock_mode != FlockMode.Flocking:
                self.mobility_model.set_mode(MobilityModelMode.POI)
                self.mobility_model.poi = content.coordinates
                self.proposed_direction = self.mobility_model.next_direction(self.coordinates)
        elif content.message_type == SafeLocationMessageType.Proposal and not self.__is_committed_to_instruct__():
            response_content = SafeLocationMessage(content.coordinates, [message.get_original_sender()],
                                                   SafeLocationMessageType.Ack)
            self.send_to_leader_via_contacts(Message(self, message.get_original_sender(), content=response_content),
                                             message.get_original_sender())
            self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=content.coordinates))

    def __process_predator_signal_message_as_leader(self, message):
        content = message.get_content()
        predator_ids = set(content.predator_coordinates.keys())
        new_predator_ids = predator_ids.difference(self.__detected_predator_ids__)
        if new_predator_ids:
            for predator_id in new_predator_ids:
                new_escape_direction = self.__update_predator_escape_direction(
                    content.predator_coordinates[predator_id], use_relative_location=False)
                self.mobility_model.current_dir = new_escape_direction
            self.__detected_predator_ids__.update(predator_ids)
            self.proposed_direction = self.mobility_model.current_dir
            self.__multicast_instruct__(instruct_override=True)

    def __quorum_fulfilled__(self):
        if self.__is__waiting_for_commit__():
            waiting_count = self.__leader_states__[LeaderStateName.WaitingForCommits].waiting_count()
            leader_count = len(self.leader_contacts.keys())
            return (1 - waiting_count / leader_count) > self.commit_quorum
        else:
            return True

    def __update__instruct_round_as_leader__(self, received_message: Message):
        instruct_round = self.world.get_actual_round() + received_message.get_content().t_wait
        self.instruct_round = instruct_round
        self.proposed_direction = received_message.get_content().proposed_direction
        self._current_instruct_message = received_message

    def _is_new_instruct(self, received_message):
        instruct_round = self.world.get_actual_round() + received_message.get_content().t_wait
        instruction_number = received_message.get_content().number
        return not (self._instruction_number_ and self.instruct_round
                    and self._instruction_number_ == instruction_number
                    and self.instruct_round >= instruct_round)
