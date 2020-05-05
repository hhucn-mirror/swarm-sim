import logging
import random

from lib.oppnet import routing
from lib.oppnet.leader_flocking.helper_classes import FlockMemberType
from lib.oppnet.leader_flocking.message_types.leader_message import LeaderMessageType
from lib.swarm_sim_header import red


def solution(world):
    global leaders, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    t_wait = world.config_data.flock_radius * 2

    if current_round == 1:
        leader_count = world.config_data.leader_count
        leaders, followers = split_particles(particles, leader_count)
        set_t_wait_values(particles, t_wait)
        initialise_leaders(t_wait, leader_count)
        initialise_neighbourhoods(particles)
    else:
        check_neighbourhoods(particles)
        routing.next_step(particles)
        update_particle_states(particles)
        send_direction_proposals(current_round)
        if current_round == 5:
            print_all_routes(particles)
        if current_round > t_wait * 3 + 1:
            move_to_next_direction(particles, current_round)


def print_all_routes(particles):
    for particle in particles:
        for target_particle, contacts in particle.leader_contacts.items():
            for contact in contacts.values():
                contact_particle = contact.get_contact_particle()
                print("route: #{} reaches #{} via #{} with {} hops".format(particle.number, target_particle.number,
                                                                           contact_particle.number, contact.get_hops()))


def set_t_wait_values(particles, t_wait):
    for particle in particles:
        particle.set_t_wait(t_wait)


def split_particles(particles, leader_count):
    leader_set = set(random.sample(particles, leader_count))
    follower_set = set(particles).difference(leader_set)
    return leader_set, follower_set


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
        print("leader {} next_direction_proposal: {}".format(leader.number, leader.next_direction_proposal_round))


def initialise_neighbourhoods(particles):
    for particle in particles:
        particle.init_neighbourhood()


def check_neighbourhoods(particles):
    for particle in particles:
        particle.check_current_neighbourhood()


def update_particle_states(particles):
    for leader in leaders:
        leader.update_leader_states()
    for particle in particles:
        particle.update_free_locations()


def send_direction_proposals(current_round):
    for leader in leaders:
        if leader.next_direction_proposal_round == current_round:
            leader.send_direction_proposal()


def move_to_next_direction(particles, current_round):
    particle_directions = {}
    first_direction = particles[0].next_moving_direction()
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction
            if first_direction and next_direction != first_direction:
                logging.error("round {}: multi_leader_flocking -> move_to_next_direction() " +
                              "not all particles in the flock are moving to in the same direction!".format(
                                  current_round))
    if particle_directions:
        if len(particle_directions) != len(particles):
            logging.error("round {}: multi_leader_flocking -> move_to_next_direction() " +
                          "not all particles returned a next_moving_direction()".format(current_round))
        particles[0].world.move_particles(particle_directions)
