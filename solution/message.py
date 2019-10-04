from copy import deepcopy


class OwnDist:
    def __init__(self, own_dist, own_id):
        self.own_dist = own_dist
        self.own_id = own_id
        self.id =  id

    def __str__(self):
        return "id: " + str(self.own_id) + " | dist: " + str(self.own_dist)


class PMax(OwnDist):
    def __init__(self, own_dist, own_id, p_max, p_max_table):
        OwnDist.__init__(self, own_dist, own_id)
        self.p_max_id = p_max.id
        self.p_max_dist = p_max.dist
        self.p_max_dir = 0
        self.p_max_table = deepcopy(p_max_table)

    def __str__(self):
        return OwnDist.__str__(self) + " | max_id: " + str(self.p_max_id) + " | max_dist: " +\
               str(self.p_max_dist) + " | max_dir: " + str(self.p_max_dir)