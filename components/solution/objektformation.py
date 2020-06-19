import random
import math
from core.swarm_sim_header import *

DEBUG = True

# directions
move_east = (1, 0, 0)
move_southeast = (0.5, -1, 0)
move_southwest = (-0.5, -1, 0)
move_west = (-1, 0, 0)
move_northwest = (-0.5, 1, 0)
move_northeast = (0.5, 1, 0)

# Phases
phase_startCounting = 1
phase_backtracking = 2
phase_countingFinished = 3
phase_countupObjects = 4
phase_waitforsubjects1 = 5
phase_startObject = 6
phase_PickupObject = 7
phase_PlaceObject = 8
phase_checkifready = 9
phase_waitforsubjects2 = 10
phase_end = 11

# NONE TYPE BEI NEXT TARGET!!!! NOCHMAL ÜBERPRÜFEN!!!
def solution(sim):
    global numberoftiles
    for particle in sim.get_agent_list():

        if sim.get_actual_round() == 1:
            setattr(particle, "phase", 0)
            setattr(particle, "numberoftiles", 0)
            setattr(particle, "nextTarget", (0, 0, 0))
            setattr(particle, "nextTile", (0, 0, 0))
            setattr(particle, "keeptarget", False)
            setattr(particle, "countedTiles", [])

            particle.phase = phase_startCounting
            particle.create_location()
            particle.write_to_with(sim.get_item_map_coordinates()[particle.coordinates], "tile", "counted")
            particle.countedTiles.append(particle.coordinates)

        if DEBUG:
            print("Round %i, Phase %i, Particle %i, number of tiles %i" % (
            sim.get_actual_round(), particle.phase, particle.number, len(particle.countedTiles)))

        if particle.phase == phase_startCounting:
            startCounting(sim, particle)

        elif particle.phase == phase_backtracking:
            backtracking(sim, particle)

        elif particle.phase == phase_countingFinished:
            particle.write_to_with(sim.get_agent_list()[0], particle.number, len(particle.countedTiles))
            particle.phase = phase_waitforsubjects1

        elif particle.phase == phase_waitforsubjects1:
            waitingforparticles(sim, phase_waitforsubjects1, phase_countupObjects)

        elif particle.phase == phase_countupObjects:
            countupObjects(sim, particle)

        elif particle.phase == phase_waitforsubjects2:
            waitingforparticles(sim, phase_waitforsubjects2, phase_startObject)

        elif particle.phase == phase_startObject:
           # if particle.number == 3 or particle.number == 22 or particle.number == 37 or particle.number == 41 or particle.number == 55:
            #    particle.phase = phase_checkifready
            #else:

            startObject(sim, particle)

        elif particle.phase == phase_PickupObject:
            PickupObject(sim, particle)

        elif particle.phase == phase_PlaceObject:
            PlaceObject(sim, particle)

        elif particle.phase == phase_checkifready:
            checkifready(sim, particle)

        elif particle.phase == phase_end:
            end(sim, particle)

        else:
            if DEBUG:
                print("Unknown Phase: %i" % (particle.phase))

############################# methods of phases ###############################################################

def startCounting(sim, particle):
    moegricht = possibleDirections(sim, particle)

    if particle.number == 3:
        print(moegricht)

    if not moegricht:
        particle.phase = phase_backtracking
    else:
        rand = random.choice(moegricht)
        if particle.number == 3:
            print("rand: ", rand)
        print(particle.move_to(rand))
        particle.create_location()
        particle.write_to_with(sim.get_item_map_coordinates()[particle.coordinates], "tile", "counted")
        particle.countedTiles.append(particle.coordinates)

def backtracking(sim, particle):
    gegangenerWeg = particle.get_gegangenerWeg()
    #print(gegangenerWeg)

    if not gegangenerWeg:
        particle.phase = phase_startCounting
        moegricht = possibleDirections(sim, particle)

        if not moegricht:
            particle.phase = phase_countingFinished

    else:
        rueckweg = particle.get_rueckweg(gegangenerWeg)
        particle.move_to(rueckweg[0])
        gegangenerWeg.pop()
        gegangenerWeg.pop()
        particle.set_gegangenerWeg(gegangenerWeg)
        particle.phase = phase_startCounting

