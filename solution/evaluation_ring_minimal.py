from lib.oppnet.communication import Message
from lib.oppnet.routing import RoutingParameters, next_step


def solution(sim):
    particles = sim.get_particle_list()
    current_round = sim.get_actual_round()
    global message_top_down

    if current_round == 1:
        # initialize the routing parameters
        for particle in particles:
            r_params = RoutingParameters(algorithm=sim.routing_algorithm, scan_radius=sim.scan_radius,
                                         delivery_delay=sim.delivery_delay)
            r_params.set(particle)
        # create the messages
        sender = particles[0]
        receiver = particles[round(len(particles) / 2)]
        # send a message from the left most particle, to the right most particle
        message_top_down = Message(sender=sender, receiver=receiver, start_round=current_round,
                                   ttl=sim.message_ttl)
        print("Round: {} [] SentCounter: {}".format(sim.get_actual_round(),
                                                    calculate_send_count_round(sim.get_actual_round(), len(particles))
                                                    ))
        next_step(particles)


def calculate_send_count_round(round_count, particle_count):
    return particle_count * (2 + (round_count - 1) * 4)
