import logging
import random
import numpy
import matplotlib.pylab as plt

"""
particle color = mode
black   (1) = search-mode
green   (4) = track-follow-mode
violet (7) = home-mode

marker color = status
black (1) = base
green (4) = track
"""
NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5
DIRECTIONS = [NE, E, SE, SW, W, NW]

search_mode_color = 1
track_follow_mode_color = 4
home_mode_color = 7
base_color = 1
track_color = 4
multi_layer_track_color = 9

global home
home = (0.0, 0.0)

# Particle respawn
def respawn(world):
    while len(world.get_particle_list()) <= 40:
        ant = world.add_particle(0, 0)
        setattr(ant, "list", [])


# Decrease lifespan of a track
def evaporation(marker):
    if (marker.get_color() == track_color):
        marker.set_alpha(marker.get_alpha() - 0.04)
    elif (marker.get_color() == multi_layer_track_color):
        marker.set_alpha(marker.get_alpha() - 0.04)


# Decrease particle lifespan
def life_span(particle):
    particle.set_alpha(particle.get_alpha() - 0.01)


# Get all surrounding pheromones and make a dictionary
def get_track(particle):
    pheromone_dict = {}
    for dir in DIRECTIONS:
        #print("test:", particle.get_marker_in(dir).get_color())
        if (particle.marker_in(dir) == True and particle.get_marker_in(dir).get_color() != base_color):
            pheromone_dict.update(
                {dir: [particle.get_marker_in(dir).layer]})
        if (particle.list != None):
            pheromone_dict.pop(particle.list[-1], None)
    return pheromone_dict


def compare_pheromones(pheromones_dict):
    # If the dictionary is empty go in a random direction
    if (len(pheromones_dict) == 0):
        return random.choice(DIRECTIONS)
    else:
        # Filter all entries which have max layer
        max_layer = max([value[0] for direction, value in pheromones_dict.items()])
        # Filter all directions which have max layer
        resulting_directions  = [direction for direction, value in pheromones_dict.items() if value[0] == max_layer]
        return random.choice(resulting_directions)


# Go home the way you came
def go_home(particle):
    particle.move_to(particle.list[-1])
    del (particle.list[-1])


# Decrease stack of food
def food_stack(food, particle):
    if (particle.coords == food.coords):
        food.set_alpha(food.get_alpha() - 0.1)


# Invert dir
def invert_dir(dir):
    if dir >= 3:
        return dir - 3
    else:
        return dir + 3


# Making a plot
def plot(rounds, deads):
    plt.plot(rounds, deads)
    plt.xlabel("rounds")
    plt.ylabel("dead ants")
    # plt.title("Rounds: ", str(rounds[-1]), "Deads:", str(deads[-1]))
    plt.show()


# Start
###########################################################################################################################################################################

rounds = []
deads = []


def solution(world):
    global dead_count

    if (world.get_actual_round() == 1):
        dead_count = 0

    respawn(world)
    rounds.append(world.get_actual_round())
    deads.append(dead_count)

    for marker in world.get_marker_list():

        evaporation(marker)

        # Delete track
        if (marker.get_alpha() == 0):
            world.remove_marker(marker.get_id())

    for particle in world.get_particle_list():

        life_span(particle)

        # Kill ant, when no life span
        if (particle.get_alpha() == 0):
            world.remove_particle(particle.get_id())
            dead_count += 1

        # Search for food
        if (particle.get_color() == search_mode_color):
            next_step = random.choice(DIRECTIONS)
            particle.move_to(next_step)
            # Save way home
            particle.list.append(invert_dir(next_step))

        # If found food, go in home-mode
        if (particle.check_on_tile() == True):
            particle.set_color(home_mode_color)
            # Reduce food stack, when take food
            for food in world.get_tiles_list():
                food_stack(food, particle)
                # Delete food when gone
                if (food.get_alpha() == 0):
                    world.remove_tile_on(food.coords)
            # Restore ant life span
            particle.set_alpha(1)

        # If in home-mode, go home and lay track
        if (particle.get_color() == home_mode_color):
            # Lay track
            if (particle.check_on_marker() == False):
                track = particle.create_marker(track_color)
                if (track != False):
                    setattr(track, 'layer', 0)
            else:
                current_marker = particle.get_marker()
                current_marker.set_color(multi_layer_track_color)
                current_marker.layer += 1
                # Reset track life span
                current_marker.set_alpha(1)

            # go home
            if (particle.list != []):
                go_home(particle)

        # If found track, follow
        if (particle.coords != home and particle.check_on_marker() == True and particle.get_color() != home_mode_color):
            particle.set_color(track_follow_mode_color)
            pheromone_to_follow = compare_pheromones(get_track(particle))
            particle.move_to(pheromone_to_follow)
            came_from = invert_dir(pheromone_to_follow)
            #print(came_from)
            particle.list.append(came_from)
            #print("test: ", particle.list[-1])

        # If home, go back in search-mode
        if (particle.coords == home):
            particle.set_color(search_mode_color)
            # Reset way home list
            particle.list = []
            # Restore ant life span
            particle.set_alpha(1)

        # If track die, go back in search-mode
        if (particle.get_color() == track_follow_mode_color and particle.check_on_marker() == False):
            particle.set_color(search_mode_color)

    # If all food is collected, success
    if (len(world.get_tiles_list()) == 0):
        world.success_termination()
        print("Rounds:", rounds[-1])
        print("Deads:", deads[-1])
        plot(rounds, deads)
