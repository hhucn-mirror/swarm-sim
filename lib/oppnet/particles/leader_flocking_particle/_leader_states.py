import logging

from ._helper_classes import LeaderStateName, LeaderState


class Mixin:
    def __add_leader_state__(self, state_name, waiting_particles, start_round, expected_rounds):
        if state_name not in self.__leader_states__ or self.__leader_states__[state_name] is None \
                or state_name == LeaderStateName.WaitingForRejoin:
            self.__leader_states__[state_name] = LeaderState(state_name, waiting_particles, start_round,
                                                             expected_rounds)
        elif state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck]:
            self.__leader_states__[state_name].add_to_waiting(waiting_particles)
        else:
            logging.debug(
                "round {}: opp_particle -> __add_leader_state__() Tried adding LeaderState {} which is already set!"
                    .format(start_round, state_name.name))

    def __remove_particle_from_states__(self, waiting_particle, state_name):
        if state_name in self.__leader_states__:
            try:
                self.__leader_states__[state_name].remove_from_waiting(waiting_particle)
            except KeyError:
                del self.__leader_states__[state_name]

    def update_leader_states(self):
        keys_to_delete = []
        for leader_state_name, leader_state in self.__leader_states__.items():
            if leader_state.is_timed_out(self.world.get_actual_round()):
                keys_to_delete.append(leader_state_name)
        for leader_state_name in keys_to_delete:
            if leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.CommittedToPropose]:
                self.reset_random_next_direction_proposal_round()
            del self.__leader_states__[leader_state_name]

    def __is__waiting_for_commit__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForCommits)

    def __is_committed_to_instruct__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommittedToInstruct)

    def __is_committed_to_propose__(self):
        return self.__is_in_leader_states__(LeaderStateName.CommittedToPropose)

    def __is__waiting_for_discover_ack__(self):
        return self.__is_in_leader_states__(LeaderStateName.WaitingForDiscoverAck)

    def __is_in_leader_states__(self, state_name):
        if state_name in self.__leader_states__:
            leader_state = self.__leader_states__[state_name]
            return not leader_state.is_completed()
        else:
            return False
