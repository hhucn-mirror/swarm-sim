import logging
import random

from lib.oppnet import routing
from lib.oppnet.message_types import LeaderMessageType
from lib.oppnet.mobility_model import MobilityModelMode
from lib.oppnet.particles import FlockMemberType, FlockMode
from lib.swarm_sim_header import red


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 5

    if current_round == 1:
        leader, _ = split_particles(particles, 1)
        world.add_leaders([leader])
        initialise_leader(t_wait, leader)
        world.csv_flock_round.add_flock(particles)
    else:
        leader = get_leader(world)
        routing.next_step(particles)
        move_to_next_direction(particles)
        if current_round % t_pick == 0:
            send_new_instruct(leader)
        predators_pursuit(world.get_predators_list())


def get_leader(world):
    leaders = world.leaders
    if len(leaders) > 1:
        logging.warning("round {}: more than one leader in one leader setting!".format(world.get_actual_round()))
    return leaders[0]


def predators_pursuit(predators):
    for predator in predators:
        predator.pursuit()


def split_particles(particles, leader_count):
    leader_particle = random.sample(particles, leader_count)[0]
    follower_set = set(particles).difference({leader_particle})
    return leader_particle, follower_set


def initialise_leader(t_wait, leader):
    leader.set_t_wait(t_wait)
    leader.set_color(red)
    leader.set_flock_member_type(FlockMemberType.Leader)
    leader.choose_direction(False)
    leader.multicast_leader_message(LeaderMessageType.instruct)


def send_new_instruct(leader):
    if leader.flock_mode == FlockMode.Flocking:
        leader.choose_direction(False)
        leader.multicast_leader_message(LeaderMessageType.instruct)
    else:
        leader.broadcast_safe_location(leader.coordinates)


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.get_next_direction()
        if next_direction:
            if particle.mobility_model.mode == MobilityModelMode.POI:
                particle.move_to(next_direction)
            else:
                particle_directions[particle] = next_direction
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
