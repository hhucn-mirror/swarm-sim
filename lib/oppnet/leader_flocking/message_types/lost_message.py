from enum import Enum


class LostMessageType(Enum):
    SeparationMessage = 0,
    RejoinMessage = 1,
    QueryNewLocation = 2,
    FreeLocations = 3


class LostMessageContent:
    def __init__(self, message_type: LostMessageType, current_location=None, free_locations=None):
        self.current_location = current_location
        self.message_type = message_type
        self.free_locations = free_locations

    def get_current_location(self):
        return self.current_location

    def get_message_type(self):
        return self.message_type

    def get_free_locations(self):
        return self.free_locations
