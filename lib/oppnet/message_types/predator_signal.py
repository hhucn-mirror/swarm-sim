from lib.oppnet.message_types.relative_location_message import CardinalDirection


class PredatorSignal:
    def __init__(self):
        self.receivers = set()

    def update_receivers(self, receivers):
        self.receivers.update(receivers)
