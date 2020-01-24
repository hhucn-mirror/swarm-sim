import math


def end_sim(sim):
    if goal_reached(sim):
        sim.set_successful_end()
        if sim.config_data.visualization:
            print("successful end reached after round:", sim.get_actual_round())


def goal_reached(sim):
    min_fl_distance = min(list(map(get_smallest_fl, sim.particles)), default=0)
    max_particle_distance = max([particle.own_dist for particle in sim.particles], default=math.inf)
    if min_fl_distance is math.inf or min_fl_distance < max_particle_distance:
        return False
    else:
        return True


def get_smallest_fl(particle):
    return min([neighbor.dist for neighbor in particle.nh_list if neighbor.type == "fl"], default=math.inf)
