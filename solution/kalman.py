from lib.std_lib import *


def coating(particle):
    if len(particle.t_dir_list) > 3:
        # Optimization movementen between tiles
        if len(particle.t_dir_list) == 4:
            return move_between_tiles(particle)
    elif particle.fl_dir_list is not None:
        return move_to_fl_dir(particle)
    return False


def move_between_tiles(particle):
    for dir in particle.fl_dir_list:
        if particle.nh_dict[dir].type == "p" and particle.nh_dict[get_the_invert(dir)].type == "fl" \
        and get_the_invert(dir) != particle.prev_dir :
            return get_the_invert(dir)
        elif particle.nh_dict[dir].type == "fl" and particle.nh_dict[get_the_invert(dir + 3)].type == "fl" \
        and dir != particle.prev_dir and not particle.particle_in(dir) and not particle.tile_in(dir):
            return dir
        elif not particle.particle_in(get_the_invert(dir)) and not particle.tile_in(get_the_invert(dir)) \
        and not particle.tile_in(dir):
            return get_the_invert(dir)
    return False


def move_to_fl_dir(particle):
    if particle.gl_p_max_dir != particle.own_dist and particle.gl_p_max_dir != -1:
        for fl_dir in particle.fl_dir_list:
            if particle.gl_p_max_dist > particle.nh_dict[fl_dir].dist and \
                    particle.particle_in (fl_dir) is False:
                return fl_dir
    elif particle.gl_fl_min_dist < particle.gl_p_max_dist and particle.particle_in (particle.gl_fl_min_dir) is False\
            and particle.tile_in (particle.gl_fl_min_dir) is False:
        return particle.gl_fl_min_dir
    return False
