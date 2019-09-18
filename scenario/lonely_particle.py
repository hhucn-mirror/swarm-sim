
def scenario(sim):

    for i in range(-7,7):
        sim.add_particle(i, 0)
    for i in range(-7,7):
        sim.add_particle(i+0.5, 1)

    print("Particle amount", len(sim.get_particle_list()))