import random
import math
import configparser
from lib import config_data as cd


E = 0
SE = 1
SW = 2
W = 3
NW = 4
NE = 5

black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violet = 9

dirs = [E, SE, SW, W, NW, NE]
x_offset = [0.5, 1,  0.5, -0.5, -1, -0.5]
y_offset = [1, 0, -1, -1,  0, 1]

dirs_array = [[E, SE, SW, W, NW, NE],
              [SE, SW, W, NW, NE, E],
              [SW, W, NW, NE, E, SE],
              [W, NW, NE, E, SE, SW],
              [NW, NE, E, SE, SW, W],
              [NE, E, SE, SW, W, NW],
              [E, NE, NW, W, SW, SE],
              [NE, NW, W, SW, SE, E],
              [NW, W, SW, SE, E, NE],
              [W, SW, SE, E, NE, NW],
              [SW, SE, E, NE, NW, W],
              [SE, E, NE, NW, W, SW]]


# -1 = DFS, 0 = BFS
search_algorithms = [0]

graph = []
visited = []
unvisited_queue = []


# Variables for evaluation
all_marked = False
location_count = {"constricted_terrain": 363,
                  "square_terrain": 527,
                  "edgy_terrain": 315,
                  "crescent_terrain": 149}


class Location:
    def __init__(self, coords):
        self.coords = coords
        self.adjacent = []
        self.visited = False

    def __eq__(self, other):
        return self.coords == other.coords

    def __str__(self):
        return str(self.coords) + ' | Adjacent: ' + str([item.coords for item in self.adjacent])


# Checks if a location exists in a graph
def location_exists(graph, coords):
    for location in graph:
        if location.coords == coords:
            return True
    return False


# Returns the location from a graph given the coordinates
def get_location_with_coords(graph, coords):
    for location in graph:
        if location.coords == coords:
            return location
    return False


# Returns the direction of a location relative to the current location
def get_dir(current_location, target_location):
    if target_location.coords[0] == current_location.coords[0] + x_offset[0] and target_location.coords[1] == current_location.coords[1] + y_offset[0]:
        return 0

    if target_location.coords[0] == current_location.coords[0] + x_offset[1] and target_location.coords[1] == current_location.coords[1] + y_offset[1]:
        return 1

    if target_location.coords[0] == current_location.coords[0] + x_offset[2] and target_location.coords[1] == current_location.coords[1] + y_offset[2]:
        return 2

    if target_location.coords[0] == current_location.coords[0] + x_offset[3] and target_location.coords[1] == current_location.coords[1] + y_offset[3]:
        return 3

    if target_location.coords[0] == current_location.coords[0] + x_offset[4] and target_location.coords[1] == current_location.coords[1] + y_offset[4]:
        return 4

    if target_location.coords[0] == current_location.coords[0] + x_offset[5] and target_location.coords[1] == current_location.coords[1] + y_offset[5]:
        return 5


# Adds a new location to a graph
def add_location_to_graph(sim, graph, location):
    if location in graph:
        return

    graph.append(location)

    for direction in dirs:
        adjacent_location_coords = sim.get_coords_in_dir(location.coords, direction)
        if location_exists(graph, adjacent_location_coords):
            if location in get_location_with_coords(graph, adjacent_location_coords).adjacent:
                continue
            get_location_with_coords(graph, adjacent_location_coords).adjacent.append(location)


def random_walk(particle):
    dir = dirs.copy()
    new_dir = random.choice(dir)
    particle.move_to_in_bounds(new_dir)


# Checks if the given coordinates are valid simulator coordinates
def valid_sim_coords(sim, coords):
    if sim.check_coords(coords[0], coords[1]):
        sim_coord = sim.coords_to_sim(coords)
        if sim.get_sim_x_size() >= abs(sim_coord[0]) and sim.get_sim_y_size() >= abs(sim_coord[1]):
            return True

    return False


# Checks if the location at the given coordinates is a border or not
def is_border(sim, coords):
    for location in sim.get_location_list():
        if coords == location.coords:
            if location.color == [0, 0, 0]:
                return True
    return False


# Initializes the new custom particle attributes
def set_particle_attributes(particle):
    directions = dirs_array.copy()
    search_algo = search_algorithms.copy()

    direction = random.choice(directions)
    search_algorithm = random.choice(search_algo)

    setattr(particle, "direction", direction)
    setattr(particle, "search_algorithm", search_algorithm)

    setattr(particle, "origin_coords", particle.coords)
    setattr(particle, "start_location", Location(particle.origin_coords))

    setattr(particle, "current_location", particle.start_location)
    setattr(particle, "target_location", particle.start_location)  # just marks origin position for now

    setattr(particle, "last_visited_locations", [])
    setattr(particle, "stuck_locations", [])

    setattr(particle, "stuck", False)
    setattr(particle, "done", False)


# Discovers the adjacent (Neighbour) locations relative to the particle's current location
def discover_adjacent_locations(sim, particle):
    global graph
    global visited
    global unvisited_queue

    for direction in particle.direction:
        adjacent_location_coords = sim.get_coords_in_dir(particle.current_location.coords, direction)

        if not valid_sim_coords(sim, adjacent_location_coords):
            continue

        if is_border(sim, adjacent_location_coords):
            continue

        if location_exists(graph, adjacent_location_coords):
            if get_location_with_coords(graph, adjacent_location_coords) in particle.current_location.adjacent:
                continue
            particle.current_location.adjacent.append(get_location_with_coords(graph, adjacent_location_coords))
            continue

        new_location = Location(adjacent_location_coords)
        particle.create_location_on(adjacent_location_coords[0], adjacent_location_coords[1], color=blue)
        particle.current_location.adjacent.append(new_location)
        unvisited_queue.append(new_location)
        add_location_to_graph(sim, graph, new_location)


