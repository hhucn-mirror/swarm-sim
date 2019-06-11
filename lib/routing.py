from enum import Enum
from lib.comms import send_message, CommEvent


class Algorithm(Enum):
    Epidemic = 0


class RoutingParameters:

    def __init__(self, algorithm, scan_radius):
        self.algorithm = algorithm
        self.scan_radius = scan_radius

    def set(self, particle):
        setattr(particle, "routing_params", self)


def next_step(particle, scan_radius=None):
    routing_params = getattr(particle, "routing_params")

    if scan_radius is None:
        scan_radius = routing_params.scan_radius

    if routing_params.algorithm == Algorithm.Epidemic:
        return __next_step_epidemic__(particle, scan_radius)


def __next_step_epidemic__(particle, scan_radius):
    nearby = particle.scan_for_particle_within(hop=scan_radius)
    if nearby is not None:
        for neighbour in nearby:
            # first check if we've got a message for this exact neighbour
            if neighbour.get_id() in particle.send_store:
                for message_key in particle.send_store[neighbour.get_id()]:
                    try:
                        message = particle.send_store[message_key]
                        comm_event = send_message(particle, message, neighbour)
                        __success_event__(particle, neighbour, message, comm_event)
                    except KeyError:
                        pass


def __success_event__(sender, receiver, message, event):
    if event == CommEvent.MessageDeliveredDirect:
        message.original_sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered=1, messages_received=1)
    elif event == CommEvent.MessageDelivered:
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered=1, messages_received=1)
    elif event == CommEvent.MessageForwarded:
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_forwarded=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_forwarded=1, messages_received=1)
    elif event == CommEvent.MessageTTLExpired:
        sender.sim.csv_round_writer.update_metrics(message_ttl_expired=1)
