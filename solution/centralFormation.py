import math
import solution.leader as leader
from solution.help_methods import add_random_particle

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

amount = 0

placed_particles = []
graph = {}
path = []

def solution(sim):
    global path
    print("Runde = ", sim.get_actual_round())
    if (sim.get_actual_round() == 1):
        initialize(sim)

    if sim.config_data.dynamic == 1 and sim.get_actual_round() == 3:
        new = add_random_particle(sim)
        new.write_memory_with("Dir", None)

    if (sim.get_actual_round() % 2 == 1):
        # calculation for movement
        calc_placed_particles(sim)
        particle = which_particle_to_move()
        create_graph(sim)

        if particle != None:
            calc_move(particle)
    else:
        move_and_refresh(path)
        delete_structures()
        is_formed(sim)

def calc_move(particle):
    global path
    spantree = create_spantree(particle)
    leafs = get_leafs(spantree)

    for leaf in leafs:
        if leaf not in placed_particles:
            path = find_shortest_path(spantree, particle, leaf)
            for particle in path:
                particle.set_color(8)
            write_replace_directions(1, path)
            return

def initialize(sim):

    global amount
    for particle in sim.get_particle_list():
        particle.write_memory_with("Dir", None)
        amount = amount + 1

    centerParticle = leader.get_random_particle(sim.get_particle_list())
    centerPos = centerParticle.coords

    form = sim.config_data.formation


    if form == 1:
        create_markersH(sim, centerPos)
    elif form == 2:
        create_markersS(sim, centerPos)
    elif form == 3:
        create_markersT(sim, centerPos)
    elif form == 4:
        create_markersL(sim, centerPos)

# triangle formula
def create_markersT(sim, pos):
    d = 0
    markerCount = 0
    particleCount = amount
    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)

        while i <= d:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if markerCount < particleCount:
                sim.add_marker(x, y)
            else:
                return
            markerCount = markerCount + 1
            i = i + 1
        d = d + 1

# line formula
def create_markersL(sim, pos):
    markerCount = 0
    particleCount = amount

    while markerCount < particleCount:
        x = pos[0] + (1*markerCount)
        y = pos[1]

        if markerCount < particleCount:
                sim.add_marker(x, y)
                markerCount = markerCount + 1

# square formula
def create_markersS(sim, pos):
    n = math.ceil(math.sqrt(amount))

    d = 0
    markerCount = 0
    particleCount = amount

    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)
        while i < n:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if markerCount < particleCount:
                sim.add_marker(x, y)
                markerCount = markerCount + 1
            else:
                return
            i = i + 1
        d = d+1

# hexagon formula
def create_markersH(sim, pos):
    markerCount = 0
    particleCount = amount

    positions = [pos]

    i = 0

    while markerCount < particleCount:
        current_pos = positions[i]

        dir = 0
        while dir < 6:
            new_coords = sim.get_coords_in_dir(current_pos, dir)
            positions.append(new_coords)
            dir = dir + 1

        if sim.get_marker_map_coords().get(current_pos) == None:
            sim.add_marker(current_pos[0], current_pos[1])
            markerCount = markerCount + 1
        i = i+1


###########################################

def which_particle_to_move():
    for particle in placed_particles:
        i = 0
        while i < 6:
            if particle.get_marker_in(i) is not None and particle.get_particle_in(i) is None:
                particle.write_memory_with("Dir", i)
                return particle
            i = i + 1

# creates graph
def create_graph(sim):
    for particle in sim.get_particle_list():
        nbs = particle.scan_for_particle_within(1)
        neighs = []
        for nb in nbs:
            neighs.append(nb)
        graph.update({particle: neighs})

# creates span tree with Breadth-First-Search
def create_spantree(particle):
    new_graph = {}

    explored = []
    queue = [particle]

    while queue:
        node = queue.pop(0)
        if node not in explored:
            nbs = graph[node]

            dict = []
            for nb in nbs:
                if nb not in queue and nb not in explored:
                    dict.append(nb)

            queue = queue + dict
            new_graph.update({node: dict})
            explored.append(node)

    return new_graph

def get_leafs(spantree):

    leafs = []

    for key in spantree.keys():
        # this key (number) is a leaf
        if spantree.get(key) == []:
            leafs.append(key)

    return leafs

# copied from https://www.geeksforgeeks.org/generate-graph-using-dictionary-python/
def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

###################################################################

def write_replace_directions(index, path):
    if index < len(path):
        dir = calc_dir(path[index-1], path[index])
        path[index].write_memory_with("Dir", dir)
        return write_replace_directions(index+1, path)

# calculates how p2 has to move to replace p1
def calc_dir(p1, p2):
    i = 0
    while i < 6:
        tmp = p2.get_particle_in(i)
        if tmp == p1:
            return i
        i = i + 1

######################################################################

def move_and_refresh(path):
    index = 0
    while index < len(path):
        path[index].move_to(path[index].read_memory_with("Dir"))
        path[index].write_memory_with("Dir", None)
        path[index].set_color(1)
        index = index + 1

#####################################################################

def delete_structures():
    placed_particles.clear()
    graph.clear()
    path.clear()

def calc_placed_particles(sim):
    for particle in sim.get_particle_list():
        if particle.check_on_marker():
            placed_particles.append(particle)

def is_formed(sim):
    for particle in sim.get_particle_list():
        if not particle.check_on_marker():
            return
    sim.success_termination()
