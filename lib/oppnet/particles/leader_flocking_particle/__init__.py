import logging
import random
from collections import Counter

import numpy as np

import lib.oppnet.particles as particles
from lib.oppnet.communication import Message, broadcast_message
from lib.oppnet.message_types import LostMessageContent, LostMessageType, LeaderMessageType
from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode
from lib.oppnet.routing import RoutingMap
from . import _leader_states, _process_as_follower, _process_as_leader, _communication, _routing
from ._helper_classes import LeaderStateName
from .. import FlockMode, FlockMemberType


class Particle(particles.Particle, _leader_states.Mixin, _process_as_follower.Mixin, _process_as_leader.Mixin,
               _communication.Mixin, _routing.Mixin):
    def __init__(self, world, coordinates, color, particle_counter=0, csv_generator=None, ms_size=None,
                 ms_strategy=None, mm_mode=None, mm_length=None, mm_zone=None, mm_starting_dir=None,
                 t_wait=None):
        super().__init__(world=world, coordinates=coordinates, color=color, particle_counter=particle_counter,
                         csv_generator=csv_generator, ms_size=ms_size, ms_strategy=ms_strategy, mm_mode=mm_mode,
                         mm_length=mm_length, mm_zone=mm_zone, mm_starting_dir=mm_starting_dir)
        if not t_wait or t_wait == 0:
            t_wait = world.config_data.flock_radius * 2
        self.t_wait = t_wait
        self.instruct_round = None
        self._instruction_number_ = None
        self.proposed_direction = None

        self._current_instruct_message = None

        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

        self.next_direction_proposal_round = None
        self._next_proposal_seed = 0
        self.__leader_states__ = dict()

        self.commit_quorum = self.world.config_data.commit_quorum
        self.flock_mode = particles.FlockMode.Flocking

        self.initial_neighborhood = set()
        self.current_neighborhood = set()
        self.previous_neighborhood = set()

        self.instruct_override = self.world.config_data.instruct_override

    def set_t_wait(self, t_wait):
        self.t_wait = t_wait

    def set_next_direction_proposal_round(self, next_round):
        self.next_direction_proposal_round = next_round
        self._next_proposal_seed = next_round

    def set_instruction_number(self, instruction_number):
        self._instruction_number_ = instruction_number

    def reset_random_next_direction_proposal_round(self):
        # make sure t_wait is set if this particle was selected as new leader
        self.t_wait = self.world.config_data.flock_radius * 2
        self._next_proposal_seed += random.randint(1, self.t_wait * 10)
        self.next_direction_proposal_round = self._next_proposal_seed + self.world.get_actual_round()

    def reset_routing_and_instructs(self):
        self.proposed_direction = None
        self.instruct_round = None
        self.leader_contacts = RoutingMap()
        self.follower_contacts = RoutingMap()

    def get_all_received_messages(self):
        received, to_forward = [], []
        while len(self.rcv_store) > 0:
            received.append(self.rcv_store.pop())
        while len(self.send_store) > 0:
            to_forward.append(self.send_store.pop())
        return received, to_forward

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
        self.follower_contacts.remove_all_entries_with_particles(lost)
        self.leader_contacts.remove_all_entries_with_particles(lost)
        if self._flock_member_type == FlockMemberType.Leader:
            self._wait_for_flock_rejoin()
        if len(self.current_neighborhood) == 0 or ((len(lost) > 1 and len(new) == 0) and self.flock_mode not in [
            FlockMode.Regrouping, FlockMode.Optimizing]):
            self.go_to_safe_location()
            self._lost_particle()
            self.reset_routing_and_instructs()
        elif len(new) > 0 and self.flock_mode == FlockMode.Regrouping \
                and self.mobility_model.mode == MobilityModelMode.Manual:
            self.flood_message_content(LostMessageContent(LostMessageType.QueryNewLocation))
            self.set_flock_mode(FlockMode.Optimizing)

    def _lost_particle(self):
        self.set_flock_mode(FlockMode.Regrouping)
        message_content = LostMessageContent(LostMessageType.SeparationMessage)
        broadcast_message(self, Message(self, None, content=message_content))
        logging.debug("round {}: neighborhood for particle {} has changed. broadcast a SeparationMessage"
                      .format(self.world.get_actual_round(), self.number))

    def _wait_for_flock_rejoin(self):
        predators = self.predators_nearby()
        if len(predators) == 0 and self.flock_mode == FlockMode.Regrouping and not self.__is_in_leader_states__(
                LeaderStateName.WaitingForRejoin):
            self.broadcast_safe_location(self.recent_safe_location)
            self.set_flock_mode(FlockMode.Searching)
            self.__add_leader_state__(LeaderStateName.WaitingForRejoin, set(self.previous_neighborhood),
                                      self.world.get_actual_round(), 20)
        elif len(self.current_neighborhood) == 6 and not self.__is_in_leader_states__(LeaderStateName.WaitingForRejoin) \
                and self.flock_mode != FlockMode.Flocking:
            self.set_flock_mode(FlockMode.Flocking)
            self.multicast_leader_message(LeaderMessageType.discover)
            self.broadcast_safe_location(self.recent_safe_location)
            self.__add_leader_state__(LeaderStateName.WaitingForRejoin, set(self.previous_neighborhood),
                                      self.world.get_actual_round(), 20)
            self.set_next_direction_proposal_round(self.world.get_actual_round() + 20)

    def __neighborhood_difference__(self):
        neighborhood = set(self.scan_for_particles_within(self.routing_parameters.interaction_radius))
        lost_neighbors = self.current_neighborhood.difference(neighborhood)
        new_neighbors = neighborhood.difference(self.current_neighborhood)
        self.previous_neighborhood = self.current_neighborhood
        self.current_neighborhood = neighborhood
        return lost_neighbors, new_neighbors

    def __get_estimate_center_from_leader_contacts__(self):
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

    def get_next_direction(self):
        predators_nearby = self.predators_nearby()
        if predators_nearby:
            next_direction = self.predators_detected_disperse(predators_nearby)
            return next_direction
        if self.flock_mode == FlockMode.Dispersing:
            return self._get_next_direction_dispersing(self.mobility_model.next_direction(self.coordinates))
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
            next_direction = self.mobility_model.next_direction(self.coordinates,
                                                                self.get_blocked_surrounding_locations())
            # reached POI or did not move any closer
            if not next_direction and self.flock_mode == FlockMode.Regrouping:
                self.mobility_model.set_mode(MobilityModelMode.Manual)
            return next_direction
        return self.mobility_model.next_direction(self.coordinates)
