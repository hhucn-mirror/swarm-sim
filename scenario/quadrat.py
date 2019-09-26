

def scenario(sim):
    #size=8
    a=6
    b=6

    for a in range(-4,3):
        for b in range(-4,3):
            if b%2==0:
                sim.add_particle(a, b)
            else:
                sim.add_particle(a+0.5, b)

    print("Particle amount", len(sim.get_particle_list()))
    for particle in sim.get_particle_list():
        print("x: ", particle.coords[0])
        print("y: ", particle.coords[1])
