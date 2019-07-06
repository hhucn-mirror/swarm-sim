import random

def scenario(sim):

    amount = 100
    added = 1

    sim.add_particle(0, 0)

    list = sim.get_particle_list()

    while added < amount:
        random.shuffle(list)
        #particle = list[0]

        dir = [0, 1, 2, 3, 4, 5]
        random.shuffle(dir)

        for particle in list:
            if particle.get_particle_in(dir[0]) is None:
                coords = sim.get_coords_in_dir(particle.coords, dir[0])
                sim.add_particle(coords[0], coords[1])
                added = added+1
                break

        list = sim.get_particle_list()