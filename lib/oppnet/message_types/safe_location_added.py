class SafeLocationAdded:
    def __init__(self, coordinates, receivers=None):
        self.coordinates = coordinates
        if receivers is not None:
            self.receivers = set(receivers)
        else:
            self.receivers = set()

    def update_receivers(self, receivers):
        self.receivers.update(receivers)
        return self.receivers
