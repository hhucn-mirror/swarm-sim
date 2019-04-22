def scenario(sim):
	x = 0
	y = 0
	i = 0
	while i < 19:
		sim.add_particle(x, y)
		x = x + 0.5
		y = y - 1
		i = i + 1
	#world.add_particle(1.0, -2.0)
	#world.add_particle(0.5, -3.0)
	#world.add_particle(1.0, -4.0)
	#world.add_particle(1.5, -5.0)
	#world.add_particle(1, 0)
	#world.add_particle(-1, 0.0)
	#world.add_particle(-2, 0)
