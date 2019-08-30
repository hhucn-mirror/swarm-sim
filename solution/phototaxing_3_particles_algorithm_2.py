import logging
import random
from solution.utils import *
from solution.goal_params import check_all_goal_params

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):
    check_all_goal_params(sim)

    for particle in sim.get_particle_list():
        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        param_lambda = sim.param_lambda
        param_delta = sim.param_delta
        if not sim.multiple:
            param_lambda = 6
            param_delta = -1

        # Scanning for the particles in the vicinity
        neighbor_list = particle.scan_for_particle_in(1)
        choices = []
        move_decr_edges = False



        # This begins the location detection algorithm
        # If there is only one neighbor, the particle may proceed similarly to the 2-particle algorithm
        if len(neighbor_list) == 1:
            nbdir = determine_direction_from_coords(particle.coords, neighbor_list[0].coords)
            choices.append((nbdir + 1) % 6)
            choices.append((nbdir - 1) % 6)
        # If there are two neighbors, the particle can be in three different states

        elif len(neighbor_list) == 2:
            # Calculating the directions of the neighbors
            nbdir = []
            nbdir.append(determine_direction_from_coords(particle.coords, neighbor_list[0].coords))
            nbdir.append(determine_direction_from_coords(particle.coords, neighbor_list[1].coords))

            # In this case, particle is in the middle of a line and can't move
            if(nbdir[0] % 3) != (nbdir[1] % 3):

                # Particle is part of a triangle and has two options to move to
                if(nbdir[0] + nbdir[1]) % 2 == 1:
                    # This is the only move which decreases edges in the system
                    move_decr_edges = True
                    # This is an edge case in which the regular algorithm fails
                    if (nbdir[0] == 5 and nbdir[1] == 0) or (nbdir[0] == 0 and nbdir[1] == 5):
                        choices.append(4)
                        choices.append(1)
                    elif nbdir[0] < nbdir[1]:
                        choices.append((nbdir[0] - 1) % 6)
                        choices.append((nbdir[1] + 1) % 6)
                    elif nbdir[1] < nbdir[0]:
                        choices.append((nbdir[0] + 1) % 6)
                        choices.append((nbdir[1] - 1) % 6)

                # The particle is part of a bent curve, which means there is only one location to move to
                elif (nbdir[0] + nbdir[1]) % 2 == 0:
                    # The following two are edge cases
                    nbsum = nbdir[0] + nbdir[1]
                    if (nbdir[0] == 4 or nbdir[1] == 4) and nbsum == 4:
                        choices.append(5)
                    elif (nbdir[0] == 5 or nbdir[1] == 5) and nbsum == 6:
                        choices.append(0)
                    else:
                        newdir = nbsum/2
                        choices.append(int(newdir))

        # The divisor is multiplied with this if the move decreases edges
        prob_divisor = 1
        # This calculates the move probability according to the ASU algorithm
        if move_decr_edges:
            prob_divisor = param_delta
        if particle.read_memory_with("light") is None:
            prob_divisor = prob_divisor * param_lambda
        choice = random.choice((0, 1))
        can_move = True

        # Scanning for goal tiles in the neighborhood and also checking whether particle can move on that spot
        # If a non goal tile occupies the space, the particle may not move
        # If a goal tile is in the 1-neighborhood, the simulation terminates successfully
        nb_tiles = particle.scan_for_tile_in(1)
        if nb_tiles is not None:
            for tile in nb_tiles:
                if len(choices)-1 >= choice and \
                    determine_direction_from_coords(particle.coords, tile.coords) == choices[choice]:
                    can_move = False

        if len(choices)-1 >= choice and can_move:
            if random.randint(0, prob_divisor - 1) == 0:
                particle.move_to(choices[choice])
