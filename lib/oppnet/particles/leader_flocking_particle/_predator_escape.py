from lib.oppnet.message_types import PredatorSignal
from lib.oppnet.mobility_model import MobilityModelMode
from lib.oppnet.particles import FlockMemberType


class Mixin:
    def __predators_detected__(self, predators):
        if self._flock_member_type == FlockMemberType.follower:
            self.__predators_detected_follower(predators)
        else:
            self.__predators_detected_leader(predators)

    def __predators_detected_follower(self, predators):
        predator_coordinates = {}
        for predator in predators:
            if predator.get_id() not in self.__detected_predator_ids__:
                predator_coordinates[predator.get_id()] = predator.coordinates
        if predator_coordinates:
            self.__detected_predator_ids__.update(set(predator_coordinates.keys()))
            content = PredatorSignal(predator_coordinates)
            self._send_via_all_contacts__(content, self.leader_contacts.keys())

    def __predators_detected_leader(self, predators):
        self.mobility_model.set_mode(MobilityModelMode.Manual)
        predator_ids = set()
        for predator in predators:
            new_escape_direction = self.__update_predator_escape_direction(predator.coordinates,
                                                                           use_relative_location=False)
            self.mobility_model.current_dir = new_escape_direction
            predator_ids.add(predator.get_id())
        self.proposed_direction = self.mobility_model.current_dir
        self.__detected_predator_ids__.update(predator_ids)
        self.__multicast_instruct__(instruct_override=True)
