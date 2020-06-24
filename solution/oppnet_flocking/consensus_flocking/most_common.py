import logging

from lib.oppnet import routing
from lib.oppnet.mobility_model import MobilityModel
from lib.swarm_sim_header import red, black


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    # send direction every round
    send_current_directions(particles)

    if current_round == 1:
        query_relative_locations(particles)
    # route messages every other round
    else:
        routing.next_step(particles)
        relative_location_propagated = current_round % (world.config_data.flock_radius * 2 + 10)
        if relative_location_propagated == 0:
            try_and_fill_flock_holes(particles)
            move_to_next_direction(particles)
        if relative_location_propagated == 1:
            query_relative_locations(particles)
    # move only after all messages should have propagated
    if current_round % (world.config_data.routing_parameters.scan_radius + 1) == 0:
        move_to_next_direction(particles)


def update_particle_neighbourhoods(particles):
    for particle in particles:
        particle.update_current_neighborhood()


def query_relative_locations(particles):
    for particle in particles:
        particle.query_relative_location()


def try_and_fill_flock_holes(particles):
    for particle in particles:
        particle.try_and_fill_flock_holes()


def log_relative_locations(particles):
    for particle in particles:
        relative = particle.relative_flock_location
        actual = particle.coordinates

        if actual != relative:
            particle.set_color(red)
        else:
            particle.set_color(black)


def send_current_directions(particles):
    for particle in particles:
        particle.update_current_neighborhood()
        particle.send_direction_message()


def set_random_direction(particles):
    random_direction = MobilityModel.random_direction()
    for particle in particles:
        particle.mobility_model.current_dir = random_direction
        print("round {}: updated particle {} direction {}".format(particle.world.get_actual_round(), particle.number,
                                                                  particle.mobility_model.current_dir))


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        # particle.set_most_common_direction(weighted_choice=False, centralisation_force=False)
        next_direction = particle.mobility_model.next_direction(particle.coordinates)
        if next_direction:
            particle_directions[particle] = next_direction
        else:
            logging.debug("round {}: common_consensus -> particle {} did not return a direction.".format(
                particle.world.get_actual_round(), particle.number))
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
