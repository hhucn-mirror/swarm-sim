import lib.swarm_sim_header as header


def solution(world):
    global leader
    if world.get_actual_round() == 1:
        handle_first_round(world)
        ##sim.get_particle_map_id()[leader]
    else:
        if leader.state == "scanning":
            handle_scanning(leader)
        elif leader.state == "caving":
            handle_caving(leader)
        elif leader.state == "toTile":
            handle_to_tile(leader)
        elif leader.state == "taking":
            handle_taking(leader)
        elif leader.state == "dropping":
            handle_dropping(leader)
        elif leader.state == "in_cave":
            handle_in_cave(leader)
        elif leader.state == "checking":
            handle_checking(leader)


def handle_first_round(world):
    global leader
    leader, distance, closest_tile_coordinates = getIdOfNearestParticleToIsland(world)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "coating_locations", [])
    setattr(leader, "caving_locations", [])
    setattr(leader, "starting_location", ())
    setattr(leader, "active_matters", world.particles.copy())
    leader.active_matters.remove(leader)
    setattr(leader, "am_distances", get_sorted_list_of_particles_distances(leader))
    setattr(leader, "aim", ())
    setattr(leader, "prev_aim", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "path_list", [])
    setattr(leader, "neighbors", {})
    setattr(leader, "obstacle_dir", False)
    setattr(leader, "cave_entrance", [])
    setattr(leader, "cave_exit", None)
    setattr(leader, "in_cave", False)
    setattr(leader, "first_level", True)

    if distance == 1:
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
        leader.coating_locations.append(leader.coordinates)
        leader.prev_aim =  leader.coordinates
        leader.move_to(dire)
        setattr(leader, "state", "scanning")
        print("Start with scanning")
    else:
        setattr(leader, "state", "toTile")
        leader.aim = closest_tile_coordinates
        leader.aim_path = world.grid.get_shortest_path(leader.coordinates, closest_tile_coordinates)
        print("Start with going to Tile")


def cave_check(leader):
    if leader.obstacle_dir:
        index_dir = leader.directions_list.index(leader.obstacle_dir)
        neighbors_string =""
        for idx in range(len(leader.directions_list)):
            dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
            if leader.matter_in(dire) is True:
                neighbors_string =  neighbors_string + "M"
            else:
                neighbors_string =  neighbors_string + "L"

        dire = None
        if len(leader.neighbors) == 2:
            if neighbors_string == "MLLLML":
                dire = leader.directions_list[(5 + index_dir) % len(leader.directions_list)]
                print("Found Cave MLLL and entrance in ", dire, leader.coordinates )
            elif neighbors_string == "MLMLLL":
                dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
                print("Found Cave and entrance in ", dire, leader.coordinates )
            elif neighbors_string == "MLLMLL":
                for idx in range(len(leader.directions_list)):
                    dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
                    if leader.matter_in(dire) is False and leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
                        if idx < 3:
                            dire = leader.directions_list[(4 + index_dir) % len(leader.directions_list)]
                        else:
                            dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]

        elif len(leader.neighbors) == 3:
            if neighbors_string == "MMLMLL":
                dire = leader.directions_list[(2 + index_dir) % len(leader.directions_list)]
            elif neighbors_string == "MLMMLL" or neighbors_string == "MLMLLM":
                print(" Check Found 3 Cave")
                dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
            elif neighbors_string == "MLLMML":
                dire = leader.directions_list[(5 + index_dir) % len(leader.directions_list)]
        if dire is not None:
            if leader.prev_aim != leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
                leader.prev_aim = leader.coordinates
                leader.cave_entrance.append(leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire))
                if not leader.cave_exit:
                    leader.cave_exit = leader.coordinates
                leader.move_to(dire)
                print(" Check Found Cave")
                return True
    return False


def get_neighbors(leader):
    leader.neighbors = {}
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.neighbors[dir] = leader.get_matter_in(dir)
            leader.obstacle_dir = dir
    return


def handle_caving(leader):
    if leader.coordinates != leader.starting_location:
        get_neighbors(leader)
        if cave_check(leader):
            if leader.first_level:
                leader.state = "scanning"
                print("from caving --> 1st_level_scanning")
                return
            leader.state = "scanning"
            print("from caving --> scanning")
            return

        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
            if get_an_adjacent_tile_directions_scanning(leader): #and leader.coordinates not in leader.cave_entrance
                leader.coating_locations.append(leader.coordinates)
                leader.caving_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)


