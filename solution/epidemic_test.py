from lib.comms import generate_random_messages
from lib.mobility_model import MobilityModel, Mode
import lib.routing


message_amount = 50


def solution(sim):

    particles = sim.get_particle_list()

    if sim.get_actual_round() == 1:
        # initialize the particle mobility models
        for particle in particles:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Random)
            m_model.set(particle)
            r_params = lib.routing.RoutingParameters(lib.routing.Algorithm.Epidemic, scan_radius=sim.scan_radius,
                                                     delivery_delay=2)
            r_params.set(particle)
        generate_random_messages(particles, 20, sim)
    else:
        # move in every round starting from the second one
        for particle in particles:
            m_model = MobilityModel.get(particle)
            particle.move_to_in_bounds(m_model.next_direction())
            lib.routing.next_step(particle, sim.get_actual_round())
