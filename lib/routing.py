from enum import Enum
from lib.comms import send_message


class Algorithm(Enum):
    Epidemic = 0


class RoutingParameters:

    def __init__(self, algorithm, scan_radius):
        self.algorithm = algorithm
        self.scan_radius = scan_radius


def next_step(particle, scan_radius=None):
    routing_params = getattr(particle, "routing_params")

    if scan_radius is None:
        scan_radius = routing_params.scan_radius

    if getattr(particle, "algorithm") == Algorithm.Epidemic:
        return __next_step_epidemic__(particle, scan_radius)


def __next_step_epidemic__(particle, scan_radius):
    nearby = particle.scan_for_particle_within(hop=scan_radius)
    for neighbour in nearby:
        # first check if we've got a message for this exact neighbour
        if neighbour.get_id() in particle.send_store:
            for message_key in particle.send_store[neighbour.get_id()]:
                send_message(particle, particle.send_store[message_key], neighbour)

