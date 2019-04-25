black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9


def scenario(sim):
    draw_terrain(sim)

    # Particles
    sim.add_particle(-9.5, 11, color=blue)
    sim.add_particle(-10, 10, color=black)
    sim.add_particle(-9, 10, color=red)
    sim.add_particle(-8.5, 11, color=green)
    # sim.add_particle(-11, 12, color=yellow)
    # sim.add_particle(-11, 10, color=violett)
    # sim.add_particle(-10, 12, color=cyan)
    # sim.add_particle(-9, 12, color=orange)
    # sim.add_particle(-10.5, 11, color=gray)


def draw_terrain(sim):
    # Top Border
    sim.add_location(-11.5, 13)
    sim.add_location(-10.5, 13)
    sim.add_location(-9.5, 13)
    sim.add_location(-8.5, 13)
    sim.add_location(-7.5, 13)
    sim.add_location(-6.5, 13)
    sim.add_location(-5.5, 13)
    sim.add_location(-4.5, 13)
    sim.add_location(-3.5, 13)
    sim.add_location(-2.5, 13)
    sim.add_location(-1.5, 13)
    sim.add_location(-0.5, 13)
    sim.add_location(0.5, 13)
    sim.add_location(1.5, 13)
    sim.add_location(2.5, 13)
    sim.add_location(3.5, 13)
    sim.add_location(4.5, 13)
    sim.add_location(5.5, 13)
    sim.add_location(6.5, 13)
    sim.add_location(7.5, 13)
    sim.add_location(8.5, 13)
    sim.add_location(9.5, 13)
    sim.add_location(10.5, 13)
    sim.add_location(11.5, 13)

    # Bottom Border
    sim.add_location(-11.5, -13)
    sim.add_location(-10.5, -13)
    sim.add_location(-9.5, -13)
    sim.add_location(-8.5, -13)
    sim.add_location(-7.5, -13)
    sim.add_location(-6.5, -13)
    sim.add_location(-5.5, -13)
    sim.add_location(-4.5, -13)
    sim.add_location(-3.5, -13)
    sim.add_location(-2.5, -13)
    sim.add_location(-1.5, -13)
    sim.add_location(-0.5, -13)
    sim.add_location(0.5, -13)
    sim.add_location(1.5, -13)
    sim.add_location(2.5, -13)
    sim.add_location(3.5, -13)
    sim.add_location(4.5, -13)
    sim.add_location(5.5, -13)
    sim.add_location(6.5, -13)
    sim.add_location(7.5, -13)
    sim.add_location(8.5, -13)
    sim.add_location(9.5, -13)
    sim.add_location(10.5, -13)
    sim.add_location(11.5, -13)

    # Left Border
    sim.add_location(-12, 12)
    sim.add_location(-11.5, 11)
    sim.add_location(-12, 10)
    sim.add_location(-11.5, 9)
    sim.add_location(-12, 8)
    sim.add_location(-11.5, 7)
    sim.add_location(-12, 6)
    sim.add_location(-11.5, 5)
    sim.add_location(-12, 4)
    sim.add_location(-11.5, 3)
    sim.add_location(-12, 2)
    sim.add_location(-11.5, 1)
    sim.add_location(-12, 0)
    sim.add_location(-12, -12)
    sim.add_location(-11.5, -11)
    sim.add_location(-12, -10)
    sim.add_location(-11.5, -9)
    sim.add_location(-12, -8)
    sim.add_location(-11.5, -7)
    sim.add_location(-12, -6)
    sim.add_location(-11.5, -5)
    sim.add_location(-12, -4)
    sim.add_location(-11.5, -3)
    sim.add_location(-12, -2)
    sim.add_location(-11.5, -1)

    # Right Border
    sim.add_location(12, 12)
    sim.add_location(11.5, 11)
    sim.add_location(12, 10)
    sim.add_location(11.5, 9)
    sim.add_location(12, 8)
    sim.add_location(11.5, 7)
    sim.add_location(12, 6)
    sim.add_location(11.5, 5)
    sim.add_location(12, 4)
    sim.add_location(11.5, 3)
    sim.add_location(12, 2)
    sim.add_location(11.5, 1)
    sim.add_location(12, 0)
    sim.add_location(12, -12)
    sim.add_location(11.5, -11)
    sim.add_location(12, -10)
    sim.add_location(11.5, -9)
    sim.add_location(12, -8)
    sim.add_location(11.5, -7)
    sim.add_location(12, -6)
    sim.add_location(11.5, -5)
    sim.add_location(12, -4)
    sim.add_location(11.5, -3)
    sim.add_location(12, -2)
    sim.add_location(11.5, -1)

    ###################################################

    # Obstacles
    sim.add_location(-2, 0)
    sim.add_location(0, -2)
    sim.add_location(1, -2)
    sim.add_location(1.5, 3)
    sim.add_location(0.5, 3)

    sim.add_location(-7.0, 8.0)
    sim.add_location(-6.5, 7.0)
    sim.add_location(-6.0, 6.0)
    sim.add_location(-5.5, 5.0)
    sim.add_location(-5.0, 4.0)
    sim.add_location(-4.5, 3.0)
    sim.add_location(-4.0, 2.0)
    sim.add_location(-3.5, 1.0)
    sim.add_location(-3.0, 0.0)

    sim.add_location(0.5, 1)
    sim.add_location(0, 2)
    sim.add_location(-0.5, 3)
    sim.add_location(-0.5, 0)
    sim.add_location(1.5, -1)

    sim.add_location(5.5, -5)
    sim.add_location(6.5, -5)
    sim.add_location(6.5, -7)
    sim.add_location(6, -6)
    sim.add_location(5, -6)
    sim.add_location(7, -6)
    sim.add_location(5.5, -7)

    sim.add_location(8.5, 11)
    sim.add_location(9, 10)
    sim.add_location(9.5, 9)
    sim.add_location(10.5, 9)
    sim.add_location(7.5, 11)
    sim.add_location(6.5, 11)
    sim.add_location(5.5, 11)
    sim.add_location(4.5, 11)
    sim.add_location(3.5, 11)
    sim.add_location(2.5, 11)
    sim.add_location(1.5, 11)
    # sim.add_location(0.5, 11)

