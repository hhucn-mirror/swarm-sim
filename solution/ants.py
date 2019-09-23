import logging
import random
import numpy
import matplotlib.pylab as plt
"""
partical color = mode
black   (1) = search-mode
green   (4) = track-follow-mode
violett (7) = home-mode

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

direction = [NE, E, SE, SW, W, NW]

search_mode = 1
track_follow_mode = 4
home_mode = 7
base = 1
track = 4

global home
home = [0, 0]

# Walk towards target coordinates
def walk(target_co, particle):
    if (particle.coords[0] < target_co[0] and particle.coords[1] < target_co[1]):
        go_to = 0  # [NE]
    elif (particle.coords[0] < target_co[0] and particle.coords[1] > target_co[1]):
        go_to = 2  # [SE]
    elif (particle.coords[0] < target_co[0] and particle.coords[1] == target_co[1]):
        go_to = 1  # [E]
    elif (particle.coords[0] > target_co[0] and particle.coords[1] < target_co[1]):
        go_to = 5  # [NW]
    elif (particle.coords[0] > target_co[0] and particle.coords[1] > target_co[1]):
        go_to = 3  # [SW]
    else:  # (particle.coords[0] > target_co[0] and particle.coords[1] == target_co[1])
        go_to = 4  # [W]
    return go_to
"""
# Get dir for way home
def way_home(last_pos, particle):
    if (particle.coords[0] < last_pos[0] and particle.coords[1] < last_pos[1]):
        go_to = 0  # [NE]
    elif (particle.coords[0] < last_pos[0] and particle.coords[1] > last_pos[1]):
        go_to = 2  # [SE]
    elif (particle.coords[0] < last_pos[0] and particle.coords[1] == last_pos[1]):
        go_to = 1  # [E]
    elif (particle.coords[0] > last_pos[0] and particle.coords[1] < last_pos[1]):
        go_to = 5  # [NW]
    elif (particle.coords[0] > last_pos[0] and particle.coords[1] > last_pos[1]):
        go_to = 3  # [SW]
    else:  # (particle.coords[0] > target_co[0] and particle.coords[1] == target_co[1])
        go_to = 4  # [W]
    particle.list.append(go_to)
