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
    check_round_message_assertions(sim, 2)


def check_round_message_assertions(sim, message_amount):
    expected_delivery_round = len(sim.get_particle_list())
    current_round = sim.get_actual_round()
    try:
        assert_sent_count(sim.csv_round_writer.get_messages_sent(), current_round, message_amount)
    except AssertionError:
        print("Sent Count assertion failed in round {}"
              .format(current_round))

    try:
        assert_forwarding_count(sim.csv_round_writer.get_messages_forwarded(), current_round, message_amount)
    except AssertionError:
        print("Forwarding Count assertion failed in round {}"
              .format(current_round))

    try:
        assert_delivery_count(sim.csv_round_writer.get_messages_delivered(), current_round, expected_delivery_round,
                              message_amount)
    except AssertionError:
        print("Delivery Count assertion failed in round {}"
              .format(current_round))


def assert_sent_count(sent_count, current_round, message_amount):
    expected = 1 + (current_round - 1) * 2 * message_amount
    assert sent_count == expected


def assert_forwarding_count(forwarding_count, current_round, message_amount):
    expected = message_amount if current_round > 1 else 0
    assert forwarding_count == expected


def assert_delivery_count(delivery_round, current_round, expected_delivery_round, message_amount):
    expected = message_amount if expected_delivery_round == current_round else 0
    assert delivery_round == expected
