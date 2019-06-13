from lib.comms import generate_random_messages
from lib.mobility_model import MobilityModel, Mode
import lib.routing


def solution(sim):
    global particles

    if sim.get_actual_round() == 1:
        particles = sim.get_particle_list()
        generate_random_messages(particles, len(particles)*2)
        # initialize the particle mobility models
        i = 0
        for particle in particles:
            p_role = lib.routing.MANeTRole.Node
            if i < 4:
                p_role = lib.routing.MANeTRole.Router
            if i % 4 == 0:
                # top-left
                p_zone = (-sim.get_sim_x_size(), -sim.get_sim_y_size(), 0, sim.get_sim_y_size())
            elif i % 4 == 1:
                # top-right
                p_zone = (0, 0, sim.get_sim_x_size(), sim.get_sim_y_size())
            elif i % 4 == 2:
                # bottom-left
                p_zone = (-sim.get_sim_x_size(), -sim.get_sim_y_size(), 0, 0)
            else:
                # bottom-right
                p_zone = (0, -sim.get_sim_y_size(), sim.get_sim_x_size(), 0)

            m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Zonal, zone=p_zone)
            m_model.set(particle)
            r_params = lib.routing.RoutingParameters(lib.routing.Algorithm.Epidemic_MANeT, 10, manet_role=p_role,
                                                     manet_group=i % 4)
            r_params.set(particle)
            i += 1
    else:
        for particle in particles:
            lib.routing.next_step(particle)
            # move the particle to the next location
            m_model = MobilityModel.get(particle)
            particle.move_to(m_model.next_direction(current_x_y=particle.coords))
