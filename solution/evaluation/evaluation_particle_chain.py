from lib.oppnet.communication import Message
from lib.oppnet.routing import RoutingParameters, next_step


def solution(sim):
    particles = sim.get_particle_list()
    current_round = sim.get_actual_round()
    global message_left_right, message_right_left

    if current_round == 1:
        # initialize the routing parameters
        for particle in particles:
            r_params = RoutingParameters(algorithm=sim.routing_algorithm, scan_radius=sim.scan_radius,
                                         delivery_delay=sim.delivery_delay)
            r_params.set(particle)
        # create the messages
        left_particle = particles[0]
        right_particle = particles[-1]
        # send a message from the left most particle, to the right most particle
        message_left_right = Message(sender=left_particle, receiver=right_particle, start_round=current_round,
                                     ttl=sim.message_ttl)
        # vice versa
        message_right_left = Message(sender=right_particle, receiver=left_particle, start_round=current_round,
                                     ttl=sim.message_ttl)
    # execute the next routing step
    next_step(particles)

    # check the assertions
    if check_message_assertions(sim):
        print("All the assertions for both message statistics passed in round: {}. Expected round: {}"
              .format(current_round, len(particles)))
        sim.set_end()


def check_message_assertions(sim):
    for message in [message_left_right, message_right_left]:
        # check if the formulas for message statistics are correct
        csv_message_data = sim.csv_round_writer.csv_msg_writer.get_csv_message_data(message)
        try:
            assert_message_statistics(csv_message_data, sim.get_actual_round(), len(sim.get_particle_list()))
        except AssertionError:
            return False
        return True


def assert_message_statistics(message_data, current_round, particle_count):
    assert message_data.get_sent_count() == __total_sent_count__(particle_count)
    assert message_data.get_forwarding_count() == __total_forwarding_count__(particle_count)
    assert message_data.get_delivery_count() == __total_delivery_count__()
    assert message_data.get_delivery_round() == __delivery_round__(particle_count)
    assert message_data.get_first_delivery_hops() == __first_delivery_hops(particle_count)


def __total_sent_count__(particle_count):
    total = 0
    for i in range(2, particle_count + 1):
        total += __max_sent_count(i)
    total += __max_sent_count(particle_count)

    return total


def __max_sent_count(particle_count):
    return 1 + (particle_count - 2) * 2


def __total_forwarding_count__(particle_count):
    return particle_count - 1


def __total_delivery_count__():
    return 1


def __delivery_round__(particle_count):
    return particle_count


def __first_delivery_hops(particle_count):
    return particle_count - 1
