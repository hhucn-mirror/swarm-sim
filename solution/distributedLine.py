NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

def solution(sim):
    print("Runde", sim.get_actual_round())
    if sim.get_actual_round() == 1:
        init_particles(sim.get_particle_list())
        leader_election(sim.get_particle_list())

    if sim.get_actual_round() % 2 == 1:
        update_leaders(sim.get_particle_list())
        calc_movement(sim.get_particle_list())
    else:
        get_first_particle_to_move(sim.get_particle_list())


# elects leader with the highest id
def leader_election(particleList):
    for particle in particleList:
        send_max_id_to_all_nbs(particle)
    for particle in particleList:
        if particle.number == particle.read_memory_with("MaxID"):
            particle.write_memory_with("Leader", "True")
            particle.set_color(4)
            look_for_more_leader(particle)

# sends max id to all nbs and recursivley the nbs send it to their nbs
def send_max_id_to_all_nbs(particle):
    nbs = particle.scan_for_particle_within(hop=1)
    for neigh in nbs:
        if neigh.read_memory_with("MaxID") < particle.read_memory_with("MaxID"):
            particle.write_to_with(neigh, "MaxID", particle.read_memory_with("MaxID"))
            send_max_id_to_all_nbs(neigh)

# initialize the memory of the particles
def init_particles(particleList):
    for particle in particleList:
        particle.write_memory_with("MaxID", particle.number)
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Mark", "False")
        particle.write_memory_with("Order", None)
        particle.write_memory_with("Direction", None)

# every particle on the same height as the first leader particle will become leaders as well
def look_for_more_leader(particle):
    particle.write_memory_with("Leader", "True")
    particle.set_color(4)

    nbW = particle.get_particle_in(W)
    nbE = particle.get_particle_in(E)

    if nbW != None and nbW.read_memory_with("Leader") == "False":
        look_for_more_leader(nbW)
    if nbE != None and nbE.read_memory_with("Leader") == "False":
        look_for_more_leader(nbE)

def update_leaders(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") == "True":
            look_for_more_leader(particle)

def calc_movement(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") == "True" and particle.read_memory_with("Mark") == "False":
            calc_movement_for_leader(particle)

def calc_movement_for_leader(particle):
    directions = [NE, SE, SW, NW]

    for dir in directions:
        if particle.get_particle_in(dir):
            shift_leaders_to_left(particle)
            # all leaders are ordered marked and rdy
            # no one leader tells one non leader neighbour how to move
            indepth_replacement(particle)

def indepth_replacement(particle):
    nbs = particle.scan_for_particle_within(1)
    for nb in nbs:
        if nb.read_memory_with("Leader") == "False" and nb.read_memory_with("Mark") == "False":
            orderNr = particle.read_memory_with("Order")
            orderNr = orderNr + 1

            dir = calc_dir(particle, nb)

            nb.write_memory_with("Mark", "True")
            nb.write_memory_with("Order", orderNr)
            nb.write_memory_with("Direction", dir)

            return indepth_replacement(nb)

def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

def shift_leaders_to_left(particle):
    nbW = particle.get_particle_in(W)
    nbE = particle.get_particle_in(E)

    orderNr = 1

    if nbW != None:
        orderNr = shift_leaders_to_left(nbW)

    particle.write_memory_with("Mark", "True")
    particle.write_memory_with("Direction", W)
    particle.write_memory_with("Order", orderNr)

    if nbE != None:
        mark_leaders_on_right(nbE)

    orderNr = orderNr + 1
    return orderNr

def mark_leaders_on_right(particle):
    particle.write_memory_with("Mark", "True")
    if particle.get_particle_in(E):
        mark_leaders_on_right(particle.get_particle_in(E))

def get_first_particle_to_move(particleList):
    particleToMove = None

    for particle in particleList:
        if particle.read_memory_with("Order") == 1:
            particleToMove = particle
            break

    if particleToMove != None:
        move_in_right_order(particleToMove, 1)

def move_in_right_order(particle, orderNr):
    if particle.read_memory_with("Order") != orderNr:
        return

    nbs = particle.scan_for_particle_within(1)

    nextParticle = None
    if nbs != None:
        for nb in nbs:
            if nb.read_memory_with("Order") == (orderNr+1):
                nextParticle = nb
                break

    dir = particle.read_memory_with("Direction")
    particle.move_to(dir)
    refresh_mem(particle)

    if nextParticle != None:
        move_in_right_order(nextParticle, (orderNr+1))

def refresh_mem(particle):
    particle.write_memory_with("Mark", "False")
    particle.write_memory_with("Order", None)
    particle.write_memory_with("Direction", None)
