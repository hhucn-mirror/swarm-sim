import random

from lib.oppnet.leader_flocking.opp_particle import FlockMemberType
from lib.swarm_sim_header import red


def solution(world):
    global leaders, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 2

    if current_round == 1:
        leaders, followers = split_particles(particles, 1)
        initialise_leaders(t_wait)
    else:
        process_received_messages()
        move_to_next_direction(particles)
        if current_round % t_pick == 0:
            initialise_leaders(t_wait)


def set_t_wait_values(t_wait):
    for particle in leaders:
        particle.set_t_wait(t_wait)


def split_particles(particles, leader_count):
    leader_set = set(random.sample(particles, leader_count))
    follower_set = set(particles).difference(leader_set)
    return leader_set, follower_set


def initialise_leaders(t_wait):
    set_t_wait_values(t_wait)
    for leader in leaders:
        leader.set_color(red)
        leader.set_flock_member_type(FlockMemberType.leader)
        leader.broadcast_direction_proposal()


def process_received_messages():
    for follower in followers:
        follower.process_received_messages()
        next_instruct_message = follower.get_current_instruct()
        if next_instruct_message:
            follower.broadcast_received_content(next_instruct_message)


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