"""
# Follow track
def follow(next_step, particle):
    if (next_step != None):
        if (len(next_step) == 2):
            if (next_step[0].get_alpha() < next_step[1].get_alpha()):
                return next_step[0].coords
            elif (next_step[1].get_alpha() < next_step[0].get_alpha()):
                return next_step[1].coords
            else:
                particle.move_to(random.choice(direction))
                return particle.coords
        elif (len(next_step) == 3):
            if (next_step[0].get_alpha() < next_step[1].get_alpha() and
                next_step[0].get_alpha() < next_step[2].get_alpha()):
                return next_step[0].coords
            elif (next_step[1].get_alpha() < next_step[0].get_alpha() and
                  next_step[1].get_alpha() < next_step[2].get_alpha()):
                return next_step[1].coords
            elif (next_step[2].get_alpha() < next_step[0].get_alpha() and
                  next_step[2].get_alpha() < next_step[1].get_alpha()):
                return next_step[2].coords
            else:
                particle.move_to(random.choice(direction))
                return particle.coords
        elif (len(next_step) == 4):
            if (next_step[0].get_alpha() < next_step[1].get_alpha() and
                next_step[0].get_alpha() < next_step[2].get_alpha() and
                next_step[0].get_alpha() < next_step[3].get_alpha()):
                return next_step[0].coords
            elif (next_step[1].get_alpha() < next_step[0].get_alpha() and
                  next_step[1].get_alpha() < next_step[2].get_alpha() and
                  next_step[1].get_alpha() < next_step[3].get_alpha()):
                return next_step[1].coords
            elif (next_step[2].get_alpha() < next_step[0].get_alpha() and
                  next_step[2].get_alpha() < next_step[1].get_alpha() and
                  next_step[2].get_alpha() < next_step[3].get_alpha()):
                return next_step[2].coords
            elif (next_step[3].get_alpha() < next_step[0].get_alpha() and
                  next_step[3].get_alpha() < next_step[1].get_alpha() and
                  next_step[3].get_alpha() < next_step[2].get_alpha()):
                return next_step[3].coords
            else:
                particle.move_to(random.choice(direction))
                return particle.coords
        elif (len(next_step) == 5):
            if (next_step[0].get_alpha() < next_step[1].get_alpha() and
                next_step[0].get_alpha() < next_step[2].get_alpha() and
                next_step[0].get_alpha() < next_step[3].get_alpha() and
                next_step[0].get_alpha() < next_step[4].get_alpha()):
                return next_step[0].coords
            elif (next_step[1].get_alpha() < next_step[0].get_alpha() and
                  next_step[1].get_alpha() < next_step[2].get_alpha() and
                  next_step[1].get_alpha() < next_step[3].get_alpha() and
                  next_step[1].get_alpha() < next_step[4].get_alpha()):
                return next_step[1].coords
            elif (next_step[2].get_alpha() < next_step[0].get_alpha() and
                  next_step[2].get_alpha() < next_step[1].get_alpha() and
                  next_step[2].get_alpha() < next_step[3].get_alpha() and
                  next_step[2].get_alpha() < next_step[4].get_alpha()):
                return next_step[2].coords
            elif (next_step[3].get_alpha() < next_step[0].get_alpha() and
                  next_step[3].get_alpha() < next_step[1].get_alpha() and
                  next_step[3].get_alpha() < next_step[2].get_alpha() and
                  next_step[3].get_alpha() < next_step[4].get_alpha()):
                return next_step[3].coords
            elif (next_step[4].get_alpha() < next_step[0].get_alpha() and
                  next_step[4].get_alpha() < next_step[1].get_alpha() and
                  next_step[4].get_alpha() < next_step[2].get_alpha() and
                  next_step[4].get_alpha() < next_step[3].get_alpha()):
                return next_step[4].coords
            else:
                particle.move_to(random.choice(direction))
                return particle.coords
        elif (len(next_step) == 6):
            if (next_step[0].get_alpha() < next_step[1].get_alpha() and
                next_step[0].get_alpha() < next_step[2].get_alpha() and
                next_step[0].get_alpha() < next_step[3].get_alpha() and
                next_step[0].get_alpha() < next_step[4].get_alpha() and
                next_step[0].get_alpha() < next_step[5].get_alpha()):
                return next_step[0].coords
            elif (next_step[1].get_alpha() < next_step[0].get_alpha() and
                  next_step[1].get_alpha() < next_step[2].get_alpha() and
                  next_step[1].get_alpha() < next_step[3].get_alpha() and
                  next_step[1].get_alpha() < next_step[4].get_alpha() and
                  next_step[1].get_alpha() < next_step[5].get_alpha()):
                return next_step[1].coords
            elif (next_step[2].get_alpha() < next_step[0].get_alpha() and
                  next_step[2].get_alpha() < next_step[1].get_alpha() and
                  next_step[2].get_alpha() < next_step[3].get_alpha() and
                  next_step[2].get_alpha() < next_step[4].get_alpha() and
                  next_step[2].get_alpha() < next_step[5].get_alpha()):
                return next_step[2].coords
            elif (next_step[3].get_alpha() < next_step[0].get_alpha() and
                  next_step[3].get_alpha() < next_step[1].get_alpha() and
                  next_step[3].get_alpha() < next_step[2].get_alpha() and
                  next_step[3].get_alpha() < next_step[4].get_alpha() and
                  next_step[3].get_alpha() < next_step[5].get_alpha()):
                return next_step[3].coords
            elif (next_step[4].get_alpha() < next_step[0].get_alpha() and
                  next_step[4].get_alpha() < next_step[1].get_alpha() and
                  next_step[4].get_alpha() < next_step[2].get_alpha() and
                  next_step[4].get_alpha() < next_step[3].get_alpha() and
                  next_step[4].get_alpha() < next_step[5].get_alpha()):
                return next_step[4].coords
            elif (next_step[5].get_alpha() < next_step[0].get_alpha() and
                  next_step[5].get_alpha() < next_step[1].get_alpha() and
                  next_step[5].get_alpha() < next_step[2].get_alpha() and
                  next_step[5].get_alpha() < next_step[3].get_alpha() and
                  next_step[5].get_alpha() < next_step[4].get_alpha()):
                return next_step[5].coords
            else:
                particle.move_to(random.choice(direction))
                return particle.coords
        else:
            particle.move_to(random.choice(direction))
            return particle.coords

# Go home the way you came
def go_home(particle):
    particle.move_to(particle.list[-1])
    del (particle.list[-1])

# Decrease lifespan of a track
def evaporation(marker):
    if (marker.get_color() == track):
        marker.set_alpha(marker.get_alpha() - 0.01)


# Decrease particle lifespan
def life_span(particle):
    particle.set_alpha(particle.get_alpha() - 0.02)

# Decrease stack of food
def food_stack(food, particle):
    if (particle.coords == food.coords):
        food.set_alpha(food.get_alpha() - 0.1)

# Give color of marker back, if it's a track
def marker_color(world, particle):
    for marker in world.get_marker_list():
        if (particle.coords == marker.coords and marker.get_color() == track):
            return track

# Particle respawn
def respawn(world):
    while len(world.get_particle_list()) < 31:
        ant = world.add_particle(0, 0)
        setattr(ant, "list", [])

# Invert dir
def invert_dir(dir):
    if dir >= 3:
        return dir - 3
    else:
        return dir + 3

# Making a plot
def plot (rounds, deads):
    plt.plot(rounds, deads)
    plt.xlabel("rounds")
    plt.ylabel("dead ants")
    #plt.title("Rounds: ", str(rounds[-1]), "Deads:", str(deads[-1]))
    plt.show()

# Start
###################################################################################################################################################################################

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
        """
        # Get home coords
        if (marker.get_color() == base):
            home = marker
        """
    for particle in world.get_particle_list():

        life_span(particle)

        # Kill ant, when no life span
        if (particle.get_alpha() == 0):
            world.remove_particle(particle.get_id())
            dead_count += 1

        # Search for food
        if (particle.get_color() == search_mode):
            #last_pos = particle.coords
            next_pos = random.choice(direction)
            particle.move_to(next_pos)
            particle.list.append(invert_dir(next_pos))
            #way_home(last_pos, particle)

        # If found food, go in home-mode
        if (particle.check_on_tile() == True):
            particle.set_color(home_mode)

            for food in world.get_tiles_list():
                food_stack(food, particle)
                # Delete food when gone
                if (food.get_alpha() == 0):
                    world.remove_tile_on(food.coords)

        # If in home-mode, go home and lay track
        if (particle.get_color() == home_mode):
            particle.create_marker(track)
            if (particle.list != []):
                go_home(particle)
            #walk(home_co, particle)
            # Restore life span
            particle.set_alpha(1)

        # If found track, follow
        if (marker_color(world, particle) == track and particle.get_color() != home_mode):
            particle.set_color(track_follow_mode)
            next_step = particle.scan_for_marker_within(1)
            #last_pos = particle.coords
            next_pos = follow(next_step, particle)
            #print("next_pos: ", next_pos)
            go_to = walk(next_pos, particle)
            particle.move_to(go_to)
            #follow(next_step, particle)
            particle.list.append(invert_dir(go_to))
            #way_home(last_pos, particle)

        # If home, go back in search-mode
        if (particle.coords == home):
            particle.set_color(search_mode)
            # Reset way home list
            particle.list = []

        # If track die, go back in search-mode
        if (particle.get_color() == track_follow_mode and particle.check_on_marker() == False):
            particle.set_color(search_mode)

    # If all food is collected, success
    if (len(world.get_tiles_list()) == 0):
        world.success_termination()
        print("Rounds:", rounds[-1])
        print("Deads:", deads[-1])
        plot(rounds, deads)

