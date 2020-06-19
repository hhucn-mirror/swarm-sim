from enum import Enum


class LeaderMessageType(Enum):
    propose = 0
    discover = 1
    discover_ack = 2
    instruct = 3
    commit = 4


class LeaderMessageContent:

    def __init__(self, sending_leader, proposed_direction, receivers, t_wait, message_type, number):
        self.__number__ = number
        self.__sending_leader__ = sending_leader
        self.__proposed__direction = proposed_direction
        self.__receivers__ = receivers
        self.__t_wait__ = t_wait
        self._message_type = message_type

    @property
    def sending_leader(self):
        return self.__sending_leader__

    @property
    def proposed_direction(self):
        return self.__proposed__direction

    @property
    def receivers(self):
        return self.__receivers__

    @property
    def t_wait(self):
        return self.__t_wait__

    @property
    def message_type(self):
        return self._message_type

    @property
    def number(self):
        return self.__number__

    def create_forward_copy(self, new_receivers, t_wait_decrement=1):
        new_t_wait = self.t_wait - t_wait_decrement
        forward_copy = type(self)(self.sending_leader, self.proposed_direction, new_receivers, new_t_wait,
                                  self.message_type, self.__number__)
        return forward_copy

    def __eq__(self, other):
        return self.number == other.number

    def __gt__(self, other):
        return self.number > other.number

    def __ge__(self, other):
        return self.number >= other.number

    def __lt__(self, other):
        return self.number < other.number

    def __le__(self, other):
        return self.number <= other.number
