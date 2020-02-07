from enum import Enum


class LostMessageType(Enum):
    SeparationMessage = 0,
    RejoinMessage = 1


class LostMessageContent:
    def __init__(self, current_location, message_type: LostMessageType):
        self.current_location = current_location
        self.message_type = message_type

    def get_current_location(self):
        return self.current_location

    def get_message_type(self):
        return self.message_type
