from enum import Enum


class LeaderMessageType(Enum):
    propose = 0
    discover = 1
    discover_ack = 2
    instruct = 3
    commit = 4


class LeaderMessageContent:

    def __init__(self, leader, proposed_direction, receivers, t_wait, message_type, number):
        self.__number__ = number
        self.__leader__ = leader
        self.__proposed__direction = proposed_direction
        self.__receivers__ = receivers
        self.__t_wait__ = t_wait
        self.__message_type__ = message_type

    def get_leader(self):
        return self.__leader__

    def get_proposed_direction(self):
        return self.__proposed__direction

    def get_receivers(self):
        return self.__receivers__

    def get_t_wait(self):
        return self.__t_wait__

    def get_message_type(self):
        return self.__message_type__

    def get_number(self):
        return self.__number__

    def create_forward_copy(self, new_receivers, t_wait_decrement=1):
        new_t_wait = self.get_t_wait() - t_wait_decrement
        forward_copy = type(self)(self.get_leader(), self.get_proposed_direction(), new_receivers, new_t_wait,
                                  self.get_message_type(), self.__number__)
        return forward_copy

    def __eq__(self, other):
        return self.get_number() == other.get_number()

    def __gt__(self, other):
        return self.get_number() > other.get_number()

    def __ge__(self, other):
        return self.get_number() >= other.get_number()

    def __lt__(self, other):
        return self.get_number() < other.get_number()

    def __le__(self, other):
        return self.get_number() <= other.get_number()
