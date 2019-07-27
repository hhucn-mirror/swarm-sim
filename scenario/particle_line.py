import random

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


	x = 6
	y = 0
	while y < 24:
		sim.add_particle(x+(0.5*y), y)
		y = y + 1

	liste = sim.get_particle_list()
	assign_new_numbers(liste)


def assign_new_numbers(particleList):
	i = 0

	random.shuffle(particleList)
	while i < len(particleList):
		particleList[i].__setattr__("number", i)
		i = i + 1