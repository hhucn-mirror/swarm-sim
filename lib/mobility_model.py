import random
from enum import Enum

from lib.directions import Directions


class Mode(Enum):
    Random_Walk = 0,
    Back_And_Forth = 1,
    Circle = 2,
    Random = 3,
    Static = 4,
    Random_Mode = 5


class MobilityModel:

    def __init__(self, start_x, start_y, mode: Mode, length: (int, int)):
        if mode == Mode.Random_Mode:
            mode = random.choice(list(Mode)[:-1])
        self.mode = mode
        self.steps = 0
        self.min_length = length[0]
        self.max_length = length[1]
        self.starting_dir = self.random_direction()
        self.route_length = random.randint(self.min_length, self.max_length)
        self.return_dir = self.__return_direction()
        self.current_dir = self.starting_dir
        self.min_x = start_x - length[1]
        self.min_y = start_y - length[1]
        self.max_x = start_x + length[1]
        self.max_y = start_y + length[1]

    def set(self, particle):
        setattr(particle, "mobility_model", self)

    def __return_direction(self):
        return self.starting_dir - 3 if self.starting_dir > 2 else self.starting_dir + 3
    
    def next_direction(self):
        if self.mode == Mode.Back_And_Forth:
            return self.__back_and_forth__()
        elif self.mode == Mode.Random_Walk:
            return self.__random_walk__()
        elif self.mode == Mode.Circle:
            return self.__circle__()
        elif self.mode == Mode.Random:
            return self.__random__()
        elif self.mode == Mode.Static:
            return Directions.S.value

    def __random__(self):
        self.current_dir = MobilityModel.random_direction()
        return self.current_dir

    def __circle__(self):
        if self.steps < self.route_length:
            self.steps += 1
        else:
            if self.current_dir == Directions.NE.value:
                self.current_dir = Directions.NW.value
            elif self.current_dir == Directions.NW.value:
                self.current_dir = Directions.W.value
            elif self.current_dir == Directions.W.value:
                self.current_dir = Directions.SW.value
            elif self.current_dir == Directions.SW.value:
                self.current_dir = Directions.SE.value
            elif self.current_dir == Directions.SE.value:
                self.current_dir = Directions.E.value
            elif self.current_dir == Directions.E.value:
                self.current_dir = Directions.NE.value
            self.steps = 1
            # new circle if we walked a full circle
            if self.current_dir == self.starting_dir:
                self.route_length = random.randint(1, self.max_length)
                self.starting_dir = MobilityModel.random_direction()
                self.current_dir = self.starting_dir
        return self.current_dir

    def __random_walk__(self):
        if self.steps < self.route_length:
            self.steps += 1
            return self.current_dir
        else:
            self.steps = 1
            self.route_length = random.randint(1, self.max_length)
            return self.__random__()

    def __back_and_forth__(self):
        if 0 < self.steps < self.route_length:
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

    @staticmethod
    def random_direction():
        return random.choice(list(Directions)[:-1]).value
