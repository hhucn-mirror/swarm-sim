from enum import Enum


class SafeLocationMessageType(Enum):
    """
    Enum to distinguish SafeLocationMessage.
    """
    TileAdded = 0,
    Proposal = 1,
    Ack = 2,
    Regroup = 3


class SafeLocationMessage:
    """
    Message content for safe locations.
    """

    def __init__(self, coordinates, receivers=None, message_type=None):
        """
        Constructor. Initializes values.
        :param coordinates: location coordinates determined as the safe location
        :param receivers: set of receivers of this message
        :param message_type: SafeLocationMessageType
        """
        self._coordinates = coordinates
        if receivers is not None:
            self.receivers = set(receivers)
        else:
            self.receivers = set()
        if message_type is None:
            message_type = SafeLocationMessageType.TileAdded
        self._message_type = message_type

    def update_receivers(self, receivers):
        """
        Updates the set of receivers with :param receivers.
        :param receivers: set of particles
        :return: new set of receivers
        """
        self.receivers.update(receivers)
        return self.receivers

    @property
    def coordinates(self):
        return self._coordinates

    @property
    def message_type(self):
        return self._message_type
