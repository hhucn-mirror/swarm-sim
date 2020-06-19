import logging
import random

from lib.oppnet import routing
from lib.oppnet.leader_flocking.helper_classes import FlockMemberType
from lib.oppnet.message_types import LeaderMessageType
from lib.swarm_sim_header import red


def solution(world):
    global leaders, followers, individual_flag

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    t_wait = world.config_data.flock_radius * 2
    t_pick = t_wait * 5

    if current_round == 1:
        leader_count = world.config_data.leader_count
        leaders, followers = split_particles(particles, leader_count)
        set_t_wait_values(particles, t_wait)
        initialise_leaders(t_wait, leader_count)
        initialise_neighborhoods(particles)
        individual_flag = True
    else:
        check_neighborhoods(particles)
        routing.next_step(particles)
        update_particle_states(particles)
        # send_direction_proposals(current_round)
        if current_round == 5:
            print_all_routes(particles, current_round)
        # if current_round > t_wait * 3 + 1:
        #    move_to_next_direction(particles, current_round)
        move_to_next_direction(particles)
        if current_round % 30 == 0:
            individual_flag = True
            leader = random.choice(leaders)
            leader.send_safe_location_proposal()
        if current_round % t_pick == 0:
            send_direction_proposals(current_round)
            individual_flag = False


def print_all_routes(particles, current_round):
    for particle in particles:
        for target_particle, contacts in particle.leader_contacts.items():
            for contact in contacts.values():
                contact_particle = contact.get_contact_particle()
                logging.debug("round: {} route: #{} reaches #{} via #{} with {} hops".format(current_round,
                                                                                             particle.number,
                                                                                             target_particle.number,
                                                                                             contact_particle.number,
                                                                                             contact.get_hops()))


def set_t_wait_values(particles, t_wait):
    for particle in particles:
        particle.set_t_wait(t_wait)


def split_particles(particles, leader_count):
    leader_set = set(random.sample(particles, leader_count))
    follower_set = set(particles).difference(leader_set)
    return list(leader_set), follower_set


def initialise_leaders(t_wait, leader_count):
    left_bound = t_wait * 3 + 1
    right_bound = left_bound * (leader_count + 1)
    next_direction_proposal_rounds = range(left_bound, right_bound, left_bound)
    for index, leader in enumerate(leaders):
        leader.set_color(red)
        leader.set_flock_member_type(FlockMemberType.leader)
        # leader.set_next_direction_proposal_round(next_direction_proposal_rounds[index])
        leader.set_next_direction_proposal_round(left_bound * (index % 2 + 1))
        leader.multicast_leader_message(LeaderMessageType.discover)
        logging.debug("round 1: leader {} next_direction_proposal: {}".format(leader.number,
                                                                              leader.next_direction_proposal_round))


def initialise_neighborhoods(particles):
    for particle in particles:
        particle.init_neighborhood()


def check_neighborhoods(particles):
    for particle in particles:
        particle.update_current_neighborhood()


def update_particle_states(particles):
    for leader in leaders:
        leader.update_leader_states()
    for particle in particles:
        particle.update_free_locations()


def send_direction_proposals(current_round):
    for leader in leaders:
        if leader.next_direction_proposal_round == current_round:
            leader.send_direction_proposal()


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
