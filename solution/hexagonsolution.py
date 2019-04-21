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
marked = []

def solution(sim, world):

    print("Runde = ",  sim.get_actual_round())
    if sim.get_actual_round() == 1:
        initialize(world)

    if sim.get_actual_round() % 2 == 1:
        look_for_all_leaders(world)

    if sim.get_actual_round() % 2 == 0:
        #every particle which has a direction in his memory should move
        #for particle in world.get_particle_list():
        appoint_leaders(leaders)
        for l in leaders:
            move_and_refresh_mem(l)
            marked.clear()

##################################################################################

def look_for_all_leaders(world):
    for leader in leaders:
    # Leader Particle directs one neighbour
        blocked_dir = [False, False, False, False, False, False]
        if leader.particle_in(NE): blocked_dir[0] = True
        if leader.particle_in(E): blocked_dir[1] = True
        if leader.particle_in(SE): blocked_dir[2] = True
        if leader.particle_in(SW): blocked_dir[3] = True
        if leader.particle_in(W): blocked_dir[4] = True
        if leader.particle_in(NW): blocked_dir[5] = True

        # neighbour directs his other neighbour to replace him
        if blocked_dir[0] == True and blocked_dir[1] == False and leader.get_particle_in(NE).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(NE), SE)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
        elif blocked_dir[1] == True and blocked_dir[2] == False and leader.get_particle_in(E).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(E), SW)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
        elif blocked_dir[2] == True and blocked_dir[3] == False and leader.get_particle_in(SE).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(SE), W)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
        elif blocked_dir[3] == True and blocked_dir[4] == False and leader.get_particle_in(SW).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(SW), NW)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
        elif blocked_dir[4] == True and blocked_dir[5] == False and leader.get_particle_in(W).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(W), NE)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
        elif blocked_dir[5] == True and blocked_dir[0] == False and leader.get_particle_in(NW).read_memory_with("Leader") != "True":
            indepth_writeout(leader.get_particle_in(NW), E)
            neighbour_of_(leader, marked[len(marked) - 1])
            return
# writes the direction per indepth search to the specific neighbours from the leader particle
def indepth_writeout(particle, dir):
    particle.write_memory_with("Mark", "True")
    marked.append(particle)
    particle.write_memory_with("Direction", dir)
    particle.set_color(3)

    neighbours = particle.scan_for_particle_in(hop=1)

    for nb in neighbours:
        if nb.read_memory_with("Leader") == "False" and nb.read_memory_with("Mark") == "False":
            direction = calc_dir(particle, nb)
            return indepth_writeout(nb, direction)

# returns direction from particle2 to particle1 so that particle2 can replace particle1 position
def calc_dir(particle1, particle2):
    # NE
    if(particle1.coords[0]-0.5 == particle2.coords[0]) & (particle1.coords[1]-1 == particle2.coords[1]):
        return NE
    # E
    if(particle1.coords[0]-1 == particle2.coords[0]) & (particle1.coords[1] == particle2.coords[1]):
        return E
    # SE
    if (particle1.coords[0]-0.5 == particle2.coords[0]) & (particle1.coords[1]+1 == particle2.coords[1]):
        return SE
    # SW
    if(particle1.coords[0]+0.5 == particle2.coords[0]) & (particle1.coords[1]+1 == particle2.coords[1]):
        return SW
    # W
    if(particle1.coords[0]+1 == particle2.coords[0]) & (particle1.coords[1] == particle2.coords[1]):
        return W
    # NW
    if(particle1.coords[0]+0.5 == particle2.coords[0]) & (particle1.coords[1]-1 == particle2.coords[1]):
        return NW

# initialize the first leader
def initialize(world):
    for particle in world.get_particle_list():
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Mark", "False")
        particle.write_memory_with("Direction", "None")
    leader = world.get_particle_list()[0]
    leader.write_memory_with("Leader", "True")
    leader.write_memory_with("Mark", "True")
    leaders.append(leader)

# move in the right order
def move_and_refresh_mem(leader):
    for leader in leaders:
        # Leader Particle directs one neighbour
        blocked_dir = [False, False, False, False, False, False]
        if leader.particle_in(NE): blocked_dir[0] = True
        if leader.particle_in(E): blocked_dir[1] = True
        if leader.particle_in(SE): blocked_dir[2] = True
        if leader.particle_in(SW): blocked_dir[3] = True
        if leader.particle_in(W): blocked_dir[4] = True
        if leader.particle_in(NW): blocked_dir[5] = True

        # neighbour directs his other neighbour to replace him
        if blocked_dir[0] == True and blocked_dir[1] == False and leader.get_particle_in(NE).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(NE))
        elif blocked_dir[1] == True and blocked_dir[2] == False and leader.get_particle_in(E).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(E))
        elif blocked_dir[2] == True and blocked_dir[3] == False and leader.get_particle_in(SE).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(SE))
        elif blocked_dir[3] == True and blocked_dir[4] == False and leader.get_particle_in(SW).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(SW))
        elif blocked_dir[4] == True and blocked_dir[5] == False and leader.get_particle_in(W).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(W))
        elif blocked_dir[5] == True and blocked_dir[0] == False and leader.get_particle_in(NW).read_memory_with("Leader") != "True":
            return move_indepth(leader.get_particle_in(NW))

def move_indepth(particle):
    #Only Marked Particles will move
    if particle.read_memory_with("Direction") != "None" and particle.read_memory_with("Mark") == "True":
        #get neighbour list before moving
        neighs = particle.scan_for_particle_within(hop=1)
        #move the particle
        dir = particle.read_memory_with("Direction")
        particle.move_to(dir)
        particle.write_memory_with("Direction", "None")
        particle.write_memory_with("Mark", "False")
        particle.set_color(1)

        #last on in the indepth search could have no neighbours
        if(neighs != None):
            for nb in neighs:
                 if nb.read_memory_with("Leader") == "False" and nb.read_memory_with("Mark") == "True":
                    return move_indepth(nb)

def appoint_leaders(leaders):
    for l in leaders:
        neighbours = l.scan_for_particle_within(hop=1)
        if len (neighbours) != 6:
            return

    next_leaders = []
    for l in leaders:
        neighbours = l.scan_for_particle_within(hop=1)
        for nb in neighbours:
            if nb.read_memory_with("Leader") == "False":
                nb.write_memory_with("Leader", "True")
                nb.write_memory_with("Mark", "True")
                next_leaders.append(nb)
    leaders.clear()
    leaders.extend(next_leaders)

def neighbour_of_(leader, particle):
    if particle != None:
        neighbours = particle.scan_for_particle_within(hop=1)

        for nb in neighbours:
            if leader == nb:
                particle.write_memory_with("Direction", "None")
                particle.write_memory_with("Mark", "False")
                particle.set_color(1)
                return True
        return False
