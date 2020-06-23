import logging
import random
from collections import Counter

import numpy as np

import lib.oppnet.particles as particles
from lib.oppnet.communication import Message, broadcast_message
from lib.oppnet.message_types import LostMessageContent, LostMessageType
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.routing import RoutingMap
from . import _leader_states, _process_as_follower, _process_as_leader, _communication, _routing, _predator_escape
from .. import FlockMode


class Particle(particles.Particle, _leader_states.Mixin, _process_as_follower.Mixin, _process_as_leader.Mixin,
               _communication.Mixin, _routing.Mixin, _predator_escape.Mixin):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 t_wait=0):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator, ms_size=ms_size, ms_strategy=ms_strategy, mm_mode=mm_mode,
                         mm_length=mm_length, mm_zone=mm_zone, mm_starting_dir=mm_starting_dir)

        self.t_wait = t_wait
        self.instruct_round = None
        self._instruction_number_ = None
        self.proposed_direction = None

        self._current_instruct_message = None

        self._flock_member_type = particles.FlockMemberType.follower
        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

        self.next_direction_proposal_round = None
        self._next_proposal_seed = 0
        self.__leader_states__ = dict()

        self.commit_quorum = self.world.config_data.commit_quorum
        self.flock_mode = particles.FlockMode.Searching
        self.__previous_neighborhood__ = set(self.scan_for_particles_within(self.routing_parameters.scan_radius))

        self.safe_locations = []

    def set_t_wait(self, t_wait):
        self.t_wait = t_wait

    def set_next_direction_proposal_round(self, next_round):
        self.next_direction_proposal_round = next_round
        self._next_proposal_seed = next_round
        random.seed(next_round)

    def set_instruction_number(self, instruction_number):
        self._instruction_number_ = instruction_number

    def reset_random_next_direction_proposal_round(self):
        self._next_proposal_seed += random.randint(1, self.t_wait * 10)
        self.next_direction_proposal_round = self._next_proposal_seed + self.world.get_actual_round()

    def set_flock_member_type(self, flock_member_type):
        self._flock_member_type = flock_member_type

    def get_flock_member_type(self):
        return self._flock_member_type

    def get_all_received_messages(self):
        received, to_forward = [], []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        while len(self.send_store) > 0:
            received.append(self.send_store.pop())
        return received

    def get_current_instruct(self):
        return self._current_instruct_message

    def choose_direction(self, no_movement=False):
        if self.mobility_model.mode == MobilityModelMode.POI:
            self.mobility_model.set_mode(MobilityModelMode.Manual)
        directions = list(self.world.grid.get_directions_dictionary().values())
        if no_movement:
            directions.append(None)
        self.proposed_direction = random.choice(directions)
        return self.proposed_direction

    def update_current_neighborhood(self):
        lost, new = self.__neighborhood_difference__()
        if len(lost) > 0 and len(self.__previous_neighborhood__) == 0 and self.flock_mode == FlockMode.Flocking:
            self.flock_mode = FlockMode.Regrouping
            self.proposed_direction = None
            self.mobility_model.set_mode(MobilityModelMode.Manual)
            self.leader_contacts.remove_all_entries_with_particles(lost)
            lost_message = Message(self, None, content=LostMessageContent(LostMessageType.SeparationMessage))
            broadcast_message(self, lost_message)
            logging.debug("round {}: opp_particle -> check_neighborhood() neighborhood for particle {} has changed."
                          .format(self.world.get_actual_round(), self.number))

    def __neighborhood_difference__(self):
        neighborhood = set(self.scan_for_particles_within(self.routing_parameters.scan_radius))
        lost_neighbors = self.__previous_neighborhood__.difference(neighborhood)
        new_neighbors = neighborhood.difference(self.__previous_neighborhood__)
        self.__previous_neighborhood__ = neighborhood
        if self.__previous_neighborhood__ is not None and self.flock_mode == FlockMode.Searching:
            self.set_flock_mode(FlockMode.Flocking)
        return lost_neighbors, new_neighbors

    def __get_estimate_centre_from_leader_contacts__(self):
        if len(self.leader_contacts.keys()) > 0:
            x_sum, y_sum, _ = np.sum([leader.coordinates for leader in self.leader_contacts.keys()], axis=0)
            x_sum += self.coordinates[0]
            y_sum += self.coordinates[1]
            return round(x_sum / (len(self.leader_contacts) + 1)), round(y_sum / (len(self.leader_contacts) + 1))
        else:
            return self.coordinates[0], self.coordinates[1]

    def update_free_locations(self):
        if (self.world.get_actual_round() - getattr(self, 'query_location_round', np.inf)) >= self.t_wait * 2:
            free_locations = getattr(self, 'free_locations', Counter())
            try:
                next_location = free_locations.most_common(1)[0][0]
                self.set_mobility_model(MobilityModel(self.coordinates, MobilityModelMode.POI, poi=next_location))
                delattr(self, 'query_location_round')
                delattr(self, 'free_locations')
            except IndexError:
                pass

    def next_moving_direction(self):
        if self.mobility_model.mode == MobilityModelMode.Manual:
            try:
                if self._instruction_number_ >= self.instruct_round:
                    return self.mobility_model.current_dir
                if self.world.get_actual_round() >= self.instruct_round:
                    self.mobility_model.current_dir = self.proposed_direction
            except TypeError:
                self.mobility_model.current_dir = None
                return None
        elif self.mobility_model.mode == MobilityModelMode.POI:
            return self.mobility_model.next_direction(self.coordinates, self.get_blocked_surrounding_locations())
        return self.mobility_model.next_direction(self.coordinates)
