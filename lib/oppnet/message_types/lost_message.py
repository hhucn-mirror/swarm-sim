from enum import Enum


class LostMessageType(Enum):
    """
    Enum to distinguish LostMessageContent
    """
    SeparationMessage = 0,
    RejoinMessage = 1,
    QueryNewLocation = 2,
    FreeLocations = 3


class LostMessageContent:
    """
    Message that indicates a particle has connection to the flock or is trying to rejoin.
    """

    def __init__(self, message_type: LostMessageType, current_location=None, free_locations=None):
        """
        Constructor. Initializes variables.
        :param message_type: LostMessageType
        :param current_location: current location of the flock for a RejoinMessage
        :param free_locations: list of free locations near a flock in as an answer to QueryNewLocation
        """
        self.current_location = current_location
        self.message_type = message_type
        self.free_locations = free_locations

    def get_current_location(self):
        """
        Gets the current location variable.
        :return: current location coordinates
        """
        return self.current_location

    def get_message_type(self):
        """
        Gets the message type.
        :return: LostMessageType
        """
        return self.message_type

    def get_free_locations(self):
        """
        Gets the list of free locations.
        :return: list of location coordinates.
        """
        return self.free_locations
