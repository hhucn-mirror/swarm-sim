import logging
import random
from lib.tile import blue

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):
    success_round = -1

    for particle in sim.get_particle_list():
        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        # Scanning for the particles in the vicinity
        neighbor_list = particle.scan_for_particle_in(1)
        choices = []
        move_decr_edges = False

        # Those are divisors that will be used in a later calculation
        div_lambda = 1
        prob_divisor = 1

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
            if(nbdir[0] % 3) == (nbdir[1] % 3):
                print("Line: Can't move!")

            # Particle is part of a triangle and has two options to move to
            elif(nbdir[0] + nbdir[1]) % 2 == 1:
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

        # This calculates the move probability according to the ASU algoritm
        if move_decr_edges:
            prob_divisor = div_lambda
        if particle.read_memory_with("light") is None:
            prob_divisor = prob_divisor * 4
        choice = random.choice((0, 1))
        can_move = True

        # Scanning for goal tiles in the neighborhood and also checking whether particle can move on that spot
        # If a non goal tile occupies the space, the particle may not move
        # If a goal tile is in the 1-neighborhood, the simulations terminates successfully
        nb_tiles = particle.scan_for_tile_in(1)
        if nb_tiles is not None:
            for tile in nb_tiles:
                if tile.read_memory_with("goal-tile") is not None:
                    if success_round == -1:
                        success_round = sim.get_actual_round()
                        print("Success at: ", success_round)
                        sim.success_termination()
                elif len(choices)-1 >= choice and \
                        determine_direction_from_coords(particle.coords, tile.coords) == choices[choice]:
                    can_move = False

        if len(choices)-1 >= choice and can_move:
            if random.randint(1, prob_divisor) == 1:
                particle.move_to(choices[choice])


# Deletes all the light-entries in the particles to make a fresh start
def delete_light_information(sim):
    for particle in sim.get_particle_list():
        if particle.read_memory_with("light") is not None:
            particle.delete_memeory_with("light")


# Initializes the light propagation. Checks each tile for the light-emission entry and starts the algorithm
def init_full_light_propagation(sim):
    for tile in sim.get_tiles_list():
        dirval = tile.read_memory_with("light_emission")
        if dirval is not None:
            # print("SEARCHING: ", dirval)
            light_propagation(sim, tile.coords[0], tile.coords[1], dirval)


# Refer to light_emission_and_random_movement.py for documentation
def light_propagation(sim, x, y, dirval):

    if dirval == 0:
        y = y+2
    elif dirval == 1:
        x = x + 0.5
        y = y + 1
    elif dirval == 2:
        x = x + 1
    elif dirval == 3:
        x = x + 0.5
        y = y + 1
    elif dirval == 4:
        y = y - 2
    elif dirval == 5:
        x = x - 0.5
        y = y - 1
    elif dirval == 6:
        x = x + 1
    elif dirval == 7:
        x = x - 0.5
        y = y + 1

    coords = (x, y)

    tile_dict = sim.get_tile_map_coords()
    potential_tile = tile_dict.get(coords, None)

    particle_dict = sim.get_particle_map_coords()
    potential_particle = particle_dict.get(coords, None)

    if x < 15:
        if potential_tile is None and potential_particle is None:
            light_propagation(sim, x, y, dirval)
        elif potential_particle is not None:
            # print("found")
            potential_particle.write_memory_with("light", 1)


# Refer to phototaxing_2_particles_algorithm.py for documentation
def determine_direction_from_coords(coords_a, coords_b):
    delta_x = coords_a[0] - coords_b[0]
    delta_y = coords_a[1] - coords_b[1]

    if delta_x == 0 and delta_y == 0:
        return -1
    elif delta_x == -0.5 and delta_y == -1:
        return 0
    elif delta_x == -1 and delta_y == 0:
        return 1
    elif delta_x == -0.5 and delta_y == 1:
        return 2
    elif delta_x == 0.5 and delta_y == 1:
        return 3
    elif delta_x == 1 and delta_y == 0:
        return 4
    elif delta_x == 0.5 and delta_y == -1:
        return 5
    else:
        return -1


# Refer to phototaxing_2_particles_algorithm.py for documentation
def determine_coords_from_direction(coords, dirval):
    coords_new = (coords[0], coords[1])
    x = coords[0]
    y = coords[1]

    if dirval == 0:
        coords_new = (x + 0.5, y + 1)
    elif dirval == 1:
        coords_new = (x+1, y)
    elif dirval == 2:
        coords_new = (x + 0.5, y - 1)
    elif dirval == 3:
        coords_new = (x - 0.5, y - 1)
    elif dirval == 4:
        coords_new = (x - 1, y)
    elif dirval == 5:
        coords_new = (x - 0.5, y + 1)
    return coords_new
