from copy import deepcopy
import math
from lib.swarm_sim_header import *

debug = 1


# def __init__(self, own_dist, fl_min_dist, fl_hop, p_max_id, p_max_dist, p_hop):
# self.own_dist = own_dist
# self.fl_min_dist = fl_min_dist
# self.fl_min_hop = fl_hop
# self.p_max_dist = p_max_dist
# self.p_max_hop = p_hop
# self.p_max_id = p_max_id


def read(memory):
    if memory():
        rcv_buf = deepcopy(memory())
        memory().clear()
        return rcv_buf
    return False


def send_own_distance(particle):
    if particle.own_dist != math.inf:
        dist_package = OwnInfo(particle.own_dist, particle.number)
        for dir in direction_list:
            neighbor_p = particle.get_particle_in(dir)
            if neighbor_p and particle.own_dist <= neighbor_p.own_dist :
                if debug:
                    print("P", particle.number, "sends own distance package", dist_package.own_dist,
                          " to", neighbor_p.number, " in dir", dir_to_str(dir))
                # invert the dir so the receiver particle knows from where direction it got the package
                particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(dist_package))
        return True
    return False


def send_to(rcver, dir, snd_buf, sender):
    if rcver and snd_buf:
        if debug:
            print("sends ", snd_buf,
                  "to P", rcver.number, " in dir", dir_to_str(dir))
        # invert the dir so the receiver particle knows from where direction it got the package
        sender.write_to_with(rcver, key=get_the_invert(dir), data=deepcopy(snd_buf))
        return True
    return False