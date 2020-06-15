import math
import random
from enum import Enum

from lib.swarm_sim_header import get_coordinates_in_direction, get_distance_from_coordinates, \
    get_surrounding_coordinates


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
    DisperseFlock = 8
    Random_Mode = 9


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

    def __init__(self, start_coordinates, mode: MobilityModelMode, length=15, zone=(), starting_dir=None, poi=()):
        """
        Constructor.
        :param start_coordinates: starting coordinates
        :param mode: the MobilityModelMode of the MobilityModel
        :param length: the length of a route as interval, e.g. for Random_Walk
        :param zone: the zone as square with 4 values: top-left x, top-left y, bottom-right x, bottom-right y
        :param starting_dir: initial direction
        :param poi: Point of Interest to navigate to in Mode POI
        """
        start_x, start_y, _ = start_coordinates
        if mode == MobilityModelMode.Random_Mode:
            mode = random.choice(list(MobilityModelMode)[:-1])
        if mode == MobilityModelMode.Zonal:
            self.min_x = zone[0]
            self.min_y = zone[1]
            self.max_x = zone[2]
            self.max_y = zone[3]
        self.mode = mode
        self.steps = 0
        if mode == MobilityModelMode.Random:
            self.starting_dir = self.random_direction()
        else:
            self.starting_dir = starting_dir
        if isinstance(length, tuple):
            self.route_length = random.randint(length[0], length[1])
            self.max_length = length[1]
        elif isinstance(length, int):
            self.route_length = length
            self.max_length = length
        self.return_dir = self.opposite_direction(self.starting_dir)
        self.current_dir = self.starting_dir
        self.previous_coordinates = start_coordinates
        self.poi = poi
        self._distance_to_poi = math.inf
        self._distance_to_poi_unimproved_rounds = 0
        self.direction_history = []
        self._direction_history_index = None

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
        if mode == self.mode:
            return
        self.mode = mode
        if mode == MobilityModelMode.Random_Mode:
            self.mode = random.choice(list(MobilityModelMode)[:-1])
        if mode == MobilityModelMode.Manual:
            self.current_dir = None
        elif mode == MobilityModelMode.Random or mode == MobilityModelMode.Random_Walk:
            self.current_dir = self.random_direction()
        elif mode == MobilityModelMode.DisperseFlock:
            self.steps = 0
        elif mode == MobilityModelMode.POI:
            self._distance_to_poi = math.inf
            self._distance_to_poi_unimproved_rounds = 0
            self.direction_history = []

    def next_direction(self, current_x_y_z, blocked_neighbors=None):
        """
        Determines the next direction of the model.
        :param current_x_y_z: the current x, y and z coordinates of the particle as tuple
        :param blocked_neighbors: blocked neighbor locations
        :return: the next direction
        """
        if self.mode == MobilityModelMode.Back_And_Forth:
            new_direction = self.__back_and_forth__()
        elif self.mode == MobilityModelMode.Random_Walk:
            new_direction = self.__random_walk__()
        elif self.mode == MobilityModelMode.Circle:
            new_direction = self.__circle__()
        elif self.mode == MobilityModelMode.Random:
            new_direction = self.__random__()
        elif self.mode == MobilityModelMode.Static:
            new_direction = False
        elif self.mode == MobilityModelMode.Zonal:
            new_direction = self.__zonal__(current_x_y_z)
        elif self.mode == MobilityModelMode.POI:
            new_direction = self.__poi__(current_x_y_z, blocked_neighbors)
        elif self.mode == MobilityModelMode.Manual:
            new_direction = self.current_dir
        elif self.mode == MobilityModelMode.DisperseFlock:
            new_direction = self.__disperse_flock__(current_x_y_z)
        else:
            new_direction = None
        self.current_dir = new_direction
        self.previous_coordinates = current_x_y_z
        return new_direction

    def turn_around(self):
        """
        Turn the mobility model in the opposite direction.
        :return: None
        """
        self.current_dir = self.opposite_direction(self.current_dir)

    def track_back(self):
        """
        Tracks back the list of directions traced with the model. Will raise an IndexError if there's nothing to
        track back.
        :return: the next traceback direction
        """
        if self._direction_history_index is None:
            self._direction_history_index = len(self.direction_history) - 1
        if self._direction_history_index < 0:
            self.set_mode(MobilityModelMode.Manual)
            return None
        next_direction = self.opposite_direction(self.direction_history[self._direction_history_index])
        self._direction_history_index -= 1
        return next_direction

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

    def __poi__(self, current_x_y_z, blocked_neighbors=None):
        """
        Moves the particle to a Point of Interest, i.e. a location, step by step.
        :param current_x_y_z: the particle's current location
        :param blocked_neighbors: blocked neighbor locations
        :return: the next direction to move to, if possible
        """
        if current_x_y_z == self.poi:
            return None
        # assume that the blocking neighbors will continue to block the path
        if blocked_neighbors and self.previous_coordinates == current_x_y_z and len(self.direction_history) > 0:
            preferred_direction = self.__poi__(current_x_y_z)
            new_coordinates = get_coordinates_in_direction(current_x_y_z, preferred_direction)
            if new_coordinates not in blocked_neighbors:
                return preferred_direction
            new_direction = self.__get_preferred_directions__(blocked_neighbors, current_x_y_z)
        else:
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
        return None if new_direction is None else self.__check_new_coordinates_(new_direction)

    def __get_preferred_directions__(self, blocked_neighbors, current_x_y_z):
        new_direction = None
        neighbor_count = -1
        for direction in self.directions:
            new_coordinates = get_coordinates_in_direction(current_x_y_z, direction)
            if new_coordinates not in blocked_neighbors:
                distance_to_poi = get_distance_from_coordinates(self.poi, new_coordinates)
                new_neighbor_count = self.__get_number_of_neighbors__(new_coordinates, blocked_neighbors)
                if distance_to_poi <= self._distance_to_poi and new_neighbor_count > neighbor_count:
                    new_direction = direction
                    neighbor_count = new_neighbor_count
        return new_direction

    @staticmethod
    def __get_number_of_neighbors__(new_coordinates, blocked_neighbors):
        surroundings = get_surrounding_coordinates(new_coordinates)
        return len([_ for _ in surroundings if _ in blocked_neighbors])

    def __check_new_coordinates_(self, new_direction):
        if 6 <= self._distance_to_poi_unimproved_rounds <= 12:
            return random.choices([new_direction, None], [1 / 6, 5 / 6], k=1)[0]
        elif self._distance_to_poi_unimproved_rounds >= 12:
            weight = 1 / self._distance_to_poi_unimproved_rounds
            return random.choices([new_direction, None], [weight, 1 - weight], k=1)[0]
        else:
            return new_direction

    def __disperse_flock__(self, current_x_y_z):
        if self.steps < self.route_length:
            self.steps += 1
            return self.current_dir
        elif self.steps < self.max_length:
            self.steps += 1
            return None
        else:
            self.mode = MobilityModelMode.Manual
            return None

    def update_history(self, coordinates):
        self.direction_history.append(self.current_dir)
        if self.mode == MobilityModelMode.POI:
            distance_to_poi = get_distance_from_coordinates(self.poi, coordinates)
            if distance_to_poi >= self._distance_to_poi:
                self._distance_to_poi_unimproved_rounds += 1
            else:
                self._distance_to_poi_unimproved_rounds = 0
            self._distance_to_poi = distance_to_poi

    @staticmethod
    def random_direction(directions=None, exclude=None):
        """
        A random direction from list :param directions:.
        :param directions: a list of directions.
        :param exclude: a list of directions to exclude
        :return: a random next direction in directions, or complete random
        """
        if directions is None:
            directions = MobilityModel.directions
        if exclude is not None:
            directions = [direction for direction in directions if direction not in exclude]
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
