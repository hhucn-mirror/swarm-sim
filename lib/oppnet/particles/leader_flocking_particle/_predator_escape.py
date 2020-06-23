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
        predator_coordinates = set()
        new_predator_ids = predator_ids = set([predator.get_id() for predator in predators])
        for predator in predators:
            if predator not in self.__detected_predator_ids__:
                predator_coordinates.add(predator.coordinates)
            else:
                predator_ids.remove(predator.get_id())
        self.__detected_predator_ids__ = new_predator_ids
        content = PredatorSignal(predator_ids, predator_coordinates)
        self._send_via_all_contacts__(content, self.leader_contacts.keys())

    def __predators_detected_leader(self, predators):
        self.mobility_model.set_mode(MobilityModelMode.Manual)
        predator_ids = set()
        for predator in predators:
            self.mobility_model.current_dir = self.__update_predator_escape_direction(predator.coordinates)
            if predator.get_id() not in self.__detected_predator_ids__:
                predator_ids = predator.get_id()
        self.proposed_direction = self.mobility_model.current_dir
        self.__detected_predator_ids__ = predator_ids
        self.__multicast_instruct__(instruct_override=True)
