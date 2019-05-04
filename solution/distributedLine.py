NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

def solution(sim):
    print("Runde = ",  sim.get_actual_round())
    if (sim.get_actual_round() == 1):
        initialize(sim)

    for particle in sim.get_particle_list():
        check_nb(particle)
##################################################################################

# initialize the memory of every particle, first delete whole and then only reserve
# memory for direction
def initialize(sim):
    for particle in sim.get_particle_list():
        particle.delete_whole_memeory()
        particle.write_memory_with("Direction", "None")
###################################################################################

# depending on the amount of neighbours switch the case
def check_nb(particle):
    neighbours = particle.scan_for_particle_within(hop=1)
    nbLen = len(neighbours)

    if nbLen == 1: one_nb(particle)
    if nbLen == 2: two_nb(particle)
    if nbLen == 3: three_nb(particle)
    #if nbLen == 4: four_nb(particle)
    #if nbLen == 5: five_nb(particle)
    #if nbLen == 6: print()#six_nb(particle)

##################################################################################
# moves to the direction in particles memory if the direction isnt none
def move_and_refresh_mem(particle):
    if particle.read_memory_with("Direction") != "None":
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.set_color(1)
##################################################################################

# calculate the movement for particle with 1 neighbour
def one_nb(particle):
    dir = 2
    while dir < 4:
        if particle.get_particle_in(dir) != None and dir != W and dir != E:
            particle.write_memory_with("Direction", (dir - 1) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1

# calculate the movement for particle with 2 neighbour
def two_nb(particle):
    if particle.get_particle_in(W) != None and particle.get_particle_in(E) != None:
        return

    if two_nb_case1(particle): return
    if two_nb_case2(particle): return
    if two_nb_case3(particle): return

def two_nb_case1(particle):
    dir = 0
    while dir < 6:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir+1) % 6)

        if firstNB != None and secondNB != None:
            particle.write_memory_with("Direction", (dir - 1) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return False
def two_nb_case2(particle):
    dir = 1
    while dir < 5:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 2) % 6)

        if firstNB != None and secondNB != None:
            particle.write_memory_with("Direction", (dir + 1) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return False
def two_nb_case3(particle):
    return True

# calculate the movement for particle with 3 neighbour
def three_nb(particle):
    if three_nb_case1(particle): return
    if three_nb_case2(particle): return
    if three_nb_case3(particle): return
    if three_nb_case4(particle): return

def three_nb_case1(particle):
    dir = 0
    while dir < 6:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 2) % 6)

        if firstNB != None and secondNB != None and thirdNB != None:
            particle.write_memory_with("Direction", (dir + 3) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return  False
def three_nb_case2(particle):
    dir = 0
    while dir < 6:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 3) % 6)

        if firstNB != None and secondNB != None and thirdNB != None:
            particle.write_memory_with("Direction", (dir + 2) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return  False
def three_nb_case3(particle):
    dir = 0
    while dir < 6:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 3) % 6)

        if firstNB != None and secondNB != None and thirdNB != None:
            particle.write_memory_with("Direction", (dir + 5) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return  False
def three_nb_case4(particle):
    return True

# calculate the movement for particle with 4 neighbour
def four_nb(particle):
    if four_nb_case1(particle): return
    if four_nb_case2(particle): return
    if four_nb_case3(particle): return

def four_nb_case1(particle):
    dir = 2
    while dir < 4:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 2) % 6)
        fourthNB = particle.get_particle_in((dir + 3) % 6)

        if firstNB != None and secondNB != None and thirdNB != None and fourthNB != None:
            particle.write_memory_with("Direction", (dir + 2) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return False
def four_nb_case2(particle):
    dir = 2
    while dir < 4:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 2) % 6)
        fourthNB = particle.get_particle_in((dir + 4) % 6)

        if firstNB != None and secondNB != None and thirdNB != None and fourthNB != None:
            particle.write_memory_with("Direction", (dir + 3) % 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return False
def four_nb_case3(particle):
    return True

# calculate the movement for particle with 5 neighbour
def five_nb(particle):
    dir = 2
    while dir < 4:
        firstNB = particle.get_particle_in(dir)
        secondNB = particle.get_particle_in((dir + 1) % 6)
        thirdNB = particle.get_particle_in((dir + 2) % 6)
        fourthNB = particle.get_particle_in((dir + 3) % 6)
        fifthNB = particle.get_particle_in((dir + 4) % 6)

        if firstNB != None and secondNB != None and thirdNB != None and fourthNB != None and fifthNB != None:
            particle.write_memory_with("Direction", (dir + 5)% 6)
            move_and_refresh_mem(particle)
            return True
        dir = dir + 1
    return False