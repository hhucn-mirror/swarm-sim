import logging
import random

from lib.oppnet import routing
from lib.oppnet.mobility_model import MobilityModel


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    if current_round == 1:
        send_current_directions(particles)
    elif current_round % 5 == 1:
        routing.next_step(particles)
        move_to_next_direction(particles)
    elif current_round % 5 == 0:
        # pick a random sample of particles to choose a new direction
        particles_subset = random.sample(particles, round(len(particles) * 0.55))
        set_random_directions(particles_subset)
        # only the subset sends their current directions
        send_current_directions(particles_subset)
    else:
        routing.next_step(particles)
        move_to_next_direction(particles)
        send_current_directions(particles)


def send_current_directions(particles):
    for particle in particles:
        particle.check_current_neighbourhood()
        particle.send_direction_message()


def set_random_directions(particles):
    for particle in particles:
        particle.mobility_model.current_dir = MobilityModel.random_direction()
        print("round {}: updated particle {} direction {}".format(particle.world.get_actual_round(), particle.number,
                                                                  particle.mobility_model.current_dir))


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        particle.set_most_common_direction()
        next_direction = particle.mobility_model.next_direction(particle.coordinates)
        if next_direction:
            particle_directions[particle] = next_direction
        else:
            logging.debug("round {}: common_consensus -> particle {} did not return a direction.".format(
                particle.world.get_actual_round(), particle.number))
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
