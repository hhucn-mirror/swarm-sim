class DirectionMessageContent:
    """
    Message content contain a direction value and indicating the neighboring particles it was sent to.
    """

    def __init__(self, direction, neighborhood):
        """
        Constructor. Initializes direction value and sets neighbor particle receivers.
        :param direction: direction value
        :param neighborhood: list of particles
        """
        self.__direction__ = direction
        self.__neighborhood__ = neighborhood

    def get_direction(self):
        """
        Gets the direction value.
        :return: direction value
        """
        return self.__direction__

    def get_neighborhood(self):
        """
        Gets the receiving neighborhood list.
        :return: list particles
        """
        return self.__neighborhood__