def countupObjects(sim, particle):
    if particle.number == 1:

        particle.numberoftiles = countuptiles(sim, particle)
        print("counted number of tiles: ", particle.numberoftiles)
        if sim.check_count(particle.numberoftiles):
            print("Count successful")
        else:
            print("Count unsuccessful")

        objekt = objectcoordinates(particle)
        i = 0
        j = 10000
        while i < particle.numberoftiles:
            particle.write_to_with(sim.get_agent_list()[0], j, objekt[i])
            #print(j, objekt[i], sep=":")
            i = i + 1
            j = j + 1
        particle.write_to_with(sim.get_agent_list()[0], j, "end")

    for koordinate in particle.countedTiles:
        i = 1000
        while particle.read_from_with(sim.get_agent_list()[0], i) is not None:
            i = i + 1
        particle.write_to_with(sim.get_agent_list()[0], i, koordinate)
        #print(i, koordinate, sep=":")

    particle.phase = phase_waitforsubjects2
    #return sim.get_agent_list()[0].numberoftiles

def startObject(sim, particle):
    # particle has target ==> particle needs next tile coordinate
    if particle.keeptarget == True:
        particle.keeptarget = False
        i = 1000
        while particle.read_from_with(sim.get_agent_list()[0], i) == "deleted":
            i = i + 1
        particle.nextTile = particle.read_from_with(sim.get_agent_list()[0], i)
        if particle.nextTile is None:
            particle.phase = phase_checkifready
        else:
            particle.write_to_with(sim.get_agent_list()[0], i, "deleted")
            particle.phase = phase_PickupObject

    # particle has no target ==> particle needs tile and target coordinates
    else:
        j = 10000
        while particle.read_from_with(sim.get_agent_list()[0], j) == "occupied":
            j = j + 1
        if particle.read_from_with(sim.get_agent_list()[0], j) == "end":
            particle.phase = phase_checkifready
        else:
            particle.nextTarget = particle.read_from_with(sim.get_agent_list()[0], j)
            particle.write_to_with(sim.get_agent_list()[0], j, "occupied")
            if not particle.carries_item():
                i = 1000
                while particle.read_from_with(sim.get_agent_list()[0], i) == "deleted":
                    i = i + 1
                particle.nextTile = particle.read_from_with(sim.get_agent_list()[0], i)
                print("Nächste Kachel: ", particle.nextTile)
                particle.write_to_with(sim.get_agent_list()[0], i, "deleted")

            particle.phase = phase_PickupObject

def PickupObject(sim, particle):
    #print("Nächste Kachel: ", particle.nextTile)
    aktPos = particle.coordinates
    if not particle.carries_item():
        if particle.nextTile is None:
            particle.phase = phase_startObject
            particle.keeptarget = True

        elif aktPos == particle.nextTile:
            if particle.is_on_item():
                if particle.read_from_with(sim.get_item_map_coordinates()[particle.coordinates], "tile") == "counted":
                    particle.write_to_with(sim.get_item_map_coordinates()[particle.coordinates], "tile", "postponed")
                    particle.take_item()
                    particle.phase = phase_PlaceObject

                else:
                    particle.keeptarget = True
                    particle.phase = phase_startObject

            else:
                particle.phase = phase_startObject

        else:
            movetocoordinate(particle, aktPos, particle.nextTile)

    else:
        particle.phase = phase_PlaceObject

def PlaceObject(sim, particle):
    aktPos = particle.coordinates
    if particle.nextTarget is None:
        particle.phase = phase_startObject

    elif aktPos == particle.nextTarget:
        if particle.is_on_item():
            if particle.read_from_with(sim.get_item_map_coordinates()[particle.coordinates], "tile") == "counted":
                particle.write_to_with(sim.get_item_map_coordinates()[particle.coordinates], "tile", "postponed")

        else:
            particle.drop_item()

        particle.phase = phase_startObject

    else:
        movetocoordinate(particle, aktPos, particle.nextTarget)

def checkifready(sim, particle):
    if particle.carries_item():
        if not particle.is_on_item():
            particle.drop_item()
            i = 1000
            while not particle.read_from_with(sim.get_agent_list()[0], i) == "deleted":
                i = i + 1
            particle.write_to_with(sim.get_agent_list()[0], i, particle.coordinates)
            particle.write_to_with(sim.get_item_map_coordinates()[particle.coordinates], "tile", "counted")
    else:
        particle.phase = phase_end

    particle.move_to(move_northwest)


def end(sim, particle):
    particle.move_to(move_northwest)
    check = True
    for particle in sim.agents:
#
        if particle.phase != phase_end:
            check = False
    if check == True:
        print(particle.number)
        if sim.check_formation():
            print("Formation Construction successful")
        else:
            print("Formation Construction unsuccessful")
        sim.set_successful_end()
        particle.phase = phase_checkifready

       # nur wenn beide Partikel fertig sind endet das Programm
