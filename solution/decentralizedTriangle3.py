import random

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

    for particle in sim.get_particle_list():
        if sim.get_actual_round() % 7 == 1:
            announce_next(particle)
        elif sim.get_actual_round() % 7 == 2:
            update_leaders(particle)
        elif sim.get_actual_round() % 7 == 3:
            neighbour_of_leader(particle)
        elif sim.get_actual_round() % 7 == 4:
            calc_move(particle)
        elif sim.get_actual_round() % 7 == 5:
            if particle.read_memory_with("Moving") == 0:
                announce_right_placed_to_leaders(particle)
            else:
                get_first_to_move(particle)
        elif sim.get_actual_round() % 7 == 6:
            update_state(particle)
        elif sim.get_actual_round() % 7 == 0:
            refresh_mem(particle)
            formed(sim)

        formed(sim)

# initialize the memory of the particles
def init_particles(particleList):
    for particle in particleList:
        particle.write_memory_with("MaxID", particle.number)
        particle.write_memory_with("Leader", 0)
        particle.write_memory_with("Mark", 0)
        particle.write_memory_with("AnnounceNext", None)
        particle.write_memory_with("Order", None)
        particle.write_memory_with("Direction", None)
        particle.write_memory_with("Moving", 0)
        particle.write_memory_with("WayForN", None)
        particle.write_memory_with("UpdateState", None)

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

def announce_next(particle):
    if particle.read_memory_with("Leader") == 1:
        if particle.read_memory_with("AnnounceNext") is None:

            sw = particle.get_particle_in(SW)
            se = particle.get_particle_in(SE)
            if sw is not None and se is not None:
                particle.write_memory_with("AnnounceNext", 1)
            else:
                particle.write_memory_with("AnnounceNext", 0)
                set_nbs_announceNext_to_false(particle)

def set_nbs_announceNext_to_false(particle):
    nbs = particle.scan_for_particle_within(1)
    for nb in nbs:
        if nb.read_memory_with("Leader") == 1 and nb.read_memory_with("AnnounceNext") != 0:
            particle.write_to_with(nb,"AnnounceNext", 0)
            set_nbs_announceNext_to_false(nb)

def update_leaders(particle):
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

def neighbour_of_leader(particle):
    if particle.read_memory_with("Leader") == 0:
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Leader") >= 1 and nb.read_memory_with("WayForN") == None:
                particle.write_to_with(nb, "WayForN", calc_dir(particle, nb))
                spread_way(nb)

# spreads a way between the leaders/placed to the non-leader
def spread_way(particle):
    if particle.read_memory_with("Leader") >= 1 and particle.read_memory_with("Mark") == 0:
        particle.write_memory_with("Mark", 1)
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Leader") >= 1 and nb.read_memory_with("WayForN") == None:
                particle.write_to_with(nb, "WayForN", calc_dir(particle, nb))
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Leader") >= 1 and nb.read_memory_with("WayForN") != None:
                spread_way(nb)

# calcs how p2 has to move to replace p1
def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1


def calc_move(particle):
    if particle.read_memory_with("Leader") == 1 and particle.read_memory_with("WayForN") != None and particle.read_memory_with("Moving") == 0:
        se = particle.get_particle_in(SE)
        sw = particle.get_particle_in(SW)

        if se == None or sw == None:
            spread_moving(particle)
        else:
            return

        if sw == None:
            particle.write_memory_with("Direction", SW)
        elif se == None:
            particle.write_memory_with("Direction", SE)

        particle.write_memory_with("Order", 1)
        replacement(particle)
        particle.set_color(3)

def spread_moving(particle):
    if particle.read_memory_with("Moving") == 0:
        particle.write_memory_with("Moving", 1)
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Leader") >= 1 and nb.read_memory_with("Moving") == 0:
                spread_moving(nb)

def replacement(particle):
    order = particle.read_memory_with("Order")
    order = order+1

    if particle.read_memory_with("Leader") >= 1:
        dir_for_next = particle.read_memory_with("WayForN")
        next = particle.get_particle_in(dir_for_next)

        particle.write_to_with(next, "Order", order)
        particle.write_to_with(next, "Direction", calc_dir(particle, next))
        particle.write_to_with(next, "UpdateState", particle.read_memory_with("Leader"))

        next.set_color(3)

        return replacement(next)

    else:
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Leader") == 0 and nb.read_memory_with("Direction") == None:

                particle.write_to_with(nb, "Order", order)
                particle.write_to_with(nb, "Direction", calc_dir(particle, nb))
                particle.write_to_with(nb, "UpdateState", particle.read_memory_with("Leader"))

                nb.set_color(3)

                return replacement(nb)

def get_first_to_move(particle):
    if particle.read_memory_with("Order") == 1:
        particle.write_memory_with("UpdateState", 2)
        move_in_right_order(particle, 1)

def move_in_right_order(particle, order):
    if particle.read_memory_with("Order") != order:
        return

    next = None
    nbs = particle.scan_for_particle_within(1)
    if nbs != None:
        for nb in particle.scan_for_particle_within(1):
            if nb.read_memory_with("Order") == (order+1):
                next = nb
                break

    dir = particle.read_memory_with("Direction")
    particle.move_to(dir)
    particle.set_color(1)

    if next != None:
        move_in_right_order(next, (order+1))

def update_state(particle):
    if particle.read_memory_with("UpdateState") != None:
        state = particle.read_memory_with("UpdateState")
        particle.write_memory_with("Leader", state)

def refresh_mem(particle):
    particle.write_memory_with("Order", None)
    particle.write_memory_with("Mark", 0)
    particle.write_memory_with("Direction", None)
    particle.write_memory_with("AnnounceNext", None)
    particle.write_memory_with("Moving", 0)
    particle.write_memory_with("WayForN", None)
    particle.write_memory_with("UpdateState", None)
    if particle.read_memory_with("Leader") == 1:
        particle.set_color(4)
    if particle.read_memory_with("Leader") == 2:
        particle.set_color(5)

def announce_right_placed_to_leaders(particle):
    if particle.read_memory_with("Leader") == 1 and particle.read_memory_with("Moving") == 0:
        sw = particle.get_particle_in(SW)
        se = particle.get_particle_in(SE)

        if sw is not None and sw.read_memory_with("Leader") == 2:
            particle.write_to_with(sw, "Leader", 1)
            sw.set_color(4)
        if se is not None and se.read_memory_with("Leader") == 2:
            particle.write_to_with(se, "Leader", 1)
            se.set_color(4)

def formed(sim):
    for particle in sim.get_particle_list():
        if particle.read_memory_with("Leader") != 1:
            return
    sim.success_termination()