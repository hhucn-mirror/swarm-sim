from lib.oppnet import routing


def solution(world):
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    send_current_directions(particles)
    routing.next_step(particles)
    move_to_next_direction(particles)


def send_current_directions(particles):
    for particle in particles:
        particle.send_direction_message()


def move_to_next_direction(particles):
    particle_directions = {}
    for particle in particles:
        particle.set_most_common_direction()
        next_direction = particle.mobility_model.next_direction(particle.coordinates)
        if next_direction:
            particle_directions[particle] = next_direction
    if particle_directions:
        particles[0].world.move_particles(particle_directions)
