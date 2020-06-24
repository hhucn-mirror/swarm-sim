import random

from lib.oppnet.communication import multicast_message_content
from lib.oppnet.message_types import PredatorSignal
from lib.oppnet.mobility_model import MobilityModelMode, MobilityModel
from lib.oppnet.particles import FlockMode


class Mixin:

    def go_to_safe_location(self):
        self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=self.get_a_safe_location()))
        self.set_flock_mode(FlockMode.Regrouping)
        return self.mobility_model.next_direction(self.coordinates, self.get_blocked_surrounding_locations())

    def get_a_safe_location(self):
        return random.choice(self.safe_locations)

    def __predators_detected__(self, predators):
        new_predator_ids = predator_ids = set([predator.get_id() for predator in predators])
        if self.flock_mode == FlockMode.Dispersing:
            # reset number of steps
            if not predator_ids.issubset(self.__detected_predator_ids__):
                self.mobility_model.steps = 0
        else:
            self.flock_mode = FlockMode.Dispersing
            self.mobility_model.set_mode(MobilityModelMode.DisperseFlock)
        if not predator_ids.issubset(self.__detected_predator_ids__):
            predator_coordinates = {}
            # take all predators into account
            for predator in predators:
                new_escape_direction = self.__update_predator_escape_direction(predator.coordinates)
                self.mobility_model.current_dir = new_escape_direction
                if predator.get_id() not in self.__detected_predator_ids__:
                    predator_coordinates[predator.get_id()] = predator.coordinates
                else:
                    predator_ids.remove(predator.get_id())
            multicast_message_content(self, self.current_neighborhood.keys(),
                                      PredatorSignal(predator_coordinates))
            self.__detected_predator_ids__ = new_predator_ids
        return self.mobility_model.next_direction(self.coordinates)
