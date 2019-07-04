def scenario(sim):
	"""sim.add_particle(0, 0)
	sim.add_particle(0.5, -1)
	sim.add_particle(1, -2)
	sim.add_particle(1.5, -3)
	sim.add_particle(2, -4)
	sim.add_particle(1, -4)
	sim.add_particle(3, -4)"""


	"""sim.add_particle(-0.5, 1.0)
	sim.add_particle(-1.0, -0.0)
	sim.add_particle(-0.0, 0.0)
	sim.add_particle(-1.5, -1.0)
	sim.add_particle(-0.5, -1.0)
	sim.add_particle(0.5, -1.0)
	sim.add_particle(-2.0, -2.0)
	sim.add_particle(-1.0, -2.0)
	sim.add_particle(-0.0, -2.0)
	sim.add_particle(1.0, -2.0)2"""

	x = 0
	y = 0
	while y < 7:
		sim.add_particle(x-(0.5*y), y)
		y = y + 1