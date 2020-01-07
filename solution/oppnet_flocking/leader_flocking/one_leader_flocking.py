from lib.oppnet.leader_flocking.opp_particle import FlockMemberType
from lib.swarm_sim_header import red

radius = 1
t_wait = 2 * radius + 1


def solution(world):
    global leaders, followers

    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    dirs = world.grid.get_directions_dictionary()

    if current_round == 1:
        leaders, followers = split_particles(particles, 1)
        initialise_leaders()
    else:
        update_t_wait_values(particles)
        process_received_messages()
        move_to_next_direction(particles)
        if current_round % 10 == 0:
            initialise_leaders()


def set_t_wait_values():
    for particle in leaders:
        particle.set_t_wait(t_wait)


def update_t_wait_values(particles):
    for particle in particles:
        particle.decrement_t_wait()


def split_particles(particles, leader_count):
    # leader_set = set(random.sample(particles, leader_count))
    leader_set = {particles[0]}
    follower_set = set(particles).difference(leader_set)
    return leader_set, follower_set


def initialise_leaders():
    set_t_wait_values()
    for leader in leaders:
        leader.set_color(red)
        leader.set_flock_member_type(FlockMemberType.leader)
        leader.broadcast_direction_proposal()


def process_received_messages():
    for follower in followers:
        received_messages = follower.get_all_received_messages()
        next_instruct_message = follower.next_instruct_from_messages(received_messages)
        if next_instruct_message:
            follower.broadcast_received_content(next_instruct_message)


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        next_direction = particle.next_moving_direction()
        if next_direction:
            particle_directions[particle] = next_direction

    particles[0].world.move_particles(particle_directions)
