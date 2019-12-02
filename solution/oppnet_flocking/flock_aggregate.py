from lib.particle import NE, NW, E, W, SE, SW


def aggregate(intended_directions):
    aggregate_directions = {}
    for particle, intended_direction in intended_directions.items():
        aggregate_directions[particle] = aggregate_direction(particle, intended_directions)
        print("next aggregate direction for particle at {} is {}"
              .format(particle.coords, aggregate_directions[particle]))
    return aggregate_directions


def aggregate_direction(particle, intended_directions):
    neighbours = neighbourhood(particle)
    direction_counts = {NE: 0, NW: 0, E: 0, W: 0, SE: 0, SW: 0}
    if not neighbours:
        return -1
    for neighbour in neighbours:
        neighbour_intended = intended_directions[neighbour]
        if neighbour_intended in direction_counts.keys():
            direction_counts[neighbour_intended] += 1
    particle_intended = intended_directions[particle]
    if particle_intended in direction_counts.keys():
        direction_counts[particle_intended] += 1
    return most_counts(direction_counts)


def most_counts(direction_counts):
    highest_count = 0
    aggregate_dir = None
    for direction, direction_count in direction_counts.items():
        if direction_count > highest_count:
            highest_count = direction_count
            aggregate_dir = direction
    return aggregate_dir


def neighbourhood(particle):
    return particle.scan_for_particle_within(hop=1)
