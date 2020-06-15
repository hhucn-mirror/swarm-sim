class PredatorSignal:
    def __init__(self, predator_ids, predator_coordinates=None):
        if predator_coordinates is None:
            predator_coordinates = []
        self.predator_ids = predator_ids
        self.receivers = set()
        self.predator_coordinates = predator_coordinates

    def update_receivers(self, receivers):
        self.receivers.update(receivers)
