from enum import Enum

from lib.colors import Colors
from lib.comms import send_message, CommEvent


class Algorithm(Enum):
    Epidemic = 0,
    Epidemic_MANeT = 1


class MANeTRole(Enum):
    Router = 0,
    Node = 1


class RoutingParameters:

    def __init__(self, algorithm, scan_radius, manet_role=None, manet_group=0):
        self.algorithm = algorithm
        self.manet_role = manet_role
        self.manet_group = manet_group
        if manet_role is None:
            self.manet_role = MANeTRole.Node
        self.scan_radius = scan_radius

    def set(self, particle):
        setattr(particle, "routing_params", self)

    @staticmethod
    def get(particle):
        return getattr(particle, "routing_params")

    @staticmethod
    def same_manet_group(particle1, particle2):
        rp1, rp2 = RoutingParameters.get(particle1), RoutingParameters.get(particle2)
        return rp1.manet_group == rp2.manet_group


def next_step(particle, scan_radius=None):
    routing_params = RoutingParameters.get(particle)

    if scan_radius is not None:
        routing_params.scan_radius = scan_radius

    if routing_params.algorithm == Algorithm.Epidemic:
        __next_step_epidemic__(particle, routing_params)
    elif routing_params.algorithm == Algorithm.Epidemic_MANeT:
        __next_step_epidemic_manet__(particle, routing_params)


def __next_step_epidemic__(particle, routing_params, nearby=None):
    if nearby is None:
        nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
        if nearby is None:
            return

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


def __next_step_epidemic_manet__(particle, routing_params):
    nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
    if nearby is None:
        return

    if routing_params.manet_role == MANeTRole.Node:
        nearby = [neighbour for neighbour in nearby if RoutingParameters.same_manet_group(particle, neighbour)]
        __next_step_epidemic__(particle, routing_params, nearby)

    elif routing_params.manet_role == MANeTRole.Router:
        __next_step_epidemic__(particle, routing_params)


def __success_event__(sender, receiver, message, event):
    if event == CommEvent.MessageDeliveredDirect:
        message.original_sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered_directly=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered_directly=1, messages_received=1)
        receiver.set_color(Colors.green.value)
    elif event == CommEvent.MessageDelivered:
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_delivered=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_delivered=1, messages_received=1)
        receiver.set_color(Colors.green.value)
    elif event == CommEvent.MessageForwarded:
        sender.csv_particle_writer.write_particle(messages_sent=1, messages_forwarded=1)
        receiver.csv_particle_writer.write_particle(messages_received=1)
        sender.sim.csv_round_writer.update_metrics(messages_sent=1, messages_forwarded=1, messages_received=1)
        sender.set_color(Colors.blue.value)
    elif event == CommEvent.MessageTTLExpired:
        sender.sim.csv_round_writer.update_metrics(message_ttl_expired=1)
    elif event == CommEvent.ReceiverOutOfMem:
        sender.sim.csv_round_writer.update_metrics(receiver_out_of_mem=1)
        sender.set_color(Colors.red.value)
