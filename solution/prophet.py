import lib.oppnet.routing
from lib.oppnet import routing
from lib.oppnet.communication import generate_random_messages

new_message_interval = 10
messages_per_interval = 2


def solution(world):
    particles = world.get_particle_list()
    config_data = world.config_data

    current_round = world.get_actual_round()
    if world.get_actual_round() == 1:
        # initially generate messages per particle
        generate_random_messages(particles, messages_per_interval, world)
        initialize_delivery_probabilities(particles)
    else:
        # generated new messages per particle
        if current_round % new_message_interval == 0:
            generate_random_messages(particles, amount=messages_per_interval, world=world)
        # move in every round starting from the second one
        for particle in particles:
            next_direction = particle.mobility_model.next_direction(current_x_y_z=particle.coordinates)
            if next_direction is not False:
                particle.move_to(next_direction)

        lib.oppnet.routing.next_step(particles)


def initialize_delivery_probabilities(particles):
    for particle in particles:
        p_init = particle.routing_parameters.p_init
        # create a dictionary of probability dictionaries for each particle
        # and each possible encountering particle
        probabilities = {}
        for encounter in particles:
            # the list [prob, age] contains the probability and the age of the last encounter
            probabilities[encounter.get_id()] = (p_init, 0)
        particle.write_to_with(target=particle, key=routing.PROB_KEY, data=probabilities)
