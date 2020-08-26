import logging

from ._helper_classes import LeaderStateName, LeaderState


class Mixin:
    def __add_leader_state__(self, state_name, waiting_particles, start_round, expected_rounds):
        """
        Adds a LeaderState to the particles map of leaderstates.
        :param state_name: LeaderStateName
        :param waiting_particles: particles to wait for
        :param start_round: round the state starts
        :param expected_rounds: expected number of rounds for the state to last
        :return: None
        """
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
        """
        Remove the particle from a leader state by :param state_name.
        :param waiting_particle: the particle to remove
        :param state_name: the LeaderStateName the particle was in the waiting list of
        :return: None
        """
        if state_name in self.__leader_states__:
            try:
                leader_state = self.__leader_states__[state_name]
            except KeyError:
                del self.__leader_states__[state_name]
                return
            try:
                leader_state.remove_from_waiting(waiting_particle)
            except KeyError:
                pass

    def update_leader_states(self):
        """
        Updates the particles leaderstates by removing timed_out ones and resetting the next direction proposal
        round if it is no longer waiting for commits or committed to a proposal.
        :return:
        """
        keys_to_delete = []
        for leader_state_name, leader_state in self.__leader_states__.items():
            if leader_state.is_timed_out(self.world.get_actual_round()):
                keys_to_delete.append(leader_state_name)
        for leader_state_name in keys_to_delete:
            if leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.CommittedToPropose]:
                self.reset_random_next_direction_proposal_round()
            del self.__leader_states__[leader_state_name]

    def __is__waiting_for_commit__(self):
        """
        Determines if the particle is waiting for a commit.
        :return: boolean
        """
        return self.__is_in_leader_states__(LeaderStateName.WaitingForCommits)

    def __is_committed_to_instruct__(self):
        """
        Determines if the particle is committed to an instruct.
        :return: boolean
        """
        return self.__is_in_leader_states__(LeaderStateName.CommittedToInstruct)

    def __is_committed_to_propose__(self):
        """
        Determines if the particle is committed to a proposal.
        :return: boolean
        """
        return self.__is_in_leader_states__(LeaderStateName.CommittedToPropose)

    def __is__waiting_for_discover_ack__(self):
        """
        Determines if the particle is waiting for a discover_ack.
        :return: boolean
        """
        return self.__is_in_leader_states__(LeaderStateName.WaitingForDiscoverAck)

    def __is_in_leader_states__(self, state_name):
        """
        Determines if the particle has a leaderstate with LeaderStateName :param state_name.
        :return: boolean
        """
        if state_name in self.__leader_states__:
            leader_state = self.__leader_states__[state_name]
            return not leader_state.is_completed()
        else:
            return False
