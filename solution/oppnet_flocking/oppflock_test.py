from solution.oppnet_flocking.flock_aggregate import aggregate
from solution.oppnet_flocking.flock_centring import next_intended_direction, initialise_particles

intended = {}


def solution(sim):
    global intended

    current_round = sim.get_actual_round()
    particles = sim.get_particle_list()

    if current_round == 1:
        intended = initialise_particles(particles)
    elif current_round % 2 == 1:
        intended = next_intended_direction(particles)
    else:
        aggregated = aggregate(intended)
        for particle, aggregate_direction in aggregated.items():
            if aggregate_direction != -1:
                particle.move_to(aggregate_direction)
