import random

from lib.comms import Message
from lib.mobility_model import MobilityModel, Mode
import lib.routing


def solution(sim):
    global particles

    if sim.get_actual_round() == 1:
        particles = sim.get_particle_list()
        # generate random messages
        for i in range(200):
            sender = random.choice(particles)
            receiver = random.choice([particle for particle in particles if particle != sender])
            Message(sender, receiver, start_round=sim.get_actual_round(), ttl=random.randint(50, sim.get_max_round()))
        # initialize the particle mobility models
        for particle in particles:
            m_model = MobilityModel(particle.coords[0], particle.coords[1], Mode.Random_Mode, (5, 30))
            m_model.set(particle)
            r_params = lib.routing.RoutingParameters(lib.routing.Algorithm.Epidemic, 10)
            r_params.set(particle)
    else:
        for particle in particles:
            lib.routing.next_step(particle)
            # move the particle to the next location
            m_model = getattr(particle, "mobility_model")
            particle.move_to(m_model.next_direction())
