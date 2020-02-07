"""""
Testumgebung für Simon
"""""
import random

random.seed(755)


def scenario(sim):
    decider = 0
    for i in range(20):
        sim.add_particle(round(random.uniform(-10.5, 10.5)), round(random.uniform(-10, 10)), 2)
        if decider == 0:
            # if random.random() > 0.90:
                for particle in sim.get_particle_list():
                    particle.write_memory_with("leader", "yes")
                    particle.set_color(3)
                    decider = 1
                    break

    #sim.add_marker(0.5, 1)

    # for i in range(50):
    #     sim.add_tile(round(random.uniform(-10.5, 10.5)), round(random.uniform(-10, 10)), 2)





    #sim.add_particle(-2.5, 3.0)
    #sim.add_particle(-2.5, 1.0)
    #sim.add_tile(-11.0, -0.0, color=3)
    #sim.add_tile(-10.0, -0.0, color=1)
    #sim.add_tile(-10.5, -1.0)
    #sim.add_tile(-11.0, -2.0)
    #sim.add_tile(-12.0, -2.0)
    #sim.add_tile(-13.0, -2.0)
    #sim.add_tile(-11.5, 1.0)
    #sim.add_tile(-12.0, 2.0)
    #sim.add_tile(-12.5, 3.0)
    #sim.add_tile(-12.5, 3.0)
    #sim.add_tile(-13.5, 3.0)