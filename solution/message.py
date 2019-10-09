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