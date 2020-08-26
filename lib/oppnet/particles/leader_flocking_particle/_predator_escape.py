from lib.oppnet.message_types import PredatorSignal
from lib.oppnet.mobility_model import MobilityModelMode
from lib.oppnet.particles import FlockMemberType


class Mixin:
    def __predators_detected__(self, predators):
        """
        Calls the specific methods for a Follower or Leader Particle.
        :param predators: list of predators detected
        :return: None
        """
        if self._flock_member_type == FlockMemberType.Follower:
            self.__predators_detected_follower(predators)
        else:
            self.__predators_detected_leader(predators)

    def __predators_detected_follower(self, predators):
        """
        Updates the dictionary of detected predators and sends a PredatorSignal message
        to all leaders if there are newly detected ones.
        :param predators: list of predators detected
        :return: None
        """
        predator_coordinates = {}
        for predator in predators:
            if predator.get_id() not in self.__detected_predator_ids__:
                predator_coordinates[predator.get_id()] = predator.coordinates
        if predator_coordinates:
            self.__detected_predator_ids__.update(set(predator_coordinates.keys()))
            content = PredatorSignal(predator_coordinates)
            self._send_via_all_contacts__(content, self.leader_contacts.keys())

    def __predators_detected_leader(self, predators):
        """
        Updates the dictionary of detected predators and determines an escape direction. Will instruct the flock
        to move in this direction.
        :param predators: list of predators detected
        :return: None
        """
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
