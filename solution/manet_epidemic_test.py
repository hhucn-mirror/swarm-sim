import lib.particle
from lib.point import Point
from lib.oppnet.comms import generate_random_messages
from lib.oppnet.mobility_model import MobilityModel, Mode
import lib.oppnet.routing


scan_radius = 1


def solution(sim):
    particles = sim.get_particle_list()
    if sim.get_actual_round() == 1:
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(100, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(80, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(60, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(50, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(20, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(5, 0), 0, 1, 1000)
        sim.memory.add_delta_message_on(particles[0].get_id(), "hallo", Point(0, 0), 0, 1, 1000)



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
        p_role = lib.oppnet.routing.MANeTRole.Router
        m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Static)
    else:
        p_role = lib.oppnet.routing.MANeTRole.Node
        m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Static, zone=p_zone)
    return p_role, m_model
