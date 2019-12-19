from solution.oppnet_flocking.flock_aggregate import aggregate
from solution.oppnet_flocking.flock_centring import next_intended_direction, initialise_particles

intended = {}


def solution(world):
    global intended

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()

    if current_round == 1:
        intended = initialise_particles(particles)
    elif current_round % 2 == 1:
        intended = next_intended_direction(particles)
    else:
        aggregated = aggregate(intended)
        for particle, aggregate_direction in aggregated.items():
            if aggregate_direction != -1:
                direction = dirs[aggregate_direction]
                particle.move_to(direction)
