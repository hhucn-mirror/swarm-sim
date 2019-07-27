import random

def scenario(sim):
	amount = sim.config_data.p_amount
	created = 0

	while created < amount:
		x = 0 + (created*1)
		sim.add_particle(x, 0)
		created = created + 1



def assign_new_numbers(particleList):
	i = 0

	random.shuffle(particleList)
	while i < len(particleList):
		particleList[i].__setattr__("number", i)
		i = i + 1