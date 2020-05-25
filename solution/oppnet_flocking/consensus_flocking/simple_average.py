import logging

from lib.oppnet import routing
from lib.oppnet.mobility_model import MobilityModel


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    # send direction every round
    send_current_directions(particles)
    # route messages every round
    if current_round > 1:
        routing.next_step(particles)
    # move only after all messages should have propagated
    if current_round % (world.config_data.routing_parameters.scan_radius + 1) == 0:
        move_to_next_direction(particles)


def send_current_directions(particles):
    for particle in particles:
        particle.update_current_neighbourhood()
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
        particle.set_average_direction()
        next_direction = particle.mobility_model.next_direction(particle.coordinates)

        if next_direction:
            particle_directions[particle] = next_direction
        else:
            logging.debug("round {}: simple_average -> particle {} did not return a direction.".format(
                particle.world.get_actual_round(), particle.number))
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
