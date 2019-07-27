import random
import math

def scenario(sim):
	d = 0

	created = 0
	amount = sim.config_data.p_amount

	startPos = [0, 0]
	pos = [0, 0]
	while True:
		i = 0
		startPos[0] = pos[0] - (0.5 * d)
		startPos[1] = pos[1] - (1 * d)

		while i <= d:
			x = startPos[0] + (1 * i)
			y = startPos[1]
			if created < amount:
				sim.add_particle(x, y)
				print(sim.get_particle_map_coords()[0,0])
				created = created+1
			else:
				return
			i = i + 1
		d = d + 1

