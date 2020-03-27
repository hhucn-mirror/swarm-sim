from scenario.particleGroups import *

def scenario(world):
	hexagon(world, (3.0-world.config_data.seed_value, 0.0, 0.0), world.config_data.seed_value)
	#create_matter_in_line(world, (3.0, 0.0, 0.0), (-1.0, 0.0, 0.0),  world.config_data.seed_value)
	world.add_tile((7.0, 0.0, 0), color=(0.3, 0.3, 0.8, 1.0))
