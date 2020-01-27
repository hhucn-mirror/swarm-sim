import random

from lib.oppnet import routing
from lib.oppnet.leader_flocking.helper_classes import FlockMemberType
from lib.swarm_sim_header import red
from solution.oppnet_flocking.leader_flocking.message_types.leader_message import LeaderMessageType

leader_count = 2


def solution(world):
    global leaders, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    t_wait = world.config_data.flock_radius * 2

    if current_round == 1:
        leaders, followers = split_particles(particles)
        initialise_leaders(t_wait)
    else:
        update_leader_states()
        routing.next_step(particles)
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
    left_bound = t_wait * 3 + 1
    right_bound = left_bound * (leader_count + 1)
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


def send_direction_proposals(current_round):
    for leader in leaders:
        if leader.next_direction_proposal_round == current_round:
            leader.send_direction_proposal()


def move_to_next_direction(particles):
    particle_directions = {}
    first_direction = particles[0].next_moving_direction()
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction
            if first_direction and next_direction != first_direction:
                print("multi_leader_flocking -> move_to_next_direction()" +
                      "not all particles in the flock are moving to in the same direction!")
    if particle_directions:
        if len(particle_directions) != len(particles):
            print("multi_leader_flocking -> move_to_next_direction()" +
                  "not all particles returned a next_moving_direction()")
        particles[0].world.move_particles(particle_directions)