def handle_in_cave(leader):
    if reached_aim(leader.aim, leader):
        #leader.prev_aim = leader.coordinates
        leader.move_to(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))
        # leader.am_distances = get_sorted_list_of_particles_distances(leader)
        # leader.aim = leader.am_distances.pop(0)
        # leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        print("from in_cave --> checking")
        leader.in_cave = False
        leader.state = "checking"


def handle_scanning(leader):
    if leader.coordinates != leader.starting_location:
        get_neighbors(leader)
        if cave_check(leader):
            leader.state = "caving"
            if leader.first_level:
                print("1st_level_scanning --> caving")
                return
            print("scanning --> caving")
            return

        if leader.first_level:
            if get_an_adjacent_obstacle_directions_scanning(leader):
                dire = obstacles_free_direction(leader)
                if get_an_adjacent_tile_directions_scanning(leader):
                    leader.coating_locations.append(leader.coordinates)
        else:
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
        leader.prev_aim = leader.coordinates
        leader.move_to(dire)
    else:
        leader.state = "checking"
        if leader.first_level:
            print("1st_level_scanning --> checking")
            leader.first_level = False
            return
        print("scanning --> checking")


def handle_to_tile(leader):
    if reached_aim(leader.aim, leader):
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)

        print("from toTile --> 1st level scanning")
        leader.state = "scanning"


def handle_taking(leader):
    if leader.in_cave:
        print("from taking -->  in_cave")
        leader.aim = leader.cave_exit
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        leader.prev_aim = leader.coordinates
        leader.state = "in_cave"
        return
    if reached_aim(leader.aim, leader):
        leader.take_particle_on(leader.aim)
        leader.coating_locations =  get_sorted_list_of_locations_distances(leader)
        leader.aim = leader.coating_locations.pop(0)
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        print("from taking --> dropping")
        leader.state = "dropping"


def handle_dropping(leader):
    if leader.in_cave:
        print("from dropping -->  in_cave")
        leader.aim = leader.cave_exit
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        leader.prev_aim = leader.coordinates
        leader.state = "in_cave"
        return
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        leader.active_matters.remove((leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))))
        leader.state = "checking"
        print("from dropping -->  checking")


def handle_checking(leader):
    if not leader.coating_locations:
        print("from checking -->  scanning")
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)
        leader.state = "scanning"
    elif leader.active_matters:
        if leader.in_cave:
            print("from checking -->  in_cave")
            leader.aim = leader.cave_exit
            leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
            leader.prev_aim = leader.coordinates
            leader.state = "in_cave"
        else:
            print("from checking -->  taking")
            leader.am_distances = get_sorted_list_of_particles_distances(leader)
            leader.aim = leader.am_distances.pop(0)
            leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
            leader.prev_aim = leader.coordinates
            leader.state = "taking"
    else:
        print("It is my turn")
        leader.state = "leader"



def get_sorted_list_of_particles_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_particles_coordinates = []
    for particle in leader.active_matters:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, particle.coordinates)
        distances.append(calculated_distance)
        tmp_dict[particle.coordinates] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist:
                if coords not in sorted_list_of_particles_coordinates:
                    sorted_list_of_particles_coordinates.append(coords)
    return sorted_list_of_particles_coordinates



def get_sorted_list_of_locations_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_locations_coordinates = []
    for location in leader.coating_locations:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, location)
        distances.append(calculated_distance)
        tmp_dict[location] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist:
                if coords not in sorted_list_of_locations_coordinates:
                    sorted_list_of_locations_coordinates.append(coords)
    return sorted_list_of_locations_coordinates


