from enum import Enum


class LeaderStateName(Enum):
    WaitingForCommits = 0,
    WaitingForDiscoverAck = 1,
    CommittedToPropose = 2,
    CommittedToInstruct = 3,
    PerformingInstruct = 4,
    SendInstruct = 5,
    WaitingForRejoin = 6


class LeaderState:

    def __init__(self, leader_state_name: LeaderStateName, waiting_particles: set, start_round, expected_rounds=0):
        self.leader_state_name = leader_state_name
        self.waiting_particles = waiting_particles
        self.start_round = start_round
        self.end_round = start_round + expected_rounds

    def get_leader_state_name(self):
        return self.leader_state_name

    def add_to_waiting(self, particle_to_add):
        if isinstance(particle_to_add, set):
            self.waiting_particles.union(particle_to_add)
        else:
            self.waiting_particles.add(particle_to_add)

    def remove_from_waiting(self, particle_to_remove):
        self.waiting_particles.remove(particle_to_remove)

    def get_waiting_particles(self):
        return self.waiting_particles

    def waiting_count(self):
        return len(self.waiting_particles)

    def is_completed(self):
        if self.leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck,
                                      LeaderStateName.CommittedToInstruct, LeaderStateName.CommittedToPropose,
                                      LeaderStateName.WaitingForRejoin]:
            return len(self.waiting_particles) == 0
        else:
            return True

    def is_timed_out(self, current_round):
        if not self.leader_state_name == LeaderStateName.PerformingInstruct:
            return self.end_round <= current_round
        else:
            return False
