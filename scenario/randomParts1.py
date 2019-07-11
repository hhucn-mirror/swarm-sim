import random

def scenario(sim):
    sim.add_particle(0, 0)
    sim.add_particle (1.0, 0.0)
    sim.add_particle (1.5, -1.0)
    sim.add_particle (2.5, -3.0)
    sim.add_particle (1.5, -3.0)
    sim.add_particle (0.5, -3.0)
    sim.add_particle (-0.5, -3.0)
    sim.add_particle (-0.0, -4.0)
    sim.add_particle (1.0, -4.0)
    sim.add_particle (2.0, -4.0)
    sim.add_particle (3.0, -4.0)
    sim.add_particle (3.5, -5.0)
    sim.add_particle (4.0, -6.0)
    sim.add_particle (4.5, -7.0)
    sim.add_particle (0.5, 1.0)
    sim.add_particle (-0.0, 2.0)
    sim.add_particle (-0.5, 3.0)
    sim.add_particle (0.5, 3.0)
    sim.add_particle (-1.0, 2.0)
    sim.add_particle (-1.5, 1.0)
    sim.add_particle (-2.0, 0.0)
    sim.add_particle (-2.5, -1.0)
    sim.add_particle (-3.0, -2.0)
    sim.add_particle (-2.5, -3.0)
    sim.add_particle (-1.5, -3.0)
    sim.add_particle (-1.0, -4.0)
    sim.add_particle (-0.5, -5.0)
    sim.add_particle (0.5, -5.0)
    sim.add_particle (1.5, -5.0)
    sim.add_particle (-1.0, -6.0)
    sim.add_particle (-0.5, -7.0)
    sim.add_particle (-0.0, -8.0)
    sim.add_particle (0.5, -9.0)
    sim.add_particle (1.0, -10.0)
    sim.add_particle (1.5, -11.0)
    sim.add_particle (2.0, -12.0)
    sim.add_particle (2.0, -2.0)


    liste = sim.get_particle_list()
    assign_new_numbers(liste)

def assign_new_numbers(particleList):
    i = 0

    random.shuffle(particleList)
    while i < len(particleList):
        particleList[i].__setattr__("number", i)
        i = i+1