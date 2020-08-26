from enum import Enum


class LeaderStateName(Enum):
    """
    Enum to distinguish LeaderState
    """
    WaitingForCommits = 0,
    WaitingForDiscoverAck = 1,
    CommittedToPropose = 2,
    CommittedToInstruct = 3,
    PerformingInstruct = 4,
    SendInstruct = 5,
    WaitingForRejoin = 6


class LeaderState:
    """
    State to track whether the leader particle is waiting for commits, discovery acks etc.
    """

    def __init__(self, leader_state_name: LeaderStateName, waiting_particles: set, start_round, expected_rounds=0):
        """
        Constructor. Initializes values
        :param leader_state_name: LeaderStateName
        :param waiting_particles: set of particles expected to respond
        :param start_round: simulator round the state started
        :param expected_rounds: expected number of simulator rounds the state will last
        """
        self.leader_state_name = leader_state_name
        self.waiting_particles = waiting_particles
        self.start_round = start_round
        self.end_round = start_round + expected_rounds

    def get_leader_state_name(self):
        """
        Gets the LeaderStateName.
        :return: LeaderStateName
        """
        return self.leader_state_name

    def add_to_waiting(self, particle_to_add):
        """
        Adds a particle to the set of particles to wait for.
        :param particle_to_add: particle
        :return: None
        """
        if isinstance(particle_to_add, set):
            self.waiting_particles.union(particle_to_add)
        else:
            self.waiting_particles.add(particle_to_add)

    def remove_from_waiting(self, particle_to_remove):
        """
        Removes a particle from the set of particles to wait for.
        :param particle_to_remove: particle
        :return: None
        """
        self.waiting_particles.remove(particle_to_remove)

    def get_waiting_particles(self):
        """
        Gets the set of particles the state is waiting on.
        :return: set of particles
        """
        return self.waiting_particles

    def waiting_count(self):
        """
        Gets the number of particles the state is waiting on.
        :return: int
        """
        return len(self.waiting_particles)

    def is_completed(self):
        """
        Determines if the state is complete. Will be complete if set of waiting particles is empty for most states.
        Other states will always be completed as they are only placeholders, such as SendInstruct.
        :return:
        """
        if self.leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck,
                                      LeaderStateName.CommittedToInstruct, LeaderStateName.CommittedToPropose,
                                      LeaderStateName.WaitingForRejoin]:
            return len(self.waiting_particles) == 0
        else:
            return True

    def is_timed_out(self, current_round):
        """
        Determines if the state has timed out, i.e. if the expected number of rounds has passed.
        :param current_round: the current simulator round
        :return: boolean
        """
        if not self.leader_state_name == LeaderStateName.PerformingInstruct:
            return self.end_round <= current_round
        else:
            return False
