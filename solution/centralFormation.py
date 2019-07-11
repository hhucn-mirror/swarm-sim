import math

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
        i = 0
        while i < len(placed_particles):
            print(placed_particles[i].coords)
            i = i+1

    if (sim.get_actual_round() % 2 == 1):
        # calculation for movement
        calc_placed_particles(sim)
        particle = which_particle_to_move(sim)
        create_graph(sim)
        if particle != None:
            spantree = create_spantree(particle)
            leafs = get_leafs(spantree)

            for leaf in leafs:
                if leaf not in placed_particles:
                    path = find_shortest_path(spantree, particle, leaf)
                    for particle in path:
                        particle.set_color(8)
                    write_replace_directions(1, path)
                    return


    else:
        move_and_refresh(path)
        delete_structures()

def initialize(sim):

    global amount
    for particle in sim.get_particle_list():
        particle.write_memory_with("Dir", None)
        amount = amount + 1

    centerParticle = sim.get_particle_list()[0]
    centerPos = centerParticle.coords

    #create_locationsT(sim, centerPos)
    #create_locationsL(sim, centerPos)
    #create_locationsS(sim, centerPos)
    create_locationsH(sim, centerPos)


# triangle formula
def create_locationsT(sim, pos):
    d = 0
    locationCount = 0
    particleCount = amount
    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)

        while i <= d:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if locationCount < particleCount:
                sim.add_location(x, y)
            else:
                return
            locationCount = locationCount + 1
            i = i + 1
        d = d + 1

# line formula
def create_locationsL(sim, pos):
    locationCount = 0
    particleCount = amount

    while locationCount < particleCount:
        x = pos[0] + (1*locationCount)
        y = pos[1]

        if locationCount < particleCount:
                sim.add_location(x, y)
        else:
            return
        locationCount = locationCount + 1

# square formula
def create_locationsS(sim, pos):
    n = round(math.sqrt(amount))
    d = 0
    locationCount = 0
    particleCount = amount

    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)
        while i < n:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if locationCount < particleCount:
                sim.add_location(x, y)
                locationCount = locationCount + 1
            else:
                return
            i = i + 1
        d = d+1

# hexagon formula
def create_locationsH(sim, pos):
    locationCount = 0
    particleCount = amount

    positions = [pos]

    i = 0
    while True:
        current_pos = positions[i]

        dir = 0
        while dir < 6:
            new_coords = sim.get_coords_in_dir(current_pos, dir)
            positions.append(new_coords)
            dir = dir + 1


        if locationCount < particleCount:
            if sim.get_location_map_coords().get(current_pos) == None:
                sim.add_location(current_pos[0], current_pos[1])
                locationCount = locationCount + 1
        else:
            return
        i = i+1


###########################################

def which_particle_to_move(sim):
    for particle in placed_particles:
        i = 0
        while i < 6:
            if particle.get_location_in(i) != None and particle.get_particle_in(i) == None:
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
        if particle.check_on_location():
            placed_particles.append(particle)
