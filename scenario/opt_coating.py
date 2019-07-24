from solution.std_lib import *

def move_between_tiles(particle):
    for dir in particle.fl_dir_list:
        if particle.nh_dict[dir].type == "p" and particle.nh_dict[get_the_invert(dir)].type == "fl"  :
            return get_the_invert(dir)
        elif particle.nh_dict[dir].type == "fl" and particle.nh_dict[get_the_invert(dir + 3)].type == "fl" \
        and dir != particle.prev_dir and not particle.particle_in(dir) and not particle.tile_in(dir):
            return dir
        elif not particle.particle_in(get_the_invert(dir)) and not particle.tile_in(get_the_invert(dir)) \
        and not particle.tile_in(dir):
            return get_the_invert(dir)
    return False

def opt_coating(particle):
    if len(particle.t_dir_list) > 3:
        # Optimization movementen between tiles
        if len(particle.t_dir_list) == 4:
            return move_between_tiles(particle)