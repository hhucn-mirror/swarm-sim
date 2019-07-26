from copy import deepcopy
import math
from solution.std_lib import *

debug = 1


class DistInfo:
    def __init__(self, own_dist, own_id, p_max):
        self.own_dist = own_dist
        self.own_id = own_id
        if p_max:
            max_key = max(p_max, key=p_max.get)
            self.p_max_id = max_key
            self.p_max_dist = p_max[self.p_max_id]
            self.p_max_dir = 0
        else:
            self.p_max_id = None
            self.p_max_dist = -math.inf

class OwnInfo:
    def __init__(self, own_dist):
        self.own_dist = own_dist
# def __init__(self, own_dist, fl_min_dist, fl_hop, p_max_id, p_max_dist, p_hop):
# self.own_dist = own_dist
# self.fl_min_dist = fl_min_dist
# self.fl_min_hop = fl_hop
# self.p_max_dist = p_max_dist
# self.p_max_hop = p_hop
# self.p_max_id = p_max_id


def read_data(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = deepcopy(particle.read_whole_memory())
        particle.delete_whole_memeory()
        return True
    return False


def send_own_distance(particle):
    if particle.own_dist != math.inf:
        dist_package = OwnInfo(particle.own_dist)
        for dir in direction:
            neighbor_p = particle.get_particle_in(dir)
            if neighbor_p:
                if debug:
                    print("P", particle.number, "sends own distance", dist_package.own_dist,
                          " to", neighbor_p.number, " in dir", dir_to_str(dir))
                # invert the dir so the receiver particle knows from where direction it got the package
                particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(dist_package))
        return True


def send_data(particle):
    if particle.own_dist != math.inf:
        dist_package = DistInfo(particle.own_dist, particle.number, particle.p_max_table)
        for dir in direction:
            neighbor_p = particle.get_particle_in(dir)
            if neighbor_p and dir not in particle.p_max.black_list:
                if debug:
                    print("P", particle.number, "sends own distance", dist_package.own_dist,
                          " P Max ID:", dist_package.p_max_id, "Dist:", dist_package.p_max_dist,
                          " to P", neighbor_p.number, " in dir", dir_to_str(dir))
                # invert the dir so the receiver particle knows from where direction it got the package
                particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(dist_package))
        return True

        ##Zukunft checken particle is updated und dann infopackage schicken

        # package = InfoPackage (particle.own_dist, particle.gl_fl_min_dist, particle.gl_fl_min_hop,
        #                        particle.gl_p_max_id, particle.gl_p_max_dist, particle.gl_p_max_hop)
        # for dir in particle.nh_dict:
        #     neighbor_p = particle.get_particle_in(dir)
        #     if neighbor_p:
        #         if debug:
        #             print("P", particle.number, "sends Data to", neighbor_p.number, " in dir", dir_to_str(dir))
        #         # invert the dir so the receiver particle knows from where direction it got the package
        #         particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(package))
        #         return True
    return False