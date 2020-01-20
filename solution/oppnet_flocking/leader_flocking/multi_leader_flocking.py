import random

from lib.oppnet.leader_flocking.opp_particle import FlockMemberType
from lib.swarm_sim_header import red
from solution.oppnet_flocking.leader_flocking.message_types.leader_message import LeaderMessageType

leader_count = 2


def solution(world):
    global leaders, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 2

    if current_round == 1:
        leaders, followers = split_particles(particles)
        initialise_leaders(t_wait)
    else:
        update_leader_states()
        process_received_messages()
        send_direction_proposals(current_round)
        move_to_next_direction(particles)


def set_t_wait_values(t_wait):
    for particle in leaders:
        particle.set_t_wait(t_wait)


def split_particles(particles):
    leader_set = set(random.sample(particles, leader_count))
    follower_set = set(particles).difference(leader_set)
    return leader_set, follower_set


def initialise_leaders(t_wait):
    set_t_wait_values(t_wait)
    left_bound = t_wait * 2
    right_bound = left_bound + t_wait * 2 * leader_count + 1
    next_direction_proposal_rounds = random.sample(range(left_bound, right_bound, left_bound), leader_count)
    for index, leader in enumerate(leaders):
        leader.set_color(red)
        leader.set_flock_member_type(FlockMemberType.leader)
        leader.set_next_direction_proposal_round(next_direction_proposal_rounds[index])
        leader.broadcast_leader_message(LeaderMessageType.discover)
        print("leader {} next_direction_proposal: {}".format(leader.number, leader.next_direction_proposal_round))


def update_leader_states():
    for leader in leaders:
        leader.update_leader_states()


def process_received_messages():
    for particle in followers.union(leaders):
        particle.process_received_messages()


def send_direction_proposals(current_round):
    for leader in leaders:
        if leader.next_direction_proposal_round == current_round:
            leader.send_direction_proposal()


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
