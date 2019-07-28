from lib.comms import Message, generate_random_messages
from lib.mobility_model import MobilityModel, Mode
import lib.routing


s_radius = 1


def solution(sim):
    global particles

    if sim.get_actual_round() == 1:
        particles = sim.get_particle_list()
        generate_random_messages(particles, len(particles)*2, sim)
        # initialize the particle mobility models
        for particle in particles:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Static, (5, 10))
            m_model.set(particle)
            r_params = lib.routing.RoutingParameters(lib.routing.Algorithm.Epidemic, scan_radius=s_radius)
            r_params.set(particle)
    else:
        Message(particles[1], particles[2], sim.get_actual_round(), 100)
        for particle in particles:
            lib.routing.next_step(particle)
            # move the particle to the next location
            m_model = MobilityModel.get(particle)
            particle.move_to_in_bounds(m_model.next_direction())
