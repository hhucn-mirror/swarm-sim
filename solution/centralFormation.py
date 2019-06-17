import math

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

amount = 0
graph = {}

def solution(sim):
    print("Runde = ", sim.get_actual_round())
    if (sim.get_actual_round() == 1):
        initialize(sim)

    if (sim.get_actual_round() % 2 == 1):
        print("Calc")
    else:
        print("Move and Refresh Memory")

def initialize(sim):

    global amount
    for particle in sim.get_particle_list():
        amount = amount + 1

    centerParticle = sim.get_particle_list()[0]
    centerPos = centerParticle.coords
    print(centerPos)

    #create_locationsT(sim, centerPos)
    #create_locationsL(sim, centerPos)
    create_locationsS(sim, centerPos)

# triangle formula
def create_locationsT(sim, pos):
    d = 0
    locationCount = 0
    particleCount = amount
    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)

        while i <= d:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if locationCount < particleCount:
                sim.add_location(x, y)
            else:
                return
            locationCount = locationCount + 1
            i = i + 1
        d = d + 1

# line formula
def create_locationsL(sim, pos):
    locationCount = 0
    particleCount = amount

    while locationCount < particleCount:
        x = pos[0] + (1*locationCount)
        y = pos[1]

        if locationCount < particleCount:
                sim.add_location(x, y)
        else:
            return
        locationCount = locationCount + 1

def create_locationsS(sim, pos):
    n = round(math.sqrt(amount))
    d = 0
    locationCount = 0
    particleCount = amount

    startPos = [0, 0]

    while True:
        i = 0
        startPos[0] = pos[0] - (0.5 * d)
        startPos[1] = pos[1] - (1 * d)
        while i < n:
            x = startPos[0]+(1*i)
            y = startPos[1]
            if locationCount < particleCount:
                sim.add_location(x, y)
            else:
                return
            locationCount = locationCount + 1
            i = i + 1
        d = d+1


