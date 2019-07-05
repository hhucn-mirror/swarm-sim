NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

leaders = []
have_to_move = []
leaders_to_move = []

def solution(sim):
    print("Runde = ",  sim.get_actual_round())

    if (sim.get_actual_round() == 1):
        initialize(sim)

    if (sim.get_actual_round() % 2 == 1):
        calc_movement()
    else:
        move_and_refresh_mem()

##################################################################################

# initialize the sim
def initialize(sim):
    for particle in sim.get_particle_list():
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
    look_for_leaders(sim.get_particle_list()[0])

# if and horizantal line already exists from the beginning,
# every particle of that is directly a leader
def look_for_leaders(particle):
    particle.write_memory_with("Leader", "True")
    leaders.append(particle)

    left_nb = particle.get_particle_in(W)
    right_nb = particle.get_particle_in(E)

    if left_nb != None and left_nb.read_memory_with("Leader") == "False":
        look_for_leaders(left_nb)
    if right_nb != None and right_nb.read_memory_with("Leader") == "False":
        look_for_leaders(right_nb)

##################################################################################

def move_and_refresh_mem():
    for particle in leaders_to_move:
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
        particle.set_color(1)

    for particle in have_to_move:
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
        particle.set_color(1)
    have_to_move.clear()
    leaders_to_move.clear()

##################################################################################

def calc_movement():
    for particle in leaders:
        i = 0
        while i < 6:
            nb = particle.get_particle_in(i)
            if nb != None:
                leader_to_left(particle)
                appoint_leader(nb)
                return replace_me(particle, nb)
            if i == 2:  i = i+1
            else:       i = i+2

# shift leaders to left to make room for one particle above or under one leader
def leader_to_left(particle):
    nw = particle.get_particle_in(W)
    if nw != None:
        leader_to_left(nw)
    particle.write_memory_with("Direction", W)
    particle.set_color(3)
    leaders_to_move.append(particle)

# replace per indepth every particle
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

# calculates how p2 has to move to replace p1
def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

# appoint leader
def appoint_leader(particle):
    particle.write_memory_with("Leader", "True")
    leaders.append(particle)
