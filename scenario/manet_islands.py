num_part_per = 5
left = -2.5
right = -left
top = 3.0
bottom = -top


def scenario(world):
    # top-left
    world.add_particle(left, top, color=1)
    world.add_particle(left + 1, top, color=1)
    world.add_particle(left + 0.5, top-1, color=1)
    world.add_particle(left - 0.5, top-1, color=1)
    # bottom-left
    world.add_particle(left, bottom, color=1)
    world.add_particle(left + 1, bottom, color=1)
    world.add_particle(left + 0.5, bottom + 1, color=1)
    world.add_particle(left - 0.5, bottom + 1, color=1)
    # top-right
    world.add_particle(right, top, color=1)
    world.add_particle(right - 1, top, color=1)
    world.add_particle(right - 0.5, top-1, color=1)
    world.add_particle(right + 0.5, top-1, color=1)
    # bottom-right
    world.add_particle(right, bottom, color=1)
    world.add_particle(right - 1, bottom, color=1)
    world.add_particle(right - 0.5, bottom + 1, color=1)
    world.add_particle(right + 0.5, bottom + 1, color=1)
