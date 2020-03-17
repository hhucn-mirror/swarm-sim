import math
from copy import deepcopy


class OwnDistance:
    def __init__(self, particle_distance, particle_id):
        """
        A message package, which contains information about the distance of the sender to the next tile.
        :param particle_distance: distance of the sender to the next tile
        :param particle_id: id of the sender particle
        """
        self.particle_distance = particle_distance
        self.particle_id = particle_id

    def __str__(self):
        return "id: " + str(self.particle_id) + " | dist: " + str(self.particle_distance)


class PMax(OwnDistance):
    def __init__(self, particle_distance, particle_id, p_max, p_max_table):
        """
        In addition to the information in OwnDistance this package contains information about the maximum particle distance
        known to this particle.
        :param particle_distance: distance of the sender to the next tile
        :param particle_id: id of the sender particle
        :param p_max: maximum distance of a particle known to this particle
        :param p_max_table: currently unused
        """
        OwnDistance.__init__(self, particle_distance, particle_id)
        self.p_max_ids = deepcopy(p_max.ids)
        self.p_max_dist = p_max.dist
        self.p_max_dir = 0
        self.p_max_table = deepcopy(p_max_table)
        self.p_max_lifetime = p_max.lifetime

    def __str__(self):
        return OwnDistance.__str__(self) + " | max_id: " + str(self.p_max_id) + " | max_dist: " + \
               str(self.p_max_dist) + " | max_dir: " + str(self.p_max_dir)


class Neighbor:
    def __init__(self, type, dist):
        """
        A type storing the type and calculated distance for a neighbor of a particle
        :param type: type of the neighbor (fl, p, t)
        :param dist: calculated distance of the neighbor to the next tile
        """
        self.type = type
        self.dist = dist

    def __str__(self):
        return str(self.type) + " | " + str(self.dist)

    def __repr__(self):
        return str(self)


class PMaxInfo:
    def __init__(self):
        """
        A type for organizing information about the current p_max.
        ids: all particle ids that are believed to have the maximum distance
        dist: maximum particle distance known to this particle
        directions: all directions from where this particle received messages with the current PMax
        black_list: unused
        """
        self.ids = set()
        self.dist = -math.inf
        self.directions = []
        self.black_list = []
        self.lifetime = 0

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
        self.lifetime = 0


class TargetTileInfo:
    def __init__(self, target):
        self.target = target

    def __str__(self):
        return str(self.target)