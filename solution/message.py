

class OwnDist:
    def __init__(self, own_dist, own_id):
        self.own_dist = own_dist
        self.own_id = own_id
        self.id =  id

class PMax(OwnDist):
    def __init__(self, own_dist, own_id, p_max):
        OwnDist.__init__(own_dist, own_id)
        max_key = max(p_max, key=p_max.get)
        self.p_max_id = max_key
        self.p_max_dist = p_max[self.p_max_id]
        self.p_max_dir = 0