#
        if DEBUG:
            print("*** Finish ***")
#
    return 0

################################### other methods ##########################################################

def possibleDirections(sim, particle):
    richtungen = [move_east, move_southwest, move_southeast, move_west, move_northeast, move_northwest]
    moegricht = []
    for richtung in richtungen:
        if not particle.agent_in(richtung) and particle.item_in(richtung) and not particle.read_from_with(
                sim.get_item_map_coordinates()[get_coordinates_in_direction(particle.coordinates, richtung)],
                "tile") == "counted":
            moegricht.append(richtung)

    return moegricht


def waitingforparticles(sim, waitphase, continuationphase):
    check = True
    for particle in sim.agents:

        if particle.phase != waitphase:
            check = False

    if check == True:
        for particle in sim.agents:
            particle.phase = continuationphase


def objectcoordinates(particle):
    s_rhombus = math.sqrt(particle.numberoftiles)
    s_triangle = -0.5 + math.sqrt(0.25 + 2 * particle.numberoftiles)
    s_hexagon = 0.5 + math.sqrt(0.25 - ((1 - particle.numberoftiles) / 3))

    objekt = []

    if s_triangle.is_integer():
        # Koordinaten des Dreiecks:
        x = 0
        y = 0
        z = 0
        s_triangle2 = s_triangle
        while y < s_triangle:
            while x < s_triangle2 + z:
                objekt.append((x, y, 0))
                x = x + 1

            y = y + 1
            z = z + 0.5
            x = z
            s_triangle2 = s_triangle2 - 1

    elif s_rhombus.is_integer():
        # Koordinaten der Raute:
        x = 0
        y = 0
        z = 0
        while y < s_rhombus:
            while x < s_rhombus + z:
                objekt.append((x, y, 0))
                x = x + 1

            y = y + 1
            z = z + 0.5
            x = z

    elif s_hexagon.is_integer():
        # Koordinaten des Hexagons:
        x = 0.5
        y = 1
        i = 1
        phase = 1

        objekt.append((0, 0, 0))

        while i < s_hexagon:
            j = 1
            while j <= i:
                if not phase == 7:
                    objekt.append((x, y, 0))
                if phase == 1:
                    x = x + 0.5
                    y = y - 1
                elif phase == 2:
                    x = x - 0.5
                    y = y - 1
                elif phase == 3:
                    x = x - 1
                elif phase == 4:
                    x = x - 0.5
                    y = y + 1
                elif phase == 5:
                    x = x + 0.5
                    y = y + 1
                elif phase == 6:
                    x = x + 1
                else:
                    i = i + 1
                    j = i
                    x = x + 0.5
                    y = y + 1
                    phase = 0
                j = j + 1
            phase = phase + 1

    else:
        # Koordinaten der Linie:
        x = 0
        y = 0
        z = 0

        while z < particle.numberoftiles:
            objekt.append((x, y, 0))
            x = x + 0.5
            y = y + 1
            z = z + 1

    return objekt


def countuptiles(sim, particle):
    numberofparticles = sim.get_amount_of_agents()
    i = 1
    while i <= numberofparticles:
        zahl = particle.read_from_with(sim.get_agent_list()[0], i)
        if zahl is not None:
            particle.numberoftiles = particle.numberoftiles + zahl
        else:
            numberofparticles = numberofparticles + 1
        i = i + 1

    return particle.numberoftiles


def movetocoordinate(particle, aktPos, coordinate):
    richtungen = [move_northeast, move_east, move_southeast, move_northwest, move_west, move_southwest]
    if aktPos[0] <= coordinate[0] and aktPos[1] < coordinate[1]:
        if particle.agent_in(move_northeast):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_northeast)

    elif aktPos[0] >= coordinate[0] and aktPos[1] < coordinate[1]:
        if particle.agent_in(move_northwest):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_northwest)

    elif aktPos[0] <= coordinate[0] and aktPos[1] > coordinate[1]:
        if particle.agent_in(move_southeast):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_southeast)

    elif aktPos[0] >= coordinate[0] and aktPos[1] > coordinate[1]:
        if particle.agent_in(move_southwest):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_southwest)

    elif aktPos[0] > coordinate[0]:
        if particle.agent_in(move_west):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_west)

    elif aktPos[0] < coordinate[0]:
        if particle.agent_in(move_east):
            particle.move_to(random.choice(richtungen))

        else:
            particle.move_to(move_east)
