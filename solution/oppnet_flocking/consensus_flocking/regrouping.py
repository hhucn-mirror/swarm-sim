from random import choice

from lib.oppnet.mobility_model import MobilityModel, MobilityModelMode

tiles_count = 0


def solution(world):
    global tiles_count
    current_round = world.get_actual_round()
    particles = world.get_particle_list()
    predators = world.get_predators_list()
    tiles = world.get_tiles_list()

    if len(tiles) > 0:
        if len(tiles) > tiles_count:
            tiles_count = len(tiles)
            for particle in particles:
                poi = choice(tiles).coordinates
                particle.mobility_model = MobilityModel(particle.coordinates, mode=MobilityModelMode.POI, poi=poi)
                next_direction = particle.mobility_model.next_direction(particle.coordinates,
                                                                        particle.get_blocked_surrounding_locations())
                if next_direction:
                    particle.move_to(next_direction)
        else:
            for particle in particles:
                next_direction = particle.mobility_model.next_direction(particle.coordinates,
                                                                        particle.get_blocked_surrounding_locations())
                if next_direction:
                    particle.move_to(next_direction)
