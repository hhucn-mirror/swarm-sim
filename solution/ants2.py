import logging
import random

"""
partical color = mode
black   (1) = search-mode
blue    (5) = track-follow-mode
violett (7) = home-mode
"""

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

home_co = [0, 0]
way_home = []

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
    particle.move_to(go_to)

# follow track
def follow(next_step, particle):
    if (next_step != None):
        if (len(next_step) == 2):
            if (next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2):
                walk(next_step[0].coords, particle)
            else:
                walk(next_step[1].coords, particle)
        elif (len(next_step) == 3):
            if (next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2):
                walk(next_step[0].coords, particle)
            elif (next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2):
                walk(next_step[1].coords, particle)
            else:
                walk(next_step[2].coords, particle)
        elif (len(next_step) == 4):
            if (next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2):
                walk(next_step[0].coords, particle)
            elif (next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2):
                walk(next_step[1].coords, particle)
            elif (next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2):
                walk(next_step[2].coords, particle)
            else:
                walk(next_step[3].coords, particle)
        elif (len(next_step) == 5):
            if (next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2):
                walk(next_step[0].coords, particle)
            elif (next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2):
                walk(next_step[1].coords, particle)
            elif (next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2):
                walk(next_step[2].coords, particle)
            elif (next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2):
                walk(next_step[3].coords, particle)
            else:
                walk(next_step[4].coords, particle)
        elif (len(next_step) == 6):
            if (next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 and
                    next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 >
                    next_step[5].coords[0] ** 2 + next_step[5].coords[1] ** 2):
                walk(next_step[0].coords, particle)
            elif (next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 and
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 >
                  next_step[5].coords[0] ** 2 + next_step[5].coords[1] ** 2):
                walk(next_step[1].coords, particle)
            elif (next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 and
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 >
                  next_step[5].coords[0] ** 2 + next_step[5].coords[1] ** 2):
                walk(next_step[2].coords, particle)
            elif (next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 and
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 >
                  next_step[5].coords[0] ** 2 + next_step[5].coords[1] ** 2):
                walk(next_step[3].coords, particle)
            elif (next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 >
                  next_step[0].coords[0] ** 2 + next_step[0].coords[1] ** 2 and
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 >
                  next_step[1].coords[0] ** 2 + next_step[1].coords[1] ** 2 and
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 >
                  next_step[2].coords[0] ** 2 + next_step[2].coords[1] ** 2 and
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 >
                  next_step[3].coords[0] ** 2 + next_step[3].coords[1] ** 2 and
                  next_step[4].coords[0] ** 2 + next_step[4].coords[1] ** 2 >
                  next_step[5].coords[0] ** 2 + next_step[5].coords[1] ** 2):
                walk(next_step[4].coords, particle)
            else:
                walk(next_step[5].coords, particle)
        else:
            particle.move_to(random.choice(direction))
    else:
        particle.move_to(random.choice(direction))

def go_home(way_home, particle):
    if (way_home != []):
        print("way home: ", way_home)
        particle.move_to(way_home[-1])
        del (way_home[-1])

def invert_dir(dir):
    if dir >= 3:
        return dir - 3
    else:
        return dir + 3

# Lifespan for track
def eva(world):
    global home1
    global home2
    for marker in world.get_marker_list():
        if (marker.get_color() == 1):
            home1 = marker
        if (marker.get_color() == 9):
            home2 = marker
        if (marker.get_color() == 4 or marker.get_color() == 5):
            marker.set_alpha(marker.get_alpha() - 0.01)
        if (marker.get_alpha() == 0):
            world.remove_marker(marker.get_id())

# Particle lifespan
def life_span(world, particle):
    particle.set_alpha(particle.get_alpha() - 0.01)
    if (particle.get_alpha() == 0):
        world.remove_particle(particle.get_id())

# Stack of food
def food_stack(world, particle):
    for food in world.get_tiles_list():
        if (particle.coords == food.coords):
            food.set_alpha(food.get_alpha() - 0.1)
        if (food.get_alpha() == 0):
            world.remove_tile_on(food.coords)

def marker_color(world, particle):
    for marker in world.get_marker_list():
        if (particle.coords == marker.coords and marker.get_color() == 4):
            return 4
        elif (particle.coords == marker.coords and marker.get_color() == 5):
            return 5
"""    
# Base coords
def base_co(world):
    global home1
    global home2
    for marker in world.get_marker_list():
        if (marker.get_color() == 1):
            home1 = marker
        if (marker.get_color() == 9):
            home2 = marker
"""
def solution(world):

    # Particle respawn
    while len(world.get_particle_list()) < 40:
        world.add_particle(0, 0, 1)
        world.add_particle(12, 0, 9)

    eva(world)
    if (len(world.get_tiles_list()) == 0):
        world.success_termination()

    for particle in world.get_particle_list():
        life_span(world, particle)

        # Search for food
        # Colony 1
        if (particle.get_color() == 1):
            particle.move_to(random.choice(direction))
            #make_home_list()

        # Colony 2
        if (particle.get_color() == 9):
        #if (particle.get_color() != 5):
            particle.move_to(random.choice(direction))
            #make_home_list()

        # If found food, go in home-mode
        # Colony 1
        if (particle.check_on_tile() == True and particle.get_color() == 1):
            particle.set_color(7)
            food_stack(world, particle)
        # Colony 2
        if (particle.check_on_tile() == True and particle.get_color() == 9):
            particle.set_color(3)
            food_stack(world, particle)

        # If in home-mode, go home and lay track
        # Colony 1
        if (particle.get_color() == 7):
            particle.create_marker(4)
            #go_home()
            walk(home1.coords, particle)
            particle.set_alpha(1)
        # Colony 2
        if (particle.get_color() == 3):
            particle.create_marker(5)
            #go_home()
            walk(home2.coords, particle)
            particle.set_alpha(1)

        # If found track, follow
        # Colony 1
        if (marker_color(world, particle) == 4):
            particle.set_color(4)
            next_step = particle.scan_for_marker_within(1)
            follow(next_step, particle)
            #make_home_list()
        # Colony 2
        if (marker_color(world, particle) == 5):
            particle.set_color(5)
            next_step = particle.scan_for_marker_within(1)
            follow(next_step, particle)
            #make_home_list()

        # If home, go back in search-mode
        # Colony 1
        if (particle.coords == home1.coords):
            particle.set_color(1)
        # Colony 2
        if (particle.coords == home2.coords):
            particle.set_color(9)

        # If track die, go back in search-mode
        # Colony 1
        if (particle.get_color() == 4 and particle.check_on_marker() == False):
            particle.set_color(1)
            way_home = []
        # Colony 2
        if (particle.get_color() == 5 and particle.check_on_marker() == False):
            particle.set_color(9)
            way_home = []