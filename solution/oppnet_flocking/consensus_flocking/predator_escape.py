import logging
import time

from lib.oppnet import routing


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    predators = world.get_predators_list()

    start = time.time()
    send_current_directions(particles)
    print("###################################################################")
    print("send_current_directions() took {} secs.".format(time.time() - start))
    if current_round == 1:
        query_relative_locations(particles)
    # route messages every other round
    else:
        if current_round == world.config_data.flock_radius * 2 + 1:
            add_predators(world, 1)
        if current_round % 30 == 0:
            activate_chase_mode(predators)
        elif current_round % 100 == 0:
            add_predators(world, 1)
        start = time.time()
        routing.next_step(particles)
        print("routing.next_step() took {} secs.".format(time.time() - start))
        relative_location_propagated = current_round > (world.config_data.flock_radius * 2 + 10)
        if relative_location_propagated:
            start = time.time()
            move_particles_to_next_direction(particles)
            move_predators_to_next_direction(predators)
            print("move() took {} secs.".format(time.time() - start))


def add_predators(world, amount):
    for _ in range(0, amount):
        x = world.config_data.flock_radius + world.config_data.predator_scan_radius * 3
        world.add_predator(coordinates=(x + _, 0, 0))
        world.add_predator(coordinates=(-x - _, 0, 0))


def query_relative_locations(particles):
    for particle in particles:
        particle.query_relative_location()


def move_predators_to_next_direction(predators):
    for predator in predators:
        predator.chase()


def activate_chase_mode(predators):
    for predator in predators:
        predator.activate_chase()


def send_current_directions(particles):
    for particle in particles:
        particle.send_direction_message()


def move_particles_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.get_next_direction()
        if next_direction:
            particle_directions[particle] = next_direction
        else:
            logging.debug("round {}: predator_test -> particle {} did not return a direction.".format(
                particle.world.get_actual_round(), particle.number))
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
