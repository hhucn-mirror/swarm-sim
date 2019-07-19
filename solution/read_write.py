from copy import deepcopy
from lib.std_lib import get_the_invert



# class InfoPackage:
#     def __init__(self, own_dist, fl_min_dist, fl_hop):
#         self.own_dist = own_dist
#         self.fl_min_dist = fl_min_dist
#         self.fl_hop = fl_hop

class InfoPackage:
    def __init__(self, own_dist, fl_min_dist, fl_hop, p_max_dist, p_hop):
        self.own_dist = own_dist
        self.fl_min_dist = fl_min_dist
        self.fl_hop = fl_hop
        self.p_max_dist = p_max_dist
        self.p_hop = p_hop


# class InfoPackage:
#     def __init__(self, own_dist):
#         self.own_dist = own_dist

def read_data(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = deepcopy(particle.read_whole_memory())
        particle.delete_whole_memeory()
        return True
    return False


def send_data(particle):
    if particle.own_dist != 10000 and particle.p_dir_list:
        package = InfoPackage (particle.own_dist, particle.loc_fl_min_dist, particle.gl_fl_min_hop,
                               particle.loc_p_max_dist, particle.gl_p_max_hop)
        for dir in particle.p_dir_list:
            neighbor_p = particle.get_particle_in(dir)
            # invert the dir so the receiver particle knows from where direction it got the package
            particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(package))