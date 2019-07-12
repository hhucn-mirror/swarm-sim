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
            sp(sim, particle, particle.tile)

def sp(sim, particle, tile):
    next_dir = -1
    #particle.create_location()
    p_x = particle.coords[0]
    p_y = particle.coords[1]
    t_x = tile.coords[0]
    t_y = tile.coords[1]
    if (p_x-t_x == p_y-t_y):
        if p_y < t_y and  p_x < t_x:
            next_dir = NE
        elif p_y < t_y and p_x > t_x:
            next_dir = NW
        elif p_y > t_y and p_x < t_x:
            next_dir = SE
        elif p_y > t_y and p_x > t_x:
            next_dir = SW
    elif p_y == 0:
        if p_x > t_x:
            next_dir = W
        elif p_x < t_x:
            next_dir = E
    elif p_x == 0:
        if p_y < t_y:
            next_dir = NE
        else:
            next_dir = SW
    else:
        if p_y < t_y and p_x < t_x:
            next_dir = NE
        elif p_y < t_y and p_x > t_x:
            next_dir = NW
        elif p_y > t_y and p_x < t_x:
            next_dir = SE
        elif p_y > t_y and p_x > t_x:
            next_dir = SW

    if particle.tile_in(next_dir) or particle.particle_in(next_dir):
        pass
    else:
        particle.move_to(next_dir)
