import random
from enum import Enum


class MobilityModelMode(Enum):
    """
    Used to easily distinguish MobilityModels.
    """
    Random_Walk = 0
    Back_And_Forth = 1
    Circle = 2
    Random = 3
    Static = 4
    Zonal = 5
    POI = 6
    Manual = 7
    Random_Mode = 8


class MobilityModel:
    """
    Class to define particle movement.
    """
    NE = (0.5, 1, 0)
    E = (1, 0, 0)
    SE = (0.5, -1, 0)
    SW = (-0.5, -1, 0)
    W = (-1, 0, 0)
    NW = (-0.5, 1, 0)

    directions = [NE, E, SE, SW, W, NW]

    def __init__(self, start_coordinates, mode: MobilityModelMode, length=(5, 30), zone=(), starting_dir=None, poi=()):
        """
        Constructor.
        :param start_coordinates: starting coordinates
        :param mode: the MobilityModelMode of the MobilityModel
        :param length: the length of a route as interval, e.g. for Random_Walk
        :param zone: the zone as square with 4 values: top-left x, top-left y, bottom-right x, bottom-right y
        :param starting_dir: initial direction
        """
        start_x, start_y, _ = start_coordinates
        if mode == MobilityModelMode.Random_Mode:
            mode = random.choice(list(MobilityModelMode)[:-1])
        if mode == MobilityModelMode.Zonal:
            self.min_x = zone[0]
            self.min_y = zone[1]
            self.max_x = zone[2]
            self.max_y = zone[3]
        else:
            self.min_x = start_x - length[1]
            self.min_y = start_y - length[1]
            self.max_x = start_x + length[1]
            self.max_y = start_y + length[1]
        self.mode = mode
        self.steps = 0
        self.min_length = length[0]
        self.max_length = length[1]
        if mode == MobilityModelMode.Random:
            self.starting_dir = self.random_direction()
        else:
            self.starting_dir = starting_dir
        self.route_length = random.randint(self.min_length, self.max_length)
        self.return_dir = self.opposite_direction(self.starting_dir)
        self.current_dir = self.starting_dir
        self.previous_coordinates = start_coordinates
        self.poi = poi

    def set(self, particle):
        """
        Sets the mobility_model attribute of :param particle:.
        :param particle: the particle the MobilityModel as attribute to.
        """
        setattr(particle, "mobility_model", self)

    def set_mode(self, mode: MobilityModelMode):
        """
        Sets the MobilityModelMode. If Manual then sets current_dir to None.
        :param mode: the mode to set to
        :type mode: MobilityModelMode
        :return: None
        """
        self.mode = mode
        if mode == MobilityModelMode.Manual:
            self.current_dir = None

    def next_direction(self, current_x_y_z):
        """
        Determines the next direction of the model.
        :param current_x_y_z: the current x, y and z coordinates of the particle as tuple
        :return: the next direction
        """
        self.previous_coordinates = current_x_y_z
        if self.mode == MobilityModelMode.Back_And_Forth:
            return self.__back_and_forth__()
        elif self.mode == MobilityModelMode.Random_Walk:
            return self.__random_walk__()
        elif self.mode == MobilityModelMode.Circle:
            return self.__circle__()
        elif self.mode == MobilityModelMode.Random:
            return self.__random__()
        elif self.mode == MobilityModelMode.Static:
            return False
        elif self.mode == MobilityModelMode.Zonal:
            return self.__zonal__(current_x_y_z)
        elif self.mode == MobilityModelMode.POI:
            return self.__poi__(current_x_y_z)
        elif self.mode == MobilityModelMode.Manual:
            return self.current_dir

    def __random__(self):
        """
        The next direction in random mode.
        :return: next direction
        """
        self.current_dir = MobilityModel.random_direction()
        return self.current_dir

    def __circle__(self):
        """
        The next direction in circle mode.
        :return: next direction
        """
        if self.steps < self.route_length:
            self.steps += 1
        else:
            if self.current_dir == self.NE:
                self.current_dir = self.NW
            elif self.current_dir == self.NW:
                self.current_dir = self.W
            elif self.current_dir == self.W:
                self.current_dir = self.SW
            elif self.current_dir == self.SW:
                self.current_dir = self.SE
            elif self.current_dir == self.SE:
                self.current_dir = self.E
            elif self.current_dir == self.E:
                self.current_dir = self.NE
            self.steps = 1
            # new circle if we walked a full circle
            if self.current_dir == self.starting_dir:
                self.route_length = random.randint(1, self.max_length)
                self.starting_dir = MobilityModel.random_direction()
                self.current_dir = self.starting_dir
        return self.current_dir

    def __random_walk__(self):
        """
        The next direction in random walk mode.
        :return: next direction
        """
        if self.steps < self.route_length:
            self.steps += 1
            return self.current_dir
        else:
            self.steps = 1
            self.route_length = random.randint(1, self.max_length)
            return self.__random__()

    def __back_and_forth__(self):
        """
        The next direction in back and forth mode.
        :return: next direction
        """
        if 0 <= self.steps < self.route_length:
            self.steps += 1
            return self.starting_dir
        elif self.steps == self.route_length:
            self.steps = -1
            return self.return_dir
        elif self.steps == -self.route_length:
            self.steps = 1
            return self.starting_dir
        else:
            self.steps -= 1
            return self.return_dir

    def __zonal__(self, current_x_y_z):
        """
        The next direction in zonal mode.
        :return: next direction
        """
        (x, y, z) = current_x_y_z
        # check if at min_x then head anywhere but west

        directions = {self.W,
                      self.SW,
                      self.NW,
                      self.E,
                      self.SE,
                      self.NE}

        if self.min_x >= x:
            directions = directions.difference({self.W, self.SW, self.NW})
        if self.max_x <= x:
            directions = directions.difference({self.E, self.SE, self.NE})
        if self.min_y >= y:
            directions = directions.difference({self.SE, self.SW})
        if self.max_y <= y:
            directions = directions.difference({self.NE, self.NW})

        next_dir = MobilityModel.random_direction(list(directions))
        return next_dir

    def __poi__(self, current_x_y_z):
        if current_x_y_z == self.poi or (current_x_y_z == self.previous_coordinates and self.current_dir is not None):
            return False

        # southern movement
        if current_x_y_z[1] > self.poi[1]:
            # western movement
            if current_x_y_z[0] > self.poi[0]:
                return self.SW
            # eastern movement
            elif current_x_y_z[0] < self.poi[0]:
                return self.SE
        # northern movement
        elif current_x_y_z[1] < self.poi[1]:
            # western movement
            if current_x_y_z[0] > self.poi[0]:
                return self.NW
            # eastern movement
            elif current_x_y_z[0] < self.poi[0]:
                return self.NE

        if current_x_y_z[0] < self.poi[0]:
            return self.E
        else:
            return self.W

    @staticmethod
    def random_direction(directions=None):
        """
        A random direction from list :param directions:.
        :param directions: a list of directions.
        :return: a random next direction in directions, or complete random
        """
        if directions is None:
            directions = MobilityModel.directions
        return random.choice(directions)

    @staticmethod
    def opposite_direction(direction):
        """
        Returns the direction opposite to :param direction or None if :param direction
        is not a valid direction
        :param direction: the starting direction
        :return: the return direction or none
        """
        if direction == MobilityModel.NE:
            return MobilityModel.SW
        elif direction == MobilityModel.E:
            return MobilityModel.W
        elif direction == MobilityModel.SE:
            return MobilityModel.NW
        elif direction == MobilityModel.SW:
            return MobilityModel.NE
        elif direction == MobilityModel.W:
            return MobilityModel.E
        elif direction == MobilityModel.NW:
            return MobilityModel.SE
        else:
            return None
