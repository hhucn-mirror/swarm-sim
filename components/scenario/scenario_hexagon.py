import numpy as np
def scenario(sim):

    #sim.add_particle(-2.5, 3.0)
    #sim.add_particle(-2.5, 1.0)
    #print(sim.grid.get_center())

    sim.add_particle((-4.0, 10.0, 0.0))
    sim.add_particle((-2.0, 10.0, 0.0))
    sim.add_particle((0.0, 10.0, 0.0))
    sim.add_particle((2.0, 10.0, 0.0))
    sim.add_particle((3.5, 9.0, 0.0))
    #sim.add_particle((7.0, 2.0, 0.0))

    kachelanzahl = 0

    for  i in range(-6, 4, 3):
        for j in range(-10, 10, 1):
            sim.add_particle((i, j, 0.0))



   # for i in range(-6, 4, 1):
    #    for j in range(-10, 10, 2):
     #       sim.add_particle((i, j, 0.0))

    #for  i in np.arange(-4.5, 5.5, 1):
     #   for j in range(-11, 11, 2):
      #      sim.add_particle((i, j, 0.0))

    for  i in range(-6, 4, 1):
        for j in range(-10, 10, 2):
            sim.add_tile((i, j, 0.0))
            kachelanzahl = kachelanzahl + 1

    for  i in np.arange(-4.5, 5.5, 1):
        for j in range(-11, 11, 2):
            sim.add_tile((i, j, 0.0))
            kachelanzahl = kachelanzahl + 1

    sim.add_tile((-4, 10, 0.0))
    sim.add_tile((-3, 10, 0.0))
    sim.add_tile((-2, 10, 0.0))
    sim.add_tile((-1, 10, 0.0))
    sim.add_tile((0, 10, 0.0))
    sim.add_tile((1, 10, 0.0))
    sim.add_tile((2, 10, 0.0))

    #sim.add_particle((-4, 10, 0.0))
    #sim.add_particle((-3, 10, 0.0))
    #sim.add_particle((-2, 10, 0.0))
    #sim.add_particle((-1, 10, 0.0))
    #sim.add_particle((0, 10, 0.0))
    #sim.add_particle((1, 10, 0.0))
    #sim.add_particle((2, 10, 0.0))
    
    kachelanzahl = kachelanzahl + 7

    print("Kachelanzahl: ", kachelanzahl)





