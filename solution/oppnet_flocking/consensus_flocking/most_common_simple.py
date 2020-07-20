import logging
import math

from lib.oppnet import routing
from lib.oppnet.mobility_model import MobilityModel
from lib.swarm_sim_header import red, black


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    t_pick = world.config_data.flock_radius * 10

    reset_neighborhood_counters(particles)

    if current_round == 1:
        world.csv_flock_round.add_flock(particles)
        query_relative_locations(particles)
    # route messages every round
    else:
        routing.next_step(particles)

    # send direction every round
    if current_round % t_pick == 0 or current_round == world.config_data.flock_radius * 2 + 1:
        send_random_next_directions(particles)
    else:
        send_current_directions(particles)
    if current_round > world.config_data.flock_radius * 3:
        move_to_next_direction(particles, world.config_data.weighted_choice, world.config_data.centralization_force)


def reset_neighborhood_counters(particles):
    for particle in particles:
        particle.reset_neighborhood_direction_counter()


def send_current_directions(particles):
    for particle in particles:
        particle.update_current_neighborhood()
        particle.send_direction_message(particle.mobility_model.current_dir)
        logging.debug("round {}: send current particle {} direction {}"
                      .format(particle.world.get_actual_round(), particle.number, particle.mobility_model.current_dir))


def send_random_next_directions(particles, split=.5):
    per_split = math.ceil(len(particles) * split)
    random_direction = MobilityModel.random_direction()
    for i, particle in enumerate(particles):
        if i % per_split == 0:
            random_direction = MobilityModel.random_direction()
        particle.update_current_neighborhood()
        particle.send_direction_message(random_direction)
        logging.debug("round {}: send next particle {} direction {}"
                      .format(particle.world.get_actual_round(), particle.number, random_direction))


def query_relative_locations(particles):
    for particle in particles:
        particle.query_relative_location()


def log_relative_locations(particles):
    for particle in particles:
        relative = particle.relative_flock_location
        actual = particle.coordinates

        if actual != relative:
            particle.set_color(red)
        else:
            particle.set_color(black)


def move_to_next_direction(particles, use_weighted_choice=True, use_centralization_force=False):
    particle_directions = {}
    for particle in particles:
        particle.set_most_common_direction(use_weighted_choice, use_centralization_force)
        next_direction = particle.mobility_model.current_dir
        if next_direction:
            particle_directions[particle] = next_direction
        else:
            logging.debug("round {}: common_consensus -> particle {} did not return a direction.".format(
                particle.world.get_actual_round(), particle.number))
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
