class Point(object):
    """
    2D coordinate object.
    """

    def __init__(self, x, y):
        """
        Constructor
        :param x: x coordinate
        :param y: y coordinate
        """
        self.x = x
        self.y = y

    def getx(self):
        """
        Returns the x coordinate.
        :return: x coordinate
        """
        return self.x

    def gety(self):
        """
        Returns the y coordinate.
        :return: y coordinate
        """
        return self.y
