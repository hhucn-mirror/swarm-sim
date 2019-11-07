import math
from copy import deepcopy


class OwnDistance:
    def __init__(self, particle_distance, particle_id):
        self.particle_distance = particle_distance
        self.particle_id = particle_id

    def __str__(self):
        return "id: " + str(self.particle_id) + " | dist: " + str(self.particle_distance)


class PMax(OwnDistance):
    def __init__(self, particle_distance, particle_id, p_max, p_max_table):
        OwnDistance.__init__(self, particle_distance, particle_id)
        self.p_max_ids = p_max.ids
        self.p_max_dist = p_max.dist
        self.p_max_dir = 0
        self.p_max_table = deepcopy(p_max_table)

    def __str__(self):
        return OwnDistance.__str__(self) + " | max_id: " + str(self.p_max_id) + " | max_dist: " + \
               str(self.p_max_dist) + " | max_dir: " + str(self.p_max_dir)


class Neighbor:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return str(self.type) + " | " + str(self.dist)


class PMaxInfo:
    def __init__(self):
        self.ids = set()
        self.dist = -math.inf
        self.directions = []
        self.black_list = []

    def __str__(self):
        return "id: " + str(self.ids) + "|" + "dist: " + str(self.dist) + "|" + "direction: " + str(self.directions) \
               + "|" + "Blacklist: " + str(self.black_list)[1:-1]

    def __eq__(self, other):
        return self.dist == other.dist and any(self_id in other.ids for self_id in self.ids)

    def reset(self):
        self.ids = set()
        self.dist = -math.inf
        self.directions = []
        self.black_list.clear()