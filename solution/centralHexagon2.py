# test

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

leaders = []
graph = {}

def solution(sim):
    print("Runde = ",  sim.get_actual_round())
    if (sim.get_actual_round() == 1):
        initialize(sim)

    if (sim.get_actual_round() % 2 == 1):
        #print("Calc Movement")
        #calc_movement()
        create_graph(sim.get_particle_list())
        print(graph)
        print(create_spantree(leaders[0].number))
    else:
        print("Move and Refresh Memory")
        #move_and_refresh_mem()

##################################################################################

# initialize the first leader
def initialize(sim):
    for particle in sim.get_particle_list():
        particle.write_memory_with("Leader", "False")
        particle.write_memory_with("Mark", "False")
        particle.write_memory_with("Direction", "None")
    leader = sim.get_particle_list()[1]
    leader.set_color(8)
    leader.write_memory_with("Leader", "True")
    leaders.append(leader)

##################################################################################

# calcs which leader particle has to move cause it doesnt have the right amount of neighbours
def leader_has_to_move():
    for particle in leaders:
        if len(particle.scan_for_particle_within(1)) != 6:
            return particle

def create_graph(particleList):
    print("Create Graph of all particles")
    for particle in particleList:
        nbs = particle.scan_for_particle_within(1)
        neighs = []
        for nb in nbs:
            neighs.append(nb.number)
        graph.update({particle.number: neighs})


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

# creates span tree with Breadth-First-Search
def create_spantree(number):
    new_graph = {}

    explored = []
    queue = [number]

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
