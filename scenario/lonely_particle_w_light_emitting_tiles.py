from lib.tile import red


def scenario(sim):
    # Adding a singular particle to see whether it registers light
    sim.add_particle(0, 0)

    # Adding all tiles
    sim.add_tile(0, -6)
    sim.add_tile(-1, -6)
    sim.add_tile(-2, -6)
    sim.add_tile(1, -6)
    sim.add_tile(2, -6)

    sim.add_tile(0.5, -5)
    sim.add_tile(-0.5, -5)
    sim.add_tile(1.5, -5)
    sim.add_tile(-1.5, -5)

    # Writing the light key into the tiles that are supposed to emit light
    # value represents direction:
    # 0 = North

    for tile in sim.tiles:
        tile.write_memory_with("light_emission", 0)
        # Red tiles are supposed to represent the light emitting tiles
        tile.set_color(red)

