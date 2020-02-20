class DirectionMessageContent:
    def __init__(self, direction, neighbourhood):
        self.__direction__ = direction
        self.__neighbourhood__ = neighbourhood

    def get_direction(self):
        return self.__direction__

    def get_neighbourhood(self):
        return self.__neighbourhood__
