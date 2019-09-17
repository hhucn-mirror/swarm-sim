import lib.oppnet.routing
from lib.oppnet import opp_solution
from lib.oppnet.comms import generate_random_messages
from lib.oppnet.mobility_model import MobilityModel, Mode
from lib.std_lib import black


def solution(sim):
    particles = sim.get_particle_list()

    if sim.get_actual_round() == 1:
        # initialize the particle mobility models
        # models for the 4 communicating particles at the edges
        for particle in particles[:4]:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], sim.mobility_model_mode)
            m_model.set(particle)

        # initially generate 5 message per particle on the edge
        messages = generate_random_messages(particles[:4], amount=5, sim=sim)

        # mobility model for the moving particle
        # make it move back and forth between the two borders
        # head east first
        m_model = MobilityModel(particles[4].coords[0], particles[4].coords[1], Mode.Back_And_Forth, length=(40, 40),
                                starting_dir=0)
        m_model.set(particles[4])

        # mobility models for the borders and diagonals
        for particle in particles[5:]:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], sim.mobility_model_mode)
            m_model.set(particle)

        # set the routing parameters for the particles
        for particle in particles:
            r_params = lib.oppnet.routing.RoutingParameters(algorithm=sim.routing_algorithm,
                                                            scan_radius=sim.scan_radius,
                                                            delivery_delay=sim.delivery_delay)
            r_params.set(particle)

    else:
        for particle in particles:
            # reset color every second round
            if sim.get_actual_round() % 2 == 0:
                particle.set_color(black)
            m_model = MobilityModel.get(particle)
            particle.move_to(m_model.next_direction(current_x_y=particle.coords))

        lib.oppnet.routing.next_step(particles, sim.get_actual_round())

    opp_solution.process_event_queue(sim)
