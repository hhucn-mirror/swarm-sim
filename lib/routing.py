from enum import Enum

from lib.comms import Message, send_message
from lib.meta import NetworkEvent, EventType


class Algorithm(Enum):
    Epidemic = 0,
    Epidemic_MANeT = 1


class MANeTRole(Enum):
    Router = 0,
    Node = 1


class SendEvent:

    def __init__(self, messages, start_round, delay, store, sender, receiver):
        self.messages = messages
        self.start_round = start_round
        self.delay = delay
        self.store = store
        self.sender = sender
        self.receiver = receiver

    def fire_event(self):
        for m in self.messages:
            send_message(self.store, self.sender, self.receiver, m)


class RoutingParameters:

    def __init__(self, algorithm, scan_radius, manet_role=None, manet_group=0, delivery_delay=2):
        if type(algorithm) == str:
            self.mode = Algorithm[algorithm]
        else:
            self.algorithm = algorithm
        self.algorithm = algorithm
        self.manet_role = manet_role
        self.manet_group = manet_group
        if manet_role is None:
            self.manet_role = MANeTRole.Node
        self.scan_radius = scan_radius
        self.delivery_delay = delivery_delay
        self.send_events = []

    def create_event(self, messages, current_round, store, sender, receiver):
        for message in messages:
            sender.sim.event_queue.append(NetworkEvent(EventType.MessageSent, sender, receiver, current_round, message))
        return SendEvent(messages, current_round, self.delivery_delay, store, sender, receiver)

    def add_events(self, events):
        self.send_events.append(events)

    def get_next_events(self, current_round):
        if not self.send_events:
            return []
        send_events = self.send_events[0]
        if type(send_events[0]) == list:
            try:
                if send_events[0][0].start_round + send_events[0][0].delay == current_round:
                    self.send_events.pop(0)
                    return send_events
            except IndexError:
                return []
        else:
            try:
                if send_events[0].start_round + send_events[0].delay == current_round:
                    self.send_events.pop(0)
                    return send_events
            except IndexError:
                return []
        return []

    def set(self, particle):
        setattr(particle, "routing_params", self)

    @staticmethod
    def get(particle):
        return getattr(particle, "routing_params")

    @staticmethod
    def same_manet_group(particle1, particle2):
        rp1, rp2 = RoutingParameters.get(particle1), RoutingParameters.get(particle2)
        return rp1.manet_group == rp2.manet_group


def next_step(particle, current_round, scan_radius=None):
    routing_params = RoutingParameters.get(particle)

    if scan_radius is not None:
        routing_params.scan_radius = scan_radius

    if routing_params.algorithm == Algorithm.Epidemic:
        __next_step_epidemic__(particle, routing_params, current_round)
    elif routing_params.algorithm == Algorithm.Epidemic_MANeT:
        __next_step_epidemic_manet__(particle, routing_params, current_round)


def __next_step_epidemic__(particle, routing_params, current_round, nearby=None):
    __create_send_events__(particle, routing_params, current_round, nearby)
    # check for messages to send
    send_events = routing_params.get_next_events(current_round)
    if send_events:
        for send_event in send_events:
            if type(send_event) == list:
                for event in send_event:
                    event.fire_event()
            else:
                send_event.fire_event()
        routing_params.set(particle)


def __create_send_events__(particle, routing_params, current_round, nearby=None):
    if nearby is None:
        nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
        if nearby is None:
            return

    send_events = []
    fwd_events = []
    for neighbour in nearby:
        if list(particle.send_store):
            send_events.append(routing_params.create_event(list(particle.send_store),
                                                           current_round, particle.send_store, particle, neighbour))
        if list(particle.fwd_store):
            fwd_events.append(routing_params.create_event(list(particle.fwd_store),
                                                          current_round, particle.fwd_store, particle, neighbour))
    routing_params.add_events([send_events, fwd_events])
    routing_params.set(particle)


def __next_step_epidemic_manet__(particle, routing_params, current_round):
    nearby = particle.scan_for_particle_within(hop=routing_params.scan_radius)
    if nearby is None:
        return

    if routing_params.manet_role == MANeTRole.Node:
        nearby = [neighbour for neighbour in nearby if RoutingParameters.same_manet_group(particle, neighbour)]
        __next_step_epidemic__(particle, routing_params, nearby)

    elif routing_params.manet_role == MANeTRole.Router:
        __next_step_epidemic__(particle, routing_params, current_round)
