from lib.oppnet.message_types.relative_location_message import CardinalDirection


class PredatorSignal:
    def __init__(self, approaching_direction: CardinalDirection):
        self.approaching_direction = approaching_direction
