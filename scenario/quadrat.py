

def scenario(sim):
    #size=8
    a=6
    b=6

    for a in range(-3,3):
        for b in range(-3,3):
            if b%2==0:
                sim.add_particle(a, b)
            else:
                sim.add_particle(a+0.5, b)

    print("Particle amount", len(sim.get_particle_list()))
