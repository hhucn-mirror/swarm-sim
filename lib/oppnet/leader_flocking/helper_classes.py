from enum import Enum


class FlockMemberType(Enum):
    leader = 0
    follower = 1


class LeaderStateName(Enum):
    WaitingForCommits = 0,
    WaitingForDiscoverAck = 1,
    CommitedToPropose = 2,
    CommittedToInstruct = 3,
    PerformingInstruct = 4,
    SendInstruct = 5


class LeaderState:

    def __init__(self, leader_state_name: LeaderStateName, waiting_ids: set, start_round, expected_rounds=0):
        self.leader_state_name = leader_state_name
        self.waiting_ids = waiting_ids
        self.start_round = start_round
        self.end_round = start_round + expected_rounds

    def get_leader_state_name(self):
        return self.leader_state_name

    def add_to_waiting(self, id_to_add):
        self.waiting_ids.add(id_to_add)

    def remove_from_waiting(self, id_to_remove):
        self.waiting_ids.remove(id_to_remove)

    def get_waiting_ids(self):
        return self.waiting_ids

    def is_completed(self):
        if self.leader_state_name in [LeaderStateName.WaitingForCommits, LeaderStateName.WaitingForDiscoverAck,
                                      LeaderStateName.CommittedToInstruct, LeaderStateName.CommitedToPropose]:
            return len(self.waiting_ids) == 0
        else:
            return True

    def is_timed_out(self, current_round):
        if not self.leader_state_name == LeaderStateName.PerformingInstruct:
            return self.end_round <= current_round
        else:
            return False
