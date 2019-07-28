from lib.comms import generate_random_messages
from lib.mobility_model import MobilityModel, Mode
import lib.routing


scan_radius = 1


def solution(sim):
    global particles

    if sim.get_actual_round() == 1:
        particles = sim.get_particle_list()
        generate_random_messages(particles, len(particles)*10)

        # initialize the particle mobility models
        particle_number = 0
        for particle in particles:
            p_zone, m_group = get_zone_and_group(particle_number, sim)
            p_role, m_model = get_role_and_model(particle_number, particle, p_zone)

            m_model.set(particle)
            r_params = lib.routing.RoutingParameters(lib.routing.Algorithm.Epidemic, scan_radius,
                                                     manet_role=p_role, manet_group=m_group)
            r_params.set(particle)
            particle_number += 1
    else:
        if sim.get_actual_round() % 5 == 0:
            generate_random_messages(particles, len(particles))
        for particle in particles:
            lib.routing.next_step(particle)
            # move the particle to the next location
            m_model = MobilityModel.get(particle)
            direction = m_model.next_direction(current_x_y=particle.coords)
            particle.move_to(direction)


def get_zone_and_group(particle_number, sim):
    if particle_number < 4:
        # top-left
        p_zone = (-sim.get_sim_x_size(), -sim.get_sim_y_size(), 0, sim.get_sim_y_size())
        m_group = 0
    elif particle_number < 8:
        # top-right
        p_zone = (0, 0, sim.get_sim_x_size(), sim.get_sim_y_size())
        m_group = 1
    elif particle_number < 12:
        # bottom-left
        p_zone = (-sim.get_sim_x_size(), -sim.get_sim_y_size(), 0, 0)
        m_group = 2
    else:
        # bottom-right
        p_zone = (0, -sim.get_sim_y_size(), sim.get_sim_x_size(), 0)
        m_group = 3
    return p_zone, m_group


def get_role_and_model(particle_number, particle, p_zone):
    if particle_number % 4 == 0:
        p_role = lib.routing.MANeTRole.Router
        m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Static)
    else:
        p_role = lib.routing.MANeTRole.Node
        m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Static, zone=p_zone)
    return p_role, m_model
