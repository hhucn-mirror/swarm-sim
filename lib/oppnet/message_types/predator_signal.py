class PredatorSignal:
    """
    Warning signal send by a predator and passed on by particles in a flock.
    """

    def __init__(self, predator_id_coordinates_dict):
        """
        Constructor. Initializes variables.
        :param predator_id_coordinates_dict: dictionary of predator coordinates by predator id.
        """
        self.receivers = set()
        self.predator_coordinates = predator_id_coordinates_dict

    def update_receivers(self, receivers):
        """
        Adds the set :param receivers: to the current receivers.
        :param receivers: set of particles
        :return: None
        """
        self.receivers.update(receivers)
