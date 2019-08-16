from enum import Enum


class EventType(Enum):
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessageDeliveredUnique = 4
    MessageDeliveredDirectUnique = 5
    MessageTTLExpired = 6
    #
    ReceiverOutOfMem = 10


class NetworkEvent:

    def __init__(self, event_type, sender, receiver, event_round, message):
        self.event_type = event_type
        self.sender = sender
        self.receiver = receiver
        self.event_round = event_round
        self.message = message