# Marks the particle's current location as visited and removes it from the particle's unvisited queue
def mark_location(sim, particle):
    global visited
    global unvisited_queue

    particle.current_location.visited = True
    visited.append(particle.current_location)
    particle.last_visited_locations.append(particle.current_location)
    unvisited_queue = [location for location in unvisited_queue if location not in visited]
    current_location = sim.get_location_map_coords()[particle.coords]

    if current_location.color == [0.0, 0.8, 0.8]:
        return

    particle.delete_location()
    particle.create_location(color=cyan)


# Returns the distance between 2 locations
def get_distance(location1, location2):
    x1 = location1.coords[0]
    x2 = location2.coords[0]

    y1 = location1.coords[1]
    y2 = location2.coords[1]

    return abs(math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2)))


# Returns the nearest location in the particle's unvisited queue relative to the particle's current location
def get_nearest_unvisited(particle):
    global unvisited_queue
    possible_unvisited_locations = []
    for location in unvisited_queue:
        possible_unvisited_locations.append((round(get_distance(particle.current_location, location)), location))

    return min(possible_unvisited_locations, key=lambda t: t[0])[1]


# Returns the next best possible move if the particle's target location is not adjacent to it (path generator)
def get_next_best_location(particle, target_location, stuck_locations):
    possible_moves = []
    all_moves = []

    for location in particle.current_location.adjacent:
        all_moves.append((get_distance(location, target_location), location))
        if location in stuck_locations:
            continue
        else:
            possible_moves.append((get_distance(location, target_location), location))

    best_location = min(possible_moves, key=lambda t: t[0])[1]

    return best_location


# Returns the next closest unvisited location relative to the particle's current location
def get_next_unvisited(particle):
    global unvisited_queue
    if unvisited_queue[particle.search_algorithm] not in particle.current_location.adjacent:
        return get_next_best_location(particle, get_nearest_unvisited(particle), particle.stuck_locations)

    else:
        particle.stuck_locations.clear()
        particle.last_visited_locations.clear()
        return unvisited_queue[particle.search_algorithm]


# Checks if the particle's next location is in a stuck cycle or not
def manage_stuck_locations(particle, next_location):
    if next_location in particle.last_visited_locations:
        if next_location in particle.stuck_locations:
            particle.stuck = True
            return True
        else:
            particle.stuck_locations.append(next_location)
            return False
    else:
        particle.last_visited_locations.append(next_location)
        return False


# Checks if all markable sim locations have already been marked
def check_all_marked(sim, scenario_location_count):
    all_locations = sim.get_location_list()
    marked_locations = [location for location in all_locations if location.color == [0.0, 0.8, 0.8]]

    if len(marked_locations) == scenario_location_count:
        return True


# Removes locations from the particle's stuck_locations list
def decay_stuck_location(particle):
    particle.last_visited_locations.clear()
    if particle.stuck_locations[-1] in particle.current_location.adjacent:
        particle.stuck_locations.pop(-1)
    else:
        particle.stuck_locations.pop(0)


# Handles the navigation of the particle through the terrain
def navigate(sim, particle, next_location):

    if manage_stuck_locations(particle, next_location):
        pass

    next_direction = get_dir(particle.current_location, next_location)
    particle.current_location = next_location
    discover_adjacent_locations(sim, particle)
    mark_location(sim, particle)
    particle.move_to(next_direction)


def solution(sim):
    global graph
    global visited
    global unvisited_queue

    global all_marked

    done_particles = 0

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    config_data = cd.ConfigData(config)
    scenario_name = config_data.scenario

    for particle in sim.get_particle_list():

        if sim.get_actual_round() == 1:
            set_particle_attributes(particle)
            particle.create_location_on(particle.origin_coords[0], particle.origin_coords[1], color=blue)
            add_location_to_graph(sim, graph, particle.current_location)
            discover_adjacent_locations(sim, particle)

        else:
            if not all_marked:
                if check_all_marked(sim, location_count[scenario_name]):
                    all_marked = True
                    sim.csv_round_writer.marking_success()
                    sim.csv_round_writer.set_marking_success_round(sim.get_actual_round())

            if len(unvisited_queue) > 0:
                try:
                    next_location = get_next_unvisited(particle)
                    navigate(sim, particle, next_location)

                except ValueError:
                    discover_adjacent_locations(sim, particle)
                    decay_stuck_location(particle)

            else:
                particle.current_location = get_location_with_coords(graph, particle.coords)
                discover_adjacent_locations(sim, particle)
                mark_location(sim, particle)

                if particle.current_location.coords == particle.target_location.coords:
                    if particle.done is False:
                        particle.csv_particle_writer.set_task_success_round(sim.get_actual_round())
                    particle.stuck_locations.clear()
                    particle.last_visited_locations.clear()
                    done_particles += 1
                    particle.done = True
                    continue

                else:
                    try:
                        next_location = get_next_best_location(particle, particle.target_location, particle.stuck_locations)
                        navigate(sim, particle, next_location)

                    except ValueError:
                        discover_adjacent_locations(sim, particle)
                        decay_stuck_location(particle)

    if done_particles == len(sim.get_particle_list()):
        sim.success_termination()

