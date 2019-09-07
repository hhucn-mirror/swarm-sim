from enum import Enum


class EventType(Enum):
    MessageSent = 0
    MessageDelivered = 1
    MessageDeliveredDirect = 2
    MessageForwarded = 3
    MessageDeliveredFirst = 4
    MessageDeliveredFirstDirect = 5
    MessageTTLExpired = 6
    #
    ReceiverOutOfMem = 10


class NetworkEvent:

    def __init__(self, event_type, sender, receiver, event_round, message):
        """
        :param event_type: The type of event
        :type event_type: :class:`~meta.EventType`
        :param sender: The particle sending the Message.
        :type sender: :class:`~particle.Particle`
        :param receiver: The intended receiver of the message.
        :type receiver: :class:`~particle.Particle`
        :param event_round: The round the event occurred in.
        :type event_round: int
        :param message: The message to send.
        :type message: :class:`~comms.Message`
        """
        self.event_type = event_type
        self.sender = sender
        self.receiver = receiver
        self.event_round = event_round
        self.message = message
