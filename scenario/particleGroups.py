import math
from math import sqrt


def block100(sim, start=(0,0,0), amount=6):
    amount = int(amount /2)
    for i in range(0,amount):
        for j in range(0,amount):
            if j%2 == 0:
                sim.add_particle(-i + start[0], j + start[1])
            else:
                sim.add_particle(-i + 0.5 + start[0], j +start[1])

#
def hexagon(world, center, hop):
    # n_sphere_border = world.grid.get_n_sphere(center, hop)
    # for l in n_sphere_border:
    #     world.add_particle(l)
    current_position = (center[0]+hop,center[1], center[2])
    for _ in range(hop):
        world.add_particle(current_position)
        current_position = world.grid.get_coordinates_in_direction(current_position, (-1, 0,0))

# def create_matter_in_line(world, start, direction, amount, matter_type='particle'):
#     current_position = start
#     for _ in range(amount):
#         if matter_type == 'particle':
#             world.add_particle(current_position)
#         elif matter_type == 'tile':
#             world.add_tile(current_position)
#         elif matter_type == 'location':
#             world.add_location(current_position)
#         else:
#             print("create_matter_in_line: unknown type (allowed: particle, tile or location")
#             return
#         current_position = world.grid.get_coordinates_in_direction(current_position, direction)


# def hexagon(world, center, amount):
#     created = 0
#     amount = amount
#
#     positions = [(center[0]+amount,center[1], center[2])]
#     pp= [(center[0]+amount,center[1], center[2])]
#     i = 0
#     dirs = world.grid.get_directions_list()
#     while created < amount-1:
#         current_pos = positions[i]
#         dir = 0
#         while dir < 6:
#             new_coords = world.grid.get_coordinates_in_direction(current_pos, dirs[dir])
#             positions.append(new_coords)
#             dir = dir + 1
#
#             if current_pos not in pp:
#                 # if world.add_particle(current_pos):
#                 #world.add_particle(current_pos)
#                 pp.append(current_pos)
#                 #     world.remove_particle_on(current_pos)
#                 created = created + 1
#         i = i + 1
#     layer = math.ceil(-1/2 + sqrt( pow(-1/2, 2) - (1-created/3)) )
#     for current_pos in pp:
#         world.add_particle((current_pos[0] - layer, current_pos[1], current_pos[2]))
