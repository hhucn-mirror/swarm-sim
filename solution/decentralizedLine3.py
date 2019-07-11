import solution.leader as l
import solution.help_methods as hm

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
        hm.init_particles(sim.get_particle_list())
        l.elect(sim.get_particle_list())

    for particle in sim.get_particle_list():
        if sim.get_actual_round() % 7 == 1:
            announce_next(particle)
        elif sim.get_actual_round() % 7 == 2:
            update_leaders(particle)
        elif sim.get_actual_round() % 7 == 3:
            hm.neighbour_of_leader(particle)
        elif sim.get_actual_round() % 7 == 4:
            calc_move(particle)
        elif sim.get_actual_round() % 7 == 5:
            if particle.read_memory_with("Moving") == 0:
                announce_right_placed_to_leaders(particle)
            else:
                hm.get_first_to_move(particle)
        elif sim.get_actual_round() % 7 == 6:
            hm.update_state(particle)
        elif sim.get_actual_round() % 7 == 0:
            hm.refresh_mem(particle)
            hm.is_formed(sim)


def announce_next(particle):
    if particle.read_memory_with("Leader") == 1:
        if particle.read_memory_with("AnnounceNext") is None:

            e = particle.get_particle_in(E)
            w = particle.get_particle_in(W)
            if e is not None and w is not None:
                particle.write_memory_with("AnnounceNext", 1)
            else:
                particle.write_memory_with("AnnounceNext", 0)
                hm.set_nbs_announceNext_to_false(particle)

def update_leaders(particle):
    if particle.read_memory_with("Leader") == 1:
        e = particle.get_particle_in(E)
        w = particle.get_particle_in(W)

        if particle.read_memory_with("AnnounceNext") == 1:
            particle.write_to_with(w, "Leader", 1)
            particle.write_to_with(e, "Leader", 1)
            w.set_color(4)
            e.set_color(4)

        if particle.read_memory_with("AnnounceNext") == 0:
            if w is not None and w.read_memory_with("Leader") == 0:
                particle.write_to_with(w, "Leader", 2)
                w.set_color(5)
            if e is not None and e.read_memory_with("Leader") == 0:
                particle.write_to_with(e, "Leader", 2)
                e.set_color(5)

def calc_move(particle):
    if particle.read_memory_with("Leader") == 1 and particle.read_memory_with("WayForN") != None and particle.read_memory_with("Moving") == 0:
        e = particle.get_particle_in(E)
        w = particle.get_particle_in(W)

        if e is None or w is None:
            hm.spread_moving(particle)
        else:
            return

        if w is None:
            particle.write_memory_with("Direction", W)
        elif e is None:
            particle.write_memory_with("Direction", E)

        particle.write_memory_with("Order", 1)
        hm.replacement(particle)
        particle.set_color(3)

def announce_right_placed_to_leaders(particle):
    if particle.read_memory_with("Leader") == 1 and particle.read_memory_with("Moving") == 0:
        e = particle.get_particle_in(E)
        w = particle.get_particle_in(W)

        if w is not None and w.read_memory_with("Leader") == 2:
            particle.write_to_with(w, "Leader", 1)
            w.set_color(4)
        if e is not None and e.read_memory_with("Leader") == 2:
            particle.write_to_with(e, "Leader", 1)
            e.set_color(4)
