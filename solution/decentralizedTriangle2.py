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

    if sim.get_actual_round() % 6 == 1:
        refresh_mem(sim.get_particle_list())
    elif sim.get_actual_round() % 6 == 2:
        announce_next(sim.get_particle_list())
    elif sim.get_actual_round() % 6 == 3:
        update_leaders(sim.get_particle_list())
    elif sim.get_actual_round() % 6 == 4:
        calc_movement(sim.get_particle_list())
    elif sim.get_actual_round() % 6 == 5:
        announce_right_placed_to_leaders(sim.get_particle_list())
    elif sim.get_actual_round() % 6 == 0:
        get_first_particle_to_move(sim.get_particle_list())


# initialize the memory of the particles
def init_particles(particleList):
    for particle in particleList:
        particle.write_memory_with("MaxID", particle.number)
        particle.write_memory_with("Leader", 0)
        particle.write_memory_with("AnnounceNext", None)
        particle.write_memory_with("Mark", 0)
        particle.write_memory_with("Order", None)
        particle.write_memory_with("Direction", None)
        particle.write_memory_with("NeighbourOfLeader", None)
        particle.write_memory_with("Moving", 0)

# elects leader with the highest id
def leader_election(particleList):
    for particle in particleList:
        send_max_id_to_all_nbs(particle)
    for particle in particleList:
        if particle.number == particle.read_memory_with("MaxID"):
            particle.write_memory_with("Leader", 1)
            particle.set_color(4)

# sends max id to all nbs and recursivley the nbs send it to their nbs
def send_max_id_to_all_nbs(particle):
    nbs = particle.scan_for_particle_within(hop=1)
    for nb in nbs:
        if nb.read_memory_with("MaxID") < particle.read_memory_with("MaxID"):
            particle.write_to_with(nb, "MaxID", particle.read_memory_with("MaxID"))
            send_max_id_to_all_nbs(nb)

#################################################################################

def announce_next(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") == 1:

            if particle.read_memory_with("AnnounceNext") is None:

                sw = particle.get_particle_in(SW)
                se = particle.get_particle_in(SE)

                if sw is not None and se is not None:
                    particle.write_memory_with("AnnounceNext", 1)
                else:
                    particle.write_memory_with("AnnounceNext", 0)

            # maybe not necessary
            if particle.read_memory_with("AnnounceNext") == 0:
                set_nbs_announceNext_to_false(particle)


def set_nbs_announceNext_to_false(particle):
    nbs = particle.scan_for_particle_within(1)
    for nb in nbs:
        if nb.read_memory_with("Leader") == 1 and nb.read_memory_with("AnnounceNext") != 0:
            particle.write_to_with(nb,"AnnounceNext", 0)
            set_nbs_announceNext_to_false(nb)

def update_leaders(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") == 1:
            sw = particle.get_particle_in(SW)
            se = particle.get_particle_in(SE)

            if particle.read_memory_with("AnnounceNext") == 1:
                particle.write_to_with(sw, "Leader", 1)
                particle.write_to_with(se, "Leader", 1)
                sw.set_color(4)
                se.set_color(4)

            if particle.read_memory_with("AnnounceNext") == 0:
                if sw is not None and sw.read_memory_with("Leader") == 0:
                    particle.write_to_with(sw, "Leader", 2)
                    sw.set_color(5)
                if se is not None and se.read_memory_with("Leader") == 0:
                    particle.write_to_with(se, "Leader", 2)
                    se.set_color(5)

#################################################################################

def calc_movement(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") >= 1:
            i = 0
            while i < 6:
                nb = particle.get_particle_in(i)
                next_nb = particle.get_particle_in((i + 1) % 6)
                if nb is not None and next_nb is None and nb.read_memory_with("Leader") == 0:
                    dir = (i + 2) % 6
                    particle.write_memory_with("Moving", 1)
                    set_moving_for_leaders(particle)
                    return dictate(nb, dir)
                i = i + 1

def set_moving_for_leaders(particle):
    nbs = particle.scan_for_particle_within(1)
    for nb in nbs:
        if nb.read_memory_with("Leader") >= 1 and nb.read_memory_with("Moving") != 1:
            particle.write_to_with(nb, "Moving", 1)
            set_moving_for_leaders(nb)

# leader tells non leader neighbour to move in a circle till every spot is filled
def dictate(particle, dir):
    particle.write_memory_with("Direction", dir)
    particle.write_memory_with("Mark", 1)
    particle.write_memory_with("Order", 1)
    particle.set_color(3)

    indepth_replacement(particle)

def indepth_replacement(particle):
    particle.set_color(3)
    nbs = particle.scan_for_particle_within(1)
    neighbour_of_leader(particle)

    if predecessor_not_nb_of_leader(particle, particle.read_memory_with("Order")):
        return

    for nb in nbs:
        if nb.read_memory_with("Leader") == 0 and nb.read_memory_with("Mark") == 0:
            orderNr = particle.read_memory_with("Order")
            orderNr = orderNr + 1

            dir = calc_dir(particle, nb)

            particle.write_to_with(nb, "Mark", 1)
            particle.write_to_with(nb, "Order", orderNr)
            particle.write_to_with(nb, "Direction", dir)

            return indepth_replacement(nb)

# tests if predecessor is not a nb of leader
def predecessor_not_nb_of_leader(particle, orderNr):
    for nb in particle.scan_for_particle_within(1):
        if nb.read_memory_with("Order") == particle.read_memory_with("Order")-1:
            if nb.read_memory_with("NeighbourOfLeader") == 0 and particle.read_memory_with("NeighbourOfLeader") >= 1:
                return True
    return False

#write to memory true if particle is nb of leader or placed particle, if not false
def neighbour_of_leader(particle):
    for nb in particle.scan_for_particle_within(1):
        if nb.read_memory_with("Leader") >= 1:
            particle.write_memory_with("NeighbourOfLeader", 1)
            return
    particle.write_memory_with("NeighbourOfLeader", 0)


def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

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
    particle.set_color(1)

    if nextParticle != None:
        move_in_right_order(nextParticle, (orderNr+1))

def refresh_mem(particleList):
    for particle in particleList:
        particle.write_memory_with("Mark", 0)
        particle.write_memory_with("Order", None)
        particle.write_memory_with("Direction", None)
        particle.write_memory_with("AnnounceNext", None)
        particle.write_memory_with("NeighbourOfLeader", None)
        particle.write_memory_with("Moving", 0)

def announce_right_placed_to_leaders(particleList):
    for particle in particleList:
        if particle.read_memory_with("Leader") == 1 and particle.read_memory_with("Moving") == 0:
            sw = particle.get_particle_in(SW)
            se = particle.get_particle_in(SE)

            if sw is not None and sw.read_memory_with("Leader") == 2:
                particle.write_to_with(sw, "Leader", 1)
                sw.set_color(4)
            if se is not None and se.read_memory_with("Leader") == 2:
                particle.write_to_with(se, "Leader", 1)
                se.set_color(4)