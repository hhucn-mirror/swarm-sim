import random

from lib.oppnet import routing
from lib.oppnet.leader_flocking.helper_classes import FlockMemberType
from lib.oppnet.message_types import LeaderMessageType
from lib.swarm_sim_header import red


def solution(world):
    global leader, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 2

    if current_round == 1:
        leader, followers = split_particles(particles, 1)
        initialise_leaders(t_wait, current_round)
    else:
        routing.next_step(particles)
        move_to_next_direction(particles)
        if current_round % t_pick == 0:
            send_new_instruct(current_round)


def split_particles(particles, leader_count):
    leader_particle = random.sample(particles, leader_count)[0]
    follower_set = set(particles).difference({leader_particle})
    return leader_particle, follower_set


def initialise_leaders(t_wait, current_round):
    leader.set_t_wait(t_wait)
    leader.set_color(red)
    leader.set_flock_member_type(FlockMemberType.leader)
    leader.set_instruction_number(current_round)
    leader.choose_direction()
    leader.multicast_leader_message(LeaderMessageType.instruct)


def send_new_instruct(current_round):
    leader.set_instruction_number(current_round)
    leader.choose_direction()
    leader.multicast_leader_message(LeaderMessageType.instruct)


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
