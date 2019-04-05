black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9


def create_scenario(sim):

    # Top Border
    sim.add_location(-11.5, 13, color=black)
    sim.add_location(-10.5, 13, color=black)
    sim.add_location(-9.5, 13, color=black)
    sim.add_location(-8.5, 13, color=black)
    sim.add_location(-7.5, 13, color=black)
    sim.add_location(-6.5, 13, color=black)
    sim.add_location(-5.5, 13, color=black)
    sim.add_location(-4.5, 13, color=black)
    sim.add_location(-3.5, 13, color=black)
    sim.add_location(-2.5, 13, color=black)
    sim.add_location(-1.5, 13, color=black)
    sim.add_location(-0.5, 13, color=black)
    sim.add_location(0.5, 13, color=black)
    sim.add_location(1.5, 13, color=black)
    sim.add_location(2.5, 13, color=black)
    sim.add_location(3.5, 13, color=black)
    sim.add_location(4.5, 13, color=black)
    sim.add_location(5.5, 13, color=black)
    sim.add_location(6.5, 13, color=black)
    sim.add_location(7.5, 13, color=black)
    sim.add_location(8.5, 13, color=black)
    sim.add_location(9.5, 13, color=black)
    sim.add_location(10.5, 13, color=black)
    sim.add_location(11.5, 13, color=black)

    # Bottom Border
    sim.add_location(-11.5, -13, color=black)
    sim.add_location(-10.5, -13, color=black)
    sim.add_location(-9.5, -13, color=black)
    sim.add_location(-8.5, -13, color=black)
    sim.add_location(-7.5, -13, color=black)
    sim.add_location(-6.5, -13, color=black)
    sim.add_location(-5.5, -13, color=black)
    sim.add_location(-4.5, -13, color=black)
    sim.add_location(-3.5, -13, color=black)
    sim.add_location(-2.5, -13, color=black)
    sim.add_location(-1.5, -13, color=black)
    sim.add_location(-0.5, -13, color=black)
    sim.add_location(0.5, -13, color=black)
    sim.add_location(1.5, -13, color=black)
    sim.add_location(2.5, -13, color=black)
    sim.add_location(3.5, -13, color=black)
    sim.add_location(4.5, -13, color=black)
    sim.add_location(5.5, -13, color=black)
    sim.add_location(6.5, -13, color=black)
    sim.add_location(7.5, -13, color=black)
    sim.add_location(8.5, -13, color=black)
    sim.add_location(9.5, -13, color=black)
    sim.add_location(10.5, -13, color=black)
    sim.add_location(11.5, -13, color=black)

    # Left Border
    sim.add_location(-12, 12, color=black)
    sim.add_location(-11.5, 11, color=black)
    sim.add_location(-12, 10, color=black)
    sim.add_location(-11.5, 9, color=black)
    sim.add_location(-12, 8, color=black)
    sim.add_location(-11.5, 7, color=black)
    sim.add_location(-12, 6, color=black)
    sim.add_location(-11.5, 5, color=black)
    sim.add_location(-12, 4, color=black)
    sim.add_location(-11.5, 3, color=black)
    sim.add_location(-12, 2, color=black)
    sim.add_location(-11.5, 1, color=black)
    sim.add_location(-12, 0, color=black)
    sim.add_location(-12, -12, color=black)
    sim.add_location(-11.5, -11, color=black)
    sim.add_location(-12, -10, color=black)
    sim.add_location(-11.5, -9, color=black)
    sim.add_location(-12, -8, color=black)
    sim.add_location(-11.5, -7, color=black)
    sim.add_location(-12, -6, color=black)
    sim.add_location(-11.5, -5, color=black)
    sim.add_location(-12, -4, color=black)
    sim.add_location(-11.5, -3, color=black)
    sim.add_location(-12, -2, color=black)
    sim.add_location(-11.5, -1, color=black)

    # Right Border
    sim.add_location(12, 12, color=black)
    sim.add_location(11.5, 11, color=black)
    sim.add_location(12, 10, color=black)
    sim.add_location(11.5, 9, color=black)
    sim.add_location(12, 8, color=black)
    sim.add_location(11.5, 7, color=black)
    sim.add_location(12, 6, color=black)
    sim.add_location(11.5, 5, color=black)
    sim.add_location(12, 4, color=black)
    sim.add_location(11.5, 3, color=black)
    sim.add_location(12, 2, color=black)
    sim.add_location(11.5, 1, color=black)
    sim.add_location(12, 0, color=black)
    sim.add_location(12, -12, color=black)
    sim.add_location(11.5, -11, color=black)
    sim.add_location(12, -10, color=black)
    sim.add_location(11.5, -9, color=black)
    sim.add_location(12, -8, color=black)
    sim.add_location(11.5, -7, color=black)
    sim.add_location(12, -6, color=black)
    sim.add_location(11.5, -5, color=black)
    sim.add_location(12, -4, color=black)
    sim.add_location(11.5, -3, color=black)
    sim.add_location(12, -2, color=black)
    sim.add_location(11.5, -1, color=black)

    ###################################################

    # In World Obstacles
    sim.add_location(-2, 0, color=black)
    sim.add_location(0, -2, color=black)
    sim.add_location(1, -2, color=black)
    sim.add_location(1.5, 3, color=black)
    sim.add_location(0.5, 3, color=black)

    sim.add_location(-7.0, 8.0, color=black)
    sim.add_location(-6.5, 7.0, color=black)
    sim.add_location(-6.0, 6.0, color=black)
    sim.add_location(-5.5, 5.0, color=black)
    sim.add_location(-5.0, 4.0, color=black)
    sim.add_location(-4.5, 3.0, color=black)
    sim.add_location(-4.0, 2.0, color=black)
    sim.add_location(-3.5, 1.0, color=black)
    sim.add_location(-3.0, 0.0, color=black)

    sim.add_location(0.5, 1, color=black)
    sim.add_location(0, 2, color=black)
    sim.add_location(-0.5, 3, color=black)
    sim.add_location(-0.5, 0, color=black)
    sim.add_location(1.5, -1, color=black)

    sim.add_location(5.5, -5, color=black)
    sim.add_location(6.5, -5, color=black)
    sim.add_location(6.5, -7, color=black)
    sim.add_location(6, -6, color=black)
    sim.add_location(5, -6, color=black)
    sim.add_location(7, -6, color=black)
    sim.add_location(5.5, -7, color=black)

    sim.add_location(8.5, 11, color=black)
    sim.add_location(9, 10, color=black)
    # sim.add_location(9.5, 9, color=black)
    # sim.add_location(10.5, 9, color=black)
    sim.add_location(7.5, 11, color=black)
    sim.add_location(6.5, 11, color=black)
    sim.add_location(5.5, 11, color=black)
    sim.add_location(4.5, 11, color=black)
    sim.add_location(3.5, 11, color=black)
    # sim.add_location(2.5, 11, color=black)
    # sim.add_location(1.5, 11, color=black)
    # sim.add_location(0.5, 11, color=black)


    ###################################################

    # Particles
    # sim.add_particle(0, 0, color=red)
    # sim.add_particle(10, 10, color=black)
    # sim.add_particle(10, -10, color=black)
    # sim.add_particle(-10, 10, color=violett)

    sim.add_particle(-9.5, 11, color=blue)
    sim.add_particle(-10, 10, color=black)
    sim.add_particle(-9, 10, color=red)
    # sim.add_particle(-9, 10, color=green)

    sim.add_particle(-8.5, 11, color=green)
    # sim.add_particle(-11, 12, color=blue)
    # sim.add_particle(10, 10, color=cyan)
    # sim.add_particle(10, 10, color=cyan)
    # sim.add_particle(-1, 0, color=violett)
    # sim.add_particle(0, 0, color=red)
    # sim.add_particle(-3, 0, color=red)
    # sim.add_particle(0.5, 1, color=red)
    # sim.add_particle(1, 2, color=red)

    ###################################################

    # Tiles
    sim.add_tile(11, 12, color=black)


