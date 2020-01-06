import lib.oppnet.routing
from lib.oppnet.communication import generate_random_messages

message_amount = 50


def solution(sim):
    particles = sim.get_particle_list()

    if sim.get_actual_round() == 1:
        # initially generate 5 message per particle
        generate_random_messages(particles, amount=2, sim=sim)
    else:
        # generate 1 message per particle, every 20 rounds
        # if sim.get_actual_round() % 20 == 0:
        #    generate_random_messages(particles, amount=1, sim=sim)
        #    print("Current round: {}".format(sim.get_actual_round()))
        # move in every round starting from the second one
        for particle in particles:
            next_direction = particle.mobility_model.next_direction(current_x_y=particle.coordinates)
            if next_direction is not False:
                particle.move_to(next_direction)

        lib.oppnet.routing.next_step(particles)
