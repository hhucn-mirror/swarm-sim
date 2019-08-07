from enum import Enum

from lib.colors import Colors


class EventType(Enum):
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessagesDeliveredUnique = 4
    MessageTTLExpired = 5
    #
    ReceiverOutOfMem = 10


class NetworkEvent:

    def __init__(self, event_type, sender, receiver, message=None):
        self.event_type = event_type
        self.sender = sender
        self.receiver = receiver
        self.message = message
