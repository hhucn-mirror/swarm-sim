class PredatorSignal:
    def __init__(self, predator_id_coordinates_dict):
        self.receivers = set()
        self.predator_coordinates = predator_id_coordinates_dict

    def update_receivers(self, receivers):
        self.receivers.update(receivers)
