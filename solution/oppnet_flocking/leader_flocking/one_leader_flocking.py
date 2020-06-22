import random

from lib.oppnet import routing
from lib.oppnet.message_types import LeaderMessageType
from lib.oppnet.particles import FlockMemberType
from lib.swarm_sim_header import red


def solution(world):
    global leader, followers, individual_flag

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 5

    if current_round == 1:
        leader, followers = split_particles(particles, 1)
        initialise_leaders(t_wait)
        individual_flag = True
    else:
        routing.next_step(particles)
        move_to_next_direction(particles)
        if current_round % 30 == 0:
            individual_flag = True
            leader.broadcast_safe_location()
        if current_round % t_pick == 0:
            send_new_instruct()
            individual_flag = False


def split_particles(particles, leader_count):
    leader_particle = random.sample(particles, leader_count)[0]
    follower_set = set(particles).difference({leader_particle})
    return leader_particle, follower_set


def initialise_leaders(t_wait):
    leader.set_t_wait(t_wait)
    leader.set_color(red)
    leader.set_flock_member_type(FlockMemberType.leader)
    leader.broadcast_safe_location()


def send_new_instruct():
    leader.choose_direction(True)
    leader.multicast_leader_message(LeaderMessageType.instruct)


def move_to_next_direction(particles):
    if individual_flag:
        for particle in particles:
            next_direction = particle.next_moving_direction()
            if next_direction:
                particle.move_to(next_direction)
    else:
        particle_directions = {}
        for particle in particles:
            next_direction = particle.next_moving_direction()
            if next_direction:
                particle_directions[particle] = next_direction
        if particle_directions:
            particles[0].world.move_particles(particle_directions)
