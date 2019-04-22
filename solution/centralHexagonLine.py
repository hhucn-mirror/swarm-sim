
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
startRound = 1
formation = "hexagon"
formed = False
tileY = None

def solution(sim):
    print("Runde = ", sim.get_actual_round())
    if formation == "hexagon":
        solution_hexagon(sim, sim)
    elif formation == "line":
        solution_line(sim, sim)

def solution_hexagon(sim):
    if formed == True:
        if (sim.get_actual_round() % 2 == 1):
            scan_for_tiles(sim.get_particle_list(), sim)
    else:
        if (sim.get_actual_round() == startRound):
            delete_memories(sim.get_particle_list())
            initialize_hexagon(sim.get_particle_list())

        if (sim.get_actual_round() % 2 == 1):
            if is_formed(sim.get_particle_list()): return
            calc_movement_hexagon()
        else:
            move_and_refresh_mem_hexagon()

def solution_line(sim):
    if formed:
        if (sim.get_actual_round() % 2 == 1):
            scan_for_tiles(sim.get_particle_list(), sim)
    else:
        if (sim.get_actual_round() == startRound):
            delete_memories(sim.get_particle_list())
            initialize_line(sim.get_particle_list())

        if (sim.get_actual_round() % 2 == 1):
            if is_formed(sim.get_particle_list()): return
            calc_movement_line()
        else:
            move_and_refresh_mem_line()

##################################################################################

def is_formed(particleList):
    global formed
    for particle in particleList:
        if particle.read_memory_with("Leader") == "False":
            return False
    formed = True
    return True

def scan_for_tiles(particleList, sim):
    global formation, formed, startRound

    if formation == "hexagon" and particle_scan_for_tile(particleList):
        formation = "line"
        formed = False
        startRound = sim.get_actual_round() + 2
    elif formation == "line" and not particle_scan_for_tile(particleList):
        formation = "hexagon"
        formed = False
        startRound = sim.get_actual_round()+2



def particle_scan_for_tile(particleList):
    global tileY
    for particle in particleList:
        dir = 0
        while dir < 6:
            if particle.get_tile_in(dir) != None:
                if dir in [5, 0]: tileY = particle.coords[1] + 1
                if dir in [4, 1]: tileY = particle.coords[1]
                if dir in [3, 2]: tileY = particle.coords[1] - 1
                return True
            dir = dir + 1
    return False
################################################################################## HEXAGON BEGIN

# initialize the first leader
def initialize_hexagon(particleList):
    leaders.clear()
    for particle in particleList:
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Mark", "False")
        particle.write_memory_with("Direction", "None")
    leader = particleList[0]
    #leader = sim.get_particle_map_coords()[0.5, -7.0]
    leader.write_memory_with("Leader", "True")
    leader.write_memory_with("Mark", "True")
    leaders.append(leader)

# calculates for one leader the movement
def calc_movement_hexagon():
    for particle in leaders:
        i = 0
        while i < 6:
            nb = particle.get_particle_in(i)
            next_nb = particle.get_particle_in((i+1)%6)
            if nb != None and  next_nb == None and nb.read_memory_with("Leader") == "False":
                dir = (i+2) % 6
                dictate(nb, dir)
                return check_if_nb_of_leader(particle, have_to_move[len(have_to_move)-1])
            i = i + 1
        appoint_leaders_hexagon()

# leader tells non leader neighbour to move in a circle till every spot is filled
def dictate(particle, dir):
    particle.write_memory_with("Direction", dir)
    particle.write_memory_with("Mark", "True")
    particle.set_color(3)
    have_to_move.append(particle)

    for p in particle.scan_for_particle_within(hop=1):
        if p.read_memory_with("Leader") == "False" and p.read_memory_with("Mark") == "False":
            return replace_me(particle, p)

# appoints next leaders only if all current leaders are an hexagon
def appoint_leaders_hexagon():
    for l in leaders:
        neighbours = l.scan_for_particle_within(hop=1)
        if len (neighbours) != 6:
            return

    new_leaders = []
    for l in leaders:
        neighbours = l.scan_for_particle_within(hop=1)
        for nb in neighbours:
            if nb.read_memory_with("Leader") == "False":
                nb.write_memory_with("Leader", "True")
                nb.write_memory_with("Mark", "True")
                new_leaders.append(nb)
    leaders.clear()
    leaders.extend(new_leaders)

# check if last particle in have_to_move is a nb of a leader
def check_if_nb_of_leader(leader, particle):
    if particle != None and len(have_to_move) > 1:
        neighbours = particle.scan_for_particle_within(hop=1)
        for nb in neighbours:
            if leader == nb:
                particle.set_color(1)
                particle.write_memory_with("Direction", "None")
                particle.write_memory_with("Mark", "False")
                have_to_move.remove(particle)

#############

def move_and_refresh_mem_hexagon():
    for particle in have_to_move:
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
        particle.set_color(1)
    have_to_move.clear()

################################################################################## HEXAGON END

############################################################################# LINE BEGIN

# initialize the sim
def initialize_line(particleList):
    leaders.clear()
    for particle in particleList:
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
    for particle in particleList:
        if particle.coords[1]+1 == tileY or particle.coords[1]-1 == tileY:
            return look_for_leaders(particle)

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

def calc_movement_line():
    for particle in leaders:
        i = 0
        while i < 6:
            nb = particle.get_particle_in(i)
            if nb != None:
                particle.set_color(2)
                leader_to_left(particle)
                appoint_leader_line(nb)
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

# appoint leader
def appoint_leader_line(particle):
    particle.write_memory_with("Leader", "True")
    leaders.append(particle)

###############

def move_and_refresh_mem_line():
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

############################################################################# LINE END

# calculates how p2 has to move to replace p1
def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

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

# delete memory of every particle in particleList
def delete_memories(particleList):
    for particle in particleList:
        particle.delete_whole_memeory()

##################################################################################