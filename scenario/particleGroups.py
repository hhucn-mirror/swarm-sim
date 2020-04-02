def doubleline20(sim):
    sim.add_particle(-5, 0)
    sim.add_particle(-4, 0)
    sim.add_particle(-3, 0)
    sim.add_particle(-2, 0)
    sim.add_particle(-1, 0)
    sim.add_particle(0, 0)
    sim.add_particle(1, 0)
    sim.add_particle(2, 0)
    sim.add_particle(3, 0)
    sim.add_particle(4, 0)
    sim.add_particle(-5.5, 1)
    sim.add_particle(-4.5, 1)
    sim.add_particle(-3.5, 1)
    sim.add_particle(-2.5, 1)
    sim.add_particle(-1.5, 1)
    sim.add_particle(-0.5, 1)
    sim.add_particle(0.5, 1)
    sim.add_particle(1.5, 1)
    sim.add_particle(2.5, 1)
    sim.add_particle(3.5, 1)

def line10(sim):
    sim.add_particle(-5, 0)
    sim.add_particle(-4, 0)
    sim.add_particle(-3, 0)
    sim.add_particle(-2, 0)
    sim.add_particle(-1, 0)
    sim.add_particle(0, 0)
    sim.add_particle(1, 0)
    sim.add_particle(2, 0)
    sim.add_particle(3, 0)
    sim.add_particle(4, 0)

def around37(sim):
    sim.add_particle(3, 0)
    sim.add_particle(1, 0)
    sim.add_particle(-1, 0)
    sim.add_particle(-0.5, 1)
    sim.add_particle(0.5, 1)
    sim.add_particle(-0.5, -1)
    sim.add_particle(0.5, -1)
    sim.add_particle(2, 0)
    sim.add_particle(-2, 0)
    sim.add_particle(-1.5, 1)
    sim.add_particle(1.5, 1)
    sim.add_particle(0, 2)
    sim.add_particle(-1, 2)
    sim.add_particle(1, 2)
    sim.add_particle(-1.5, -1)
    sim.add_particle(1.5, -1)
    sim.add_particle(0, -2)
    sim.add_particle(-1, -2)
    sim.add_particle(1, -2)
    sim.add_particle(-3, 0)
    sim.add_particle(-2.5, 1)
    sim.add_particle(2.5, 1)
    sim.add_particle(-2, 2)
    sim.add_particle(2, 2)
    sim.add_particle(-1.5, 3)
    sim.add_particle(1.5, 3)
    sim.add_particle(-0.5, 3)
    sim.add_particle(0.5, 3)
    sim.add_particle(-2.5, -1)
    sim.add_particle(2.5, -1)
    sim.add_particle(-2, -2)
    sim.add_particle(2, -2)
    sim.add_particle(-1.5, -3)
    sim.add_particle(1.5, -3)
    sim.add_particle(-0.5, -3)
    sim.add_particle(0.5, -3)
    sim.add_particle(0, 0)

def star50(sim):
    sim.add_particle(3,0)
    sim.add_particle(2,0)
    sim.add_particle(1,0)
    sim.add_particle(0,0)
    sim.add_particle(-1,0)
    sim.add_particle(-2,0)
    sim.add_particle(-3,0)
    sim.add_particle(-4,0)
    sim.add_particle(-5,0)
    sim.add_particle(-6,0)
    sim.add_particle(-7,0)
    sim.add_particle(-8,0)
    sim.add_particle(-9,0)
    sim.add_particle(-10,0)

    sim.add_particle(-2.5, 1)
    sim.add_particle(-2.5, -1)
    sim.add_particle(-3.5, 1)
    sim.add_particle(-3.5, -1)

    sim.add_particle(-2, 2)
    sim.add_particle(-2, -2)
    sim.add_particle(-4, 2)
    sim.add_particle(-4, -2)

    sim.add_particle(-1.5, 3)
    sim.add_particle(-1.5, -3)
    sim.add_particle(-4.5, 3)
    sim.add_particle(-4.5, -3)

    sim.add_particle(-1, 4)
    sim.add_particle(-1, -4)
    sim.add_particle(-5, 4)
    sim.add_particle(-5, -4)

    sim.add_particle(-0.5, 5)
    sim.add_particle(-0.5, -5)
    sim.add_particle(-5.5, 5)
    sim.add_particle(-5.5, -5)

    sim.add_particle(0, 6)
    sim.add_particle(0, -6)
    sim.add_particle(-6, 6)
    sim.add_particle(-6, -6)

    #38
    sim.add_particle(0.5, 7)
    sim.add_particle(0.5, -7)
    sim.add_particle(-6.5, 7)
    sim.add_particle(-6.5, -7)

    sim.add_particle(1, 8)
    sim.add_particle(1, -8)
    sim.add_particle(-7, 8)
    sim.add_particle(-7, -8)

    sim.add_particle(1.5, 9)
    sim.add_particle(1.5, -9)
    sim.add_particle(-7.5, 9)
    sim.add_particle(-7.5, -9)

    sim.add_particle(2, 10)
    sim.add_particle(2, -10)
    sim.add_particle(-8, 10)
    sim.add_particle(-8, -10)

def block100(sim, start=(0,0,0), amount=6):
    amount = int(amount /2)
    for i in range(0,amount):
        for j in range(0,amount):
            if j%2 == 0:
                sim.add_particle(-i + start[0], j + start[1])
            else:
                sim.add_particle(-i + 0.5 + start[0], j +start[1])


def hexagon(world, center, hop):
    # n_sphere_border = world.grid.get_n_sphere(center, hop)
    # for l in n_sphere_border:
    #     world.add_particle(l)
    current_position = (center[0]+hop,center[1], center[2])
    for _ in range(hop):
        world.add_particle(current_position)
        current_position = world.grid.get_coordinates_in_direction(current_position, (-1, 0,0))
def create_matter_in_line(world, start, direction, amount, matter_type='particle'):
    current_position = start
    for _ in range(amount):
        if matter_type == 'particle':
            world.add_particle(current_position)
        elif matter_type == 'tile':
            world.add_tile(current_position)
        elif matter_type == 'location':
            world.add_location(current_position)
        else:
            print("create_matter_in_line: unknown type (allowed: particle, tile or location")
            return
        current_position = world.grid.get_coordinates_in_direction(current_position, direction)