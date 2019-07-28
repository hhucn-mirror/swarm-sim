import math
import solution.leader as leader

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
    if sim.get_actual_round() == 1:
        create_graph(sim)
        for x in graph:
            print("Particle", x.coords)
            for y in graph[x]:
                print("\t", y.coords)
            print()


# creates graph
def create_graph(sim):
    for particle in sim.get_particle_list():
        nbs = particle.scan_for_particle_within(1)
        neighs = []
        for nb in nbs:
            neighs.append(nb)
        graph.update({particle: neighs})


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