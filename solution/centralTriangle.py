import logging
import random

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

leaders = []
have_to_move = []

def solution(sim, world):
    print("Runde = ",  sim.get_actual_round())
    if (sim.get_actual_round() == 1):
        initialize(world)

    if (sim.get_actual_round() % 2 == 1):
        calc_movement()
    else:
        move_and_refresh_mem()

##################################################################################

# initialize the first leader
def initialize(world):
    for particle in world.get_particle_list():
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Mark", "False")
        particle.write_memory_with("Direction", "None")
    leader = world.get_particle_list()[0]
    #leader = world.get_particle_map_coords()[2.5, -1.0]
    leader.write_memory_with("Leader", "True")
    leader.write_memory_with("Mark", "True")
    leaders.append(leader)

##################################################################################

# calculates how p2 has to move to replace p1
def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

# calculates for one leader the movement
def calc_movement():
    for particle in leaders:
        i = 0
        while i < 6:
            nb = particle.get_particle_in(i)
            next_nb = particle.get_particle_in((i+1)%6)
            if nb != None and  next_nb == None and nb.read_memory_with("Leader") == "False":
                dir = (i+2) % 6
                dictate(nb, dir)
                return check_if_nb_of_leader(particle, have_to_move[len(have_to_move) - 1])
            i = i + 1
        appoint_leaders()

# leader tells non leader neighbour to move in a circle till every spot is filled
def dictate(particle, dir):
    particle.write_memory_with("Direction", dir)
    particle.write_memory_with("Mark", "True")
    particle.set_color(3)
    have_to_move.append(particle)

    for p in particle.scan_for_particle_within(hop=1):
        if p.read_memory_with("Leader") == "False" and p.read_memory_with("Mark") == "False":
            return replace_me(particle, p)

# replace per indepth every non leader particle
def replace_me(particle, particle2):
    dir = calc_dir(particle, particle2)
    particle2.write_memory_with("Direction", dir)
    particle2.write_memory_with("Mark", "True")
    particle2.set_color(3)
    have_to_move.append(particle2)

    for p in particle2.scan_for_particle_within(hop=1):
        #if p != None:
        if p.read_memory_with("Leader") == "False" and p.read_memory_with("Mark") == "False":
            return replace_me(particle2, p)

##################################################################################

# appoints next leaders only if all current leaders are a square
def appoint_leaders():
    for l in leaders:
        b_r = l.get_particle_in(SE)
        b_l = l.get_particle_in(SW)
        if b_r == None or b_l == None:
            return

    new_leaders = []
    for l in leaders:
        i = 2
        while i < 4:
            p = l.get_particle_in(i)
            if p.read_memory_with("Leader") == "False":
                p.write_memory_with("Leader", "True")
                p.write_memory_with("Mark", "True")
                new_leaders.append(p)
            i = i + 1
    leaders.extend(new_leaders)

##################################################################################

def move_and_refresh_mem():
    for particle in have_to_move:
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
        particle.set_color(1)
    have_to_move.clear()

##################################################################################

def check_if_nb_of_leader(leader, particle):
    if particle != None and len(have_to_move) > 1:
        neighbours = particle.scan_for_particle_within(hop=1)
        for nb in neighbours:
            if leader == nb:
                particle.set_color(1)
                particle.write_memory_with("Direction", "None")
                particle.write_memory_with("Mark", "False")
                have_to_move.remove(particle)