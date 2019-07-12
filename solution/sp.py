import logging
import math
import random
import sys
import copy
from copy import deepcopy
import collections


black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

def getAllSuroundingCoords(pcoords, world):
    return [
        world.get_coords_in_dir(pcoords, E),
        world.get_coords_in_dir(pcoords, W),
        world.get_coords_in_dir(pcoords, NE),
        world.get_coords_in_dir(pcoords, NW),
        world.get_coords_in_dir(pcoords, SE),
        world.get_coords_in_dir(pcoords, SW)
    ]

def solution( sim):
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            setattr(particle, "current_way", [])
            tCoords = random.choice(sim.get_tiles_list()).coords
            particle.current_way = findWayToAim(particle.coords, tCoords, sim)
            particle.current_way.pop(0)
        if sim.get_actual_round() > 1:
            if len(particle.current_way):
                dir = getDirectionForCoords(particle.current_way.pop(0), particle.coords)
                if not particle.particle_in(dir):
                    particle.move_to(dir)

def getCoordsOfNearestTile(partilceCoords, world):
    tileCoords = world.get_tile_map_coords()

    # max float
    min = 1.7976931348623157e+308
    x = world. get_sim_x_size()
    y = world.get_sim_y_size()
    for tCoords in tileCoords:
        xdiff = partilceCoords[0] - tCoords[0]
        ydiff = partilceCoords[1] - tCoords[1]
        value = math.sqrt((xdiff * xdiff) + (ydiff * ydiff))
        if (value < min):
            min = value
            x = tCoords[0]
            y = tCoords[1]
    return (x, y)


def findWayToAim(lCoords, tCoords, world):
    coordLists = [[lCoords]]
    visitedCoords = [lCoords]
    while len(coordLists) > 0:
        currentList = coordLists.pop(0)
        length = len(currentList)
        if areAimCoordinatesReachable(tCoords, currentList[length - 1], world):
            return currentList
        else:
            aroundLast = getAllSuroundingCoords(currentList[length - 1], world)
            for tmp in aroundLast:
                if (isCoordUnvisitedAndFree(tmp, visitedCoords, world)):
                    newList = deepcopy(currentList)
                    newList.append(tmp)
                    coordLists.append(newList)
                    visitedCoords.append(tmp)


def areAimCoordinatesReachable(aCoords, bCoords, world):
    if aCoords == bCoords:
        return True
    around = getAllSuroundingCoords(aCoords, world)
    for tmp in around:
        if tmp == bCoords:
            return True
    return False

def isCoordUnvisitedAndFree(coord, visitedCoords, world):
    if coord in visitedCoords:
        return False
    if coord in world.get_particle_map_coords():
        return False
    if coord in world.get_tile_map_coords():
        return False
    return True

def getDirectionForCoords(toCoords, fromCoords):
    if toCoords[1] == fromCoords[1] and toCoords[0] == fromCoords[0]:
        return S
    # same height
    if toCoords[1] == fromCoords[1]:
        if toCoords[0] < fromCoords[0]:
            return W
        return E
    # different height
    # aim is lower than currentpos
    if toCoords[1] < fromCoords[1]:
        if toCoords[0] < fromCoords[0]:
            return SW
        return SE
    # aim is higher than currentpos
    if toCoords[0] < fromCoords[0]:
        return NW
    return NE