class DirectionMessageContent:
    def __init__(self, direction, neighborhood):
        self.__direction__ = direction
        self.__neighborhood__ = neighborhood

    def get_direction(self):
        return self.__direction__

    def get_neighborhood(self):
        return self.__neighborhood__
