import logging
import random

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

tile = None
def solution (sim):
    global tile
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            setattr(particle, "tile", None)
            particle.tile = random.choice(sim.tiles)
        else:
            mv_one_step_closer_to(particle, tile)

def mv_one_step_closer_to(particle, tile):
    next_dir =get_next_dir_to(particle.coords[0], particle.coords[1],  tile.coords[0], tile.coords[1])

    if not particle.tile_in(next_dir) and not particle.particle_in(next_dir) and next_dir != -1:
        particle.move_to(next_dir)


def get_next_dir_to(src_x, src_y, dest_x, dest_y):
    next_dir = -1
    if (src_x < dest_x or src_x == dest_x) and src_y < dest_y:
        next_dir = NE
    elif src_y < dest_y and src_x > dest_x:
        next_dir = NW
    elif src_y > dest_y and src_x < dest_x:
        next_dir = SE
    elif (src_x > dest_x or src_x == dest_x) and src_y > dest_y :
        next_dir = SW
    elif src_y == dest_y and src_x > dest_x:
        next_dir = W
    elif src_y == dest_y and src_x < dest_x:
        next_dir = E
    return next_dir
