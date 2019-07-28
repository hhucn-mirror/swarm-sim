from lib.colors import Colors

num_part_per = 5
left = -2.5
right = -left
top = 3.0
bottom = -top


def scenario(world):
    # top-left

    for x in range(-4, 0):
        for y in range (-4,4,2):
            world.add_tile(x,y)

    world.add_particle(left, top, color=Colors.violet.value)


    """world.add_particle(left + 1, top, color=Colors.violet.value)
    world.add_particle(left + 0.5, top-1, color=Colors.violet.value)
    world.add_particle(left - 0.5, top-1, color=Colors.violet.value)

    # bottom-left
    world.add_particle(left, bottom, color=Colors.yellow.value)
    world.add_particle(left + 1, bottom, color=Colors.yellow.value)
    world.add_particle(left + 0.5, bottom + 1, color=Colors.yellow.value)
    world.add_particle(left - 0.5, bottom + 1, color=Colors.yellow.value)
    # top-right
    world.add_particle(right, top, color=Colors.green.value)
    world.add_particle(right - 1, top, color=Colors.green.value)
    world.add_particle(right - 0.5, top-1, color=Colors.green.value)
    world.add_particle(right + 0.5, top-1, color=Colors.green.value)
    # bottom-right
    world.add_particle(right, bottom, color=Colors.red.value)
    world.add_particle(right - 1, bottom, color=Colors.red.value)
    world.add_particle(right - 0.5, bottom + 1, color=Colors.red.value)"""
    world.add_particle(right + 0.5, bottom + 1, color=Colors.red.value)