def obstacle_avoidance_path(leader, obstacle_dir, cave=False):
    index_of_dir = leader.directions_list.index(obstacle_dir)
    if index_of_dir is not None:
        for idx in range(len(leader.directions_list)):
            dir_1 = leader.directions_list[(idx + index_of_dir) % len(leader.directions_list)]
            bla = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_1)

            if cave is False and leader.matter_in(dir_1) is False : #and bla not in leader.cave_entrance
                break
            elif cave is True and leader.matter_in(dir_1) is False and bla not in leader.cave_entrance and bla not in leader.caving_locations:
                break

        idx = len(leader.directions_list)
        while idx >= 0:
            dir_2 = leader.directions_list[(idx + index_of_dir) % len(leader.directions_list)]
            bla = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2)
            if cave is False and leader.matter_in(dir_2) is False :
                break
            elif cave is True and leader.matter_in(dir_2) is False and bla not in leader.cave_entrance  and bla not in leader.caving_locations:
                break
            idx -= 1
        path_1 = [dir_1]
        path_2 = [dir_2]
        path_1.extend( leader.world.grid.get_shortest_path(leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_1), leader.aim))
        path_2.extend(leader.world.grid.get_shortest_path(leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2), leader.aim))
        if len(path_1) >= len(path_2):
            if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2):
                return path_1
        elif len(path_1) < len(path_2):
            if leader.prev_aim != leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_1):
                return path_1
        return path_2


def obstacles_free_direction(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False and leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
            idx_2 = len(leader.directions_list)
            while idx_2 >= 0:
                dire = leader.directions_list[(idx_2 + index_dir) % len(leader.directions_list)]
                if leader.matter_in(
                        dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
                        leader.coordinates, dire):
                    return dire
                idx_2 -= 1
        if leader.matter_in(dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
            leader.coordinates, dire):
            return dire


def get_adjacent_obstacles_directions(leader):
    leader.obstacle_dir.clear()
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir.append(dir)
    if bool(leader.obstacle_dir):
        return True
    return False
    #return surroundings
# region surround island


def get_an_adjacent_obstacle_directions(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def get_an_adjacent_obstacle_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if leader.get_matter_in(dir).type == "particle" and leader.get_matter_in(dir) in leader.active_matters:
                leader.active_matters.remove(leader.get_matter_in(dir))
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def get_an_adjacent_tile_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if leader.get_matter_in(dir).type == "tile":
                return True
    return False


def getIdOfNearestParticleToIsland(sim):
    closestParticle = sim.get_particle_list()[0]
    min = None
    for particle in sim.get_particle_list():
        for tile in sim.get_tiles_list():
            value = sim.grid.get_distance(particle.coordinates, tile.coordinates)
            if min is None:
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
            elif (value < min):
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
    return closestParticle, min, closest_tile_coordinate


def reached_aim(aim, leader):
    if leader.aim_path:
        next_dir = leader.aim_path.pop(0)
        next_coords = header.get_coordinates_in_direction(leader.coordinates, next_dir)
        #print(" next coords ", next_coords, " path ", leader.aim_path )
        if leader.coordinates in leader.caving_locations and leader.aim not in leader.caving_locations:
            print("Inside the cave")
            leader.in_cave = True
        elif leader.coordinates in leader.coating_locations :
            print("Outside the cave")
            leader.in_cave = False
        elif leader.in_cave  and leader.aim not in leader.caving_locations:
            print("New caving location")
            leader.caving_locations.append(leader.coordinates)
            leader.in_cave = True
        else:
            leader.in_cave = False

        if aim == next_coords:
            return True
        if leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_dir) == leader.prev_aim :
            if get_an_adjacent_obstacle_directions(leader):
                leader.aim_path = obstacle_avoidance_path(leader, leader.obstacle_dir)
                next_dir = leader.aim_path.pop(0)
                next_coords = leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_dir)
        if  leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_dir) in leader.cave_entrance:
            print ("I'm infront of cave")
            if leader.state == "taking":
                print("Taking")
                if get_an_adjacent_obstacle_directions(leader):
                    leader.aim_path = obstacle_avoidance_path(leader, leader.obstacle_dir, True)
                    next_dir = leader.aim_path.pop(0)
        if leader.tile_in(next_dir):
            print(" tile obstacle ")
            leader.aim_path = obstacle_avoidance_path(leader, next_dir)
            print(" new path ", leader.aim_path)
            return False
        prev_aim = leader.coordinates
        if not leader.move_to(next_dir):
            print("obstacle")
            leader.aim_path = obstacle_avoidance_path(leader, next_dir)
            print ("new_path", leader.aim_path)
            return False
        leader.prev_aim = prev_aim
        #leader.move_to(next_dir)
        return False