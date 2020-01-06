import random

from lib.std_lib import get_next_dir_to


def next_intended_direction(particles):
    intended_direction = {}
    for particle, most_one_hop_location in most_neighbours_locations(particles).items():
        if most_one_hop_location is not None:
            intended_direction[particle] = direction_from_location_neighbour(particle, most_one_hop_location)
        else:
            intended_direction[particle] = random.choices(["NE", "E", "SE", "SW", "NW", "W"])[0]
    return intended_direction


def initialisation(sim):
    particles = sim.get_particle_list()
    initialise_particles(particles)


def initialise_particles(particles):
    intended = {}
    for particle in particles:
        intended[particle] = "NE"
    return intended


def most_neighbours_locations(particles):
    most_neighbours = {}
    for particle in particles:
        two_hop = particle.scan_for_particles_in(hop=2)
        two_hop_locations = locations_from_particles(two_hop)
        most_one_hop_location = most_one_hop_neighbours_location(particle, two_hop_locations)
        most_neighbours[particle] = most_one_hop_location
    return most_neighbours


def locations_from_particles(particles):
    if particles is None:
        return set([])
    return set([p.coordinates for p in particles])


def direction_from_location_neighbour(particle, neighbour_location):
    (p_x, p_y, _) = particle.coordinates
    (n_x, n_y, _) = neighbour_location
    return get_next_dir_to(p_x, p_y, n_x, n_y)


def most_one_hop_neighbours_location(particle, two_hop_locations):
    one_hop_locations = neighbour_locations(particle.coordinates, 1)
    most_one_hop_neighbours = set([])
    most_neighbours_location = None
    for neighbour_location in one_hop_locations:
        # for every one_hop location surrounding the particle, calculate the surrounding locations
        surroundings = neighbour_locations(neighbour_location, 1)
        # intersect two_hop neighbours with all two_hop neighbours
        two_hop_intersect = set(two_hop_locations).intersection(surroundings)
        if len(two_hop_intersect) > len(most_one_hop_neighbours):
            most_one_hop_neighbours = two_hop_intersect
            most_neighbours_location = neighbour_location
    return most_neighbours_location


def neighbour_locations(centre, radius):
    locations = set([])
    displacement = - radius + 0.5
    iteration = 0
    for i in range(1, radius + 1):
        locations.add((i, centre[1], 0))
        locations.add((-i, centre[1], 0))
    for i in range(1, radius + 1):
        for j in range(0, (2 * radius) - iteration):
            locations.add((displacement + j + centre[0], i + centre[1], 0))
            locations.add((displacement + j + centre[0], -i + centre[1], 0))
        iteration = iteration + 1
        displacement = displacement + 0.5
    return locations
