import random

from lib.oppnet.communication import broadcast_message, Message
from .message_types.leader_message import LeaderMessageContent, LeaderMessageType

radius = 2
t_wait = 2 * radius


def solution(world):
    current_round = world.get_actual_round()
    particles = set(world.get_particle_list())
    dirs = world.grid.get_directions_dictionary()

    if current_round == 1:
        leaders, followers = split_particles(particles, 1)
        initialise_leaders(leaders, dirs)


def split_particles(particles, leader_count):
    leaders = set(random.sample(particles, leader_count))
    followers = particles.difference(leaders)
    return leaders, followers


def initialise_leaders(leaders, dirs):
    for leader in leaders:
        proposed_direction = random.choice(dirs)
        broadcast_direction_proposal(leader, leader, proposed_direction)


def broadcast_direction_proposal(sender, leader, proposed_direction):
    max_hops = leader.routing_parameters.scan_radius
    neighbours = leader.scan_for_particles_in(hop=max_hops)

    for hop in range(1, max_hops + 1):
        receivers = leader.scan_for_particles_in(hop=hop)
        content = LeaderMessageContent(leader, proposed_direction, receivers, t_wait - hop + 1,
                                       LeaderMessageType.instruct)
        broadcast_message(sender, neighbours, content)


def broadcast_received_content(sender, received: Message):
    received_content = received.get_content()
    if isinstance(received_content, LeaderMessageContent):
        max_hops = sender.routing_parameters.scan_radius
        neighbours = sender.scan_for_particles_in(hop=max_hops)

        for hop in range(1, max_hops + 1):
            receivers = sender.scan_for_particles_in(hop=hop)
            content = received_content.create_forward_copy(neighbours, hop)
            broadcast_message(sender, receivers, content)


def forward_all_received(followers):
    for follower in followers:
        received_messages = followers.get_all_received()
        for received_message in received_messages:
            broadcast_received_content(follower, received_message)
