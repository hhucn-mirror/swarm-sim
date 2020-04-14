from copy import deepcopy

QUICK_COATING = False

ONE_LAYER_COATING = False

CAVING = True
ORDERING = True

ENTRANCE = 100
PREVIOUS = 11
BESIDE_SUBJECT = 103
FREE_LOCATION = 1000
SUBJECT = 200


S3_BS_P_E= 3*SUBJECT + BESIDE_SUBJECT + ENTRANCE + PREVIOUS
S3_P_E2= 3*SUBJECT + 2*ENTRANCE + PREVIOUS
S4_P_E= 4*SUBJECT + ENTRANCE +  PREVIOUS


S2_BS3_P= 2*SUBJECT + 3*BESIDE_SUBJECT + PREVIOUS
S3_BS2_P= 3*SUBJECT + 2*BESIDE_SUBJECT + PREVIOUS

FL_S2_BS_P_E= FREE_LOCATION+ 2*SUBJECT + BESIDE_SUBJECT + PREVIOUS + ENTRANCE
FL_S2_BS2_P= FREE_LOCATION+ 2*SUBJECT + 2*BESIDE_SUBJECT + PREVIOUS
FL_S3_BS_P= FREE_LOCATION + 3*SUBJECT + BESIDE_SUBJECT + PREVIOUS

S4_BS_P= 4*SUBJECT + BESIDE_SUBJECT + PREVIOUS
S5_P= 5*SUBJECT + PREVIOUS


leader = None

def next_leader(world, coated_locations, subject_locations):
    global leader
    leader, distance, closest_tile_coordinates = get_leader_distance_to_object(world, coated_locations, subject_locations)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "uncoated_locations", [])
    setattr(leader, "cave_locations", [])
    setattr(leader, "tunnel_locations", [])
    setattr(leader, "previous_location", ())
    setattr(leader, "subject_locations", subject_locations.copy())
    if leader.coordinates in leader.subject_locations:
        if isinstance(leader.subject_locations, dict):
            del leader.subject_locations[leader.coordinates]
        else:
            leader.subject_locations.remove(leader.coordinates)
    leader.subject_locations = sorting_list(leader.coordinates, leader.subject_locations, leader.world.grid.get_distance)
    setattr(leader, "coated_locations", [])
    setattr(leader, "aim", ())
    setattr(leader, "shortest_path", [])
    setattr(leader, "cave_exit_storage", [])
    setattr(leader, "dead_end_flag", False)
    setattr(leader, "state_storage", [])
    setattr(leader, "state", "toTile")
    if distance == 1:
        setattr(leader, "state", "scanning")
    else:
        setattr(leader, "state", "toTile")
        leader.aim = closest_tile_coordinates
        leader.shortest_path = get_shortest_path(leader.coordinates, closest_tile_coordinates, leader.world)
    return leader


def solution(world):
    global leader
    if world.get_actual_round() == 1:
        leader = next_leader(world, world.tile_map_coordinates, world.particle_map_coordinates)
    if leader:
        if leader.state == "toTile":
            handle_go_to_object(leader)
        elif leader.state == "scanning":
            handle_scanning(leader)
        elif leader.state == "cave_scanning":
            handle_cave_scanning(leader)
        elif leader.state == "cave_discovery":
            handle_cave_discovery(leader)
        elif leader.state == "taking":
            handle_taking(leader)
        elif leader.state == "coating":
            handle_coating(leader)
        elif leader.state == "cave_escaping":
            handle_cave_escaping(leader)
        elif leader.state == "leader_coating":
            handle_leader_coating(leader)
        elif leader.state == "finished":
            handle_finished(leader)
            world.csv_round.update_finished()


def scanning(leader, uncoated_storage):
    sum_of_neighbors_labels, neighbor_number_map_direction = get_neighbors(leader.directions_list,
                                                                           leader.matter_in, 
                                                                           get_direction_for(leader.coordinates, 
                                                                           leader.previous_location))
    finished=False
    if (sum_of_neighbors_labels > FREE_LOCATION and
        sum_of_neighbors_labels != FL_S2_BS_P_E) or \
        sum_of_neighbors_labels == S4_BS_P or \
        sum_of_neighbors_labels == S3_BS2_P:
        
        finished = wide_space_scanning(finished, leader, 
                                       neighbor_number_map_direction, 
                                       sum_of_neighbors_labels, uncoated_storage)
    else:
        
        tunnel_entrance(leader, sum_of_neighbors_labels, neighbor_number_map_direction)
        
    return uncoated_storage, finished


def wide_space_scanning(finished, leader, neighbor_number_map_direction, sum_of_neighbors_labels, uncoated_storage):
    if leader.coordinates not in leader.uncoated_locations \
            and leader.coordinates not in leader.tunnel_locations and leader.coordinates != leader.aim:
        uncoated_storage.append(leader.coordinates)
    direction = next_direction(leader.coordinates, sum_of_neighbors_labels, neighbor_number_map_direction,
                               leader.uncoated_locations + leader.tunnel_locations)
    if direction:
        move_to(direction, leader)
    else:
        finished = True
    leader.world.csv_round.update_scanning()
    return finished


def move_to(direction, leader):
    leader.previous_location = leader.coordinates
    leader.move_to(direction)


def handle_scanning(leader):
    leader.uncoated_locations, finished  = scanning(leader, leader.uncoated_locations )
    if leader.coordinates in leader.uncoated_locations or finished:
        finished_scanning(leader)


def beaming(leader):
    leader.uncoated_locations = list(dict.fromkeys(leader.uncoated_locations))
    while leader.uncoated_locations:
        uncoated_location = leader.uncoated_locations.pop()
        if leader.subject_locations:
            if leader.coordinates == uncoated_location:
                sumo, neigh = get_neighbors(leader.directions_list, leader.matter_in, get_direction_for(leader.coordinates, leader.previous_location) )
                direction = next_direction(leader.coordinates, sumo, neigh, leader.previous_location)
                move_to(direction, leader)
                leader.world.csv_round.update_metrics(steps=-1)
            subject_location =leader.subject_locations.pop(0)
            # shortest_path = get_shortest_path(leader.coordinates, subject_location, leader.world)
            # leader.world.csv_round.update_metrics(steps=len(shortest_path)-1)
            leader.take_particle_on(subject_location)
            #shortest_path = get_shortest_path(subject_location, uncoated_location, leader.world)
            # leader.world.csv_round.update_metrics(steps=len(shortest_path)-1)
            leader.drop_particle_on(uncoated_location)
            leader.coated_locations.append(uncoated_location)
        else:
            leader.aim = uncoated_location
            return
    if ONE_LAYER_COATING:
        delete_tunnel_entrances(leader)
        handle_finished(leader)


def handle_scanned_locations(leader):
    if not ONE_LAYER_COATING:
        if CAVING:
            if enough_particles(leader):
                if leader.dead_end_flag:
                    if leader.tunnel_locations:
                        leader.uncoated_locations.extend(leader.tunnel_locations)
                    leader.dead_end_flag = False
    else:
        if leader.tunnel_locations:
            leader.uncoated_locations.extend(leader.tunnel_locations)
        leader.uncoated_locations = list(dict.fromkeys(leader.uncoated_locations))


def enough_particles(leader):
    subjects_cardinality = len(leader.subject_locations) + 1  # for the leader

    locations_cardinality = len(leader.uncoated_locations)
    tunnel_cardinality = 0
    if leader.tunnel_locations:
        tunnel_cardinality = len(leader.tunnel_locations)
        print("tunnel cardinality ", tunnel_cardinality)
    if subjects_cardinality < tunnel_cardinality:
        reduce_tunnel_locations(leader, subjects_cardinality, tunnel_cardinality)

        leader.uncoated_locations = leader.tunnel_locations
        return False
    elif tunnel_cardinality <= subjects_cardinality < locations_cardinality+tunnel_cardinality:
        leader.uncoated_locations = leader.tunnel_locations + leader.uncoated_locations[0:subjects_cardinality-tunnel_cardinality]
        return False

    return True


def reduce_tunnel_locations(leader, subjects_cardinality, tunnel_cardinality):
    leader.uncoated_locations.clear()
    i = 0
    while i < tunnel_cardinality - subjects_cardinality:
        if leader.tunnel_locations:
            if i % 2 == 0:
                leader.tunnel_locations.pop(0)
            elif i % 2 == 1:
                leader.tunnel_locations.pop()
        i += 1


def finished_scanning(leader):
    handle_scanned_locations(leader)
    leader.aim = None
    if leader.subject_locations and leader.uncoated_locations:
        if QUICK_COATING:
            beaming(leader)
            if not leader.subject_locations and (leader.uncoated_locations or leader.aim):
                it_is_leader_turn_to_coat(leader)
            else:
                go_scanning(leader)
        else:
            go_taking_particles(leader)
    else:
        it_is_leader_turn_to_coat(leader)


def found_tunnel_entrance_go_for_cave_discovery(leader, direction_entrance):
    leader.tunnel_locations.append(leader.coordinates)
    leader.cave_exit_storage.append(leader.coordinates)
    leader.directions_entrance = direction_entrance
    leader.state = "cave_discovery"
    move_to(direction_entrance , leader)
    leader.world.csv_round.update_cave_discovery()


def tunnel_entrance(leader, sum_of_neighbors_labels, neighbor_number_map_direction ):

    if sum_of_neighbors_labels != FL_S2_BS_P_E \
            and sum_of_neighbors_labels != FL_S2_BS2_P  and sum_of_neighbors_labels != S3_BS2_P \
            and leader.coordinates not in leader.uncoated_locations + leader.tunnel_locations:
    
        direction_entrance = handling_special_entrance(leader)
    
    elif sum_of_neighbors_labels == FL_S2_BS_P_E :
    
        for direction in neighbor_number_map_direction:
            if neighbor_number_map_direction[direction] == ENTRANCE:
                direction_entrance = direction

    found_tunnel_entrance_go_for_cave_discovery(leader, direction_entrance)
    return True


def handling_special_entrance(leader):
    direction_exit = get_exit_direction(leader)
    own = leader.coordinates
    leader.move_to(direction_exit)
    if leader.coordinates in leader.uncoated_locations:
        leader.uncoated_locations.remove(leader.coordinates)
    leader.world.csv_round.update_metrics(steps=- 1)
    direction_entrance = leader.world.grid.get_nearest_direction(leader.coordinates, own)
    return direction_entrance


def get_exit_direction(leader):
    for idx in range(len(leader.directions_list)):
        if get_coordinates_in_direction(leader.coordinates, leader.directions_list[
            idx % len(leader.directions_list)]) == leader.previous_location:
            direction_left = leader.directions_list[(idx + 1) % len(leader.directions_list)]
            direction_right = leader.directions_list[(idx - 1) % len(leader.directions_list)]
            if leader.matter_in(direction_right) is False:
                direction_exit = direction_right
            else:
                direction_exit = direction_left
    return direction_exit


def handle_cave_discovery(leader):
    sum_of_neighbors_labels, neighbor_number_map_direction = get_neighbors(leader.directions_list, leader.matter_in,
                                                                           get_direction_for(leader.coordinates,
                                                                            leader.previous_location))
    if leader.coordinates not in leader.tunnel_locations:
        leader.tunnel_locations.append(leader.coordinates)
    
    if sum_of_neighbors_labels == S5_P:
        handling_dead_end(leader)
    else:
        if sum_of_neighbors_labels >= FREE_LOCATION and sum_of_neighbors_labels != FL_S3_BS_P:
            #If there is an a big area than
            move_to(next_direction(leader.coordinates, sum_of_neighbors_labels, neighbor_number_map_direction, leader.uncoated_locations+leader.tunnel_locations), leader)
            leader.state = "cave_scanning"
        elif  sum_of_neighbors_labels == S4_BS_P:
            
            if leader.coordinates in leader.tunnel_locations:
                leader.tunnel_locations.remove(leader.coordinates)
            leader.state = "cave_scanning"
        else:
            
            direction = get_next_direction_in_tunnel(leader, neighbor_number_map_direction, sum_of_neighbors_labels)
            move_to(direction, leader)


def get_next_direction_in_tunnel(leader, neighbor_number_map_direction, sum_of_neighbors_labels):
    for dir in neighbor_number_map_direction:
        if get_coordinates_in_direction(leader.coordinates, dir) \
                not in leader.tunnel_locations + leader.uncoated_locations:
            if neighbor_number_map_direction[dir] == BESIDE_SUBJECT \
                    and (sum_of_neighbors_labels == S3_BS2_P or sum_of_neighbors_labels == S2_BS3_P \
                         or sum_of_neighbors_labels == FL_S3_BS_P):
                direction = dir
            elif neighbor_number_map_direction[dir] == ENTRANCE and (sum_of_neighbors_labels == S4_P_E \
                                                                     or sum_of_neighbors_labels == S3_BS_P_E):
                direction = dir
    return direction


def handle_cave_scanning(leader):
    leader.cave_locations, finished = scanning(leader, leader.uncoated_locations)
    if leader.coordinates in leader.uncoated_locations or leader.coordinates in leader.tunnel_locations or finished:
        go_cave_escaping(leader)


def delete_tunnel_entrances(leader):
    if not ONE_LAYER_COATING:
        if leader.cave_exit_storage and leader.cave_exit_storage in leader.uncoated_locations:
            leader.uncoated_locations.remove(leader.cave_exit_storage)
    leader.tunnel_locations.clear()
    leader.cave_exit_storage.clear()


def get_direction_for(source, destiny):
    if destiny and source:
         new_direction = []
         for i in range(len(source)):
             new_direction.append(destiny[i] - source[i] )
         return tuple(new_direction)
    else:
        return False


def get_coordinates_in_direction(position, direction):
    new_pos = []
    for i in range(len(position)):
        new_pos.append(position[i]+direction[i])
    return tuple(new_pos)


def get_neighbors(directions_list, matter_in, previous_direction):
    sum_of_neighbors_labels = 0
    neighbor_number_map_direction = {}
    for idx in range(len(directions_list)):
        facing_direction = directions_list[idx % len(directions_list)]
        direction_left = directions_list[(idx - 1) % len(directions_list)]
        direction_right = directions_list[(idx + 1) % len(directions_list)]
        type_number = label_neighbor(facing_direction, direction_left, direction_right, matter_in, previous_direction)
        sum_of_neighbors_labels += type_number
        neighbor_number_map_direction[facing_direction] = type_number
    return sum_of_neighbors_labels,  neighbor_number_map_direction



def label_neighbor(facing_direction, direction_left, direction_right, matter_in, previous_direction):
    number = 0
    if matter_in(facing_direction) is False:
        if facing_direction == previous_direction:
            number = PREVIOUS
        elif matter_in(direction_left) is True and matter_in(direction_right) is True:
            number = ENTRANCE

        elif matter_in(direction_left) is True and  matter_in(direction_right) is False\
                or matter_in(direction_right) is True and  matter_in(direction_left) is False:
                number = BESIDE_SUBJECT
        elif matter_in(direction_left) is False and  matter_in(direction_right) is False:
            number = FREE_LOCATION
    else:
        number =  SUBJECT
    return number


def go_cave_escaping(leader):
    leader.aim = leader.cave_exit_storage.pop()
    leader.shortest_path = get_shortest_path(leader.coordinates, leader.aim, leader.world)
    leader.state = "cave_escaping"


def handling_dead_end(leader):
    leader.aim = leader.cave_exit_storage.pop()
    leader.shortest_path = get_shortest_path(leader.coordinates, leader.aim, leader.world)
    leader.dead_end_flag = True
    leader.state = "cave_escaping"


def handle_cave_escaping(leader):
    if reached_aim(leader.aim, leader):
        move_to(get_direction_for(leader.coordinates, leader.aim), leader)
        if leader.state_storage:
            leader.state = leader.state_storage.pop()
        else:
            leader.state = "scanning"
        return


def handle_go_to_object(leader):
    if reached_aim(leader.aim, leader):
        if leader.subject_locations:
            leader.state = "scanning"
        else:
            leader.state = "finished"
    else:
        leader.world.csv_round.update_to_tile()


def handle_taking(leader):
    if reached_aim(leader.aim, leader):
        go_coating(leader)
    else:
        leader.world.csv_round.update_taking()


def go_coating(leader):
    leader.take_particle_on(leader.aim)
    leader.aim = leader.uncoated_locations.pop()
    leader.shortest_path = get_shortest_path(leader.coordinates, leader.aim, leader.world)
    leader.state = "coating"


def handle_coating(leader):
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        if leader.uncoated_locations and leader.subject_locations:
            if ONE_LAYER_COATING and len(leader.uncoated_locations) == 1:
                it_is_leader_turn_to_coat(leader)
            else:
                go_taking_particles(leader)
        elif not leader.uncoated_locations and leader.subject_locations and not ONE_LAYER_COATING:
            go_scanning(leader)
        else:
            leader.aim = None
            it_is_leader_turn_to_coat(leader)


def it_is_leader_turn_to_coat(leader):
    leader.state = "leader_coating"
    if leader.aim is None:
        leader.aim = leader.uncoated_locations.pop()
    leader.shortest_path = get_shortest_path(leader.coordinates, leader.aim, leader.world)


def go_taking_particles(leader):
    leader.scanning = False
    #leader.subject_locations = sorting_list(leader.coordinates, leader.subject_locations, leader.world.grid.get_distance)
    leader.aim = leader.subject_locations.pop(0)
    leader.shortest_path = get_shortest_path(leader.coordinates, leader.aim, leader.world)
    leader.state = "taking"


def go_scanning(leader):
    delete_tunnel_entrances(leader)
    leader.world.csv_round.update_layer()
    leader.state = "scanning"


def handle_leader_coating(leader):
    if leader.coordinates == leader.aim:
        leader.state = "finished"
        leader.world.csv_round.update_leader_coating()
    elif leader.shortest_path:
        next_location = leader.shortest_path.pop(0)
        move_to(get_direction_for(leader.coordinates, next_location), leader)
        # print("Finished")


def handle_finished(leader):
    particle_distance_list = []
    locations_distance_list = []
    coated_subjects = get_coated_subjects_list(leader)
    create_locations(coated_subjects, leader, particle_distance_list)
    for location in leader.world.locations:
        locations_distance_list.append(get_distance_to_closest_tile(location.coordinates,leader.world))
    if particle_distance_list and locations_distance_list:
        check_valid_type(locations_distance_list, particle_distance_list, leader.world)


def create_locations(coated_subjects, leader, particle_distance_list):
    for particle in coated_subjects:
        for direction in leader.world.grid.get_directions_list():
            if not particle.matter_in(direction):
                particle.create_location_in(direction)
        particle_distance_list.append(get_distance_to_closest_tile(particle.coordinates, leader.world))


def get_coated_subjects_list(leader):
    for particle in leader.subject_locations:
        leader.world.particles.remove(leader.world.particle_map_coordinates[particle])
    if leader.world.particles:
        listi = leader.world.particles
    else:
        listi = leader.coated_particles
    return listi


def check_valid_type(locations_distance_list, particle_distance_list, world):
    if max(particle_distance_list) <= min(locations_distance_list):
        leader.world.csv_round.update_valid(1)
        print ("Valid")
        leader.state="End"
        world.set_successful_end()
    else:
        leader.world.csv_round.update_valid(0)
        world.set_unsuccessful_end()


def sorting_list(source_location, destiny_locations_list, get_distance, reverse=False):
    distances = []
    tmp_dict = {}
    sorted_list = []
    for destiny_location in destiny_locations_list:
        calculated_distance = get_distance(source_location, destiny_location)
        distances.append(calculated_distance)
        tmp_dict[destiny_location] = calculated_distance
    distances.sort(reverse=reverse)
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist and coords not in sorted_list:
                sorted_list.append(coords)
    return sorted_list


def next_direction(own_location,  sum_of_neighbors, type_maps_direction, previous_locations):
    direction_list = []
    if sum_of_neighbors >= FREE_LOCATION or sum_of_neighbors == S4_BS_P:
        for direction in type_maps_direction:
            if type_maps_direction[direction] == BESIDE_SUBJECT:
                direction_list.append(direction)
        for direction in direction_list:
            if get_coordinates_in_direction(own_location, direction) not in previous_locations:
                return direction
        return None


def get_leader_distance_to_object(world, objact_list, am_list):
    closest_particle = None
    min = None
    for am_coordinates in am_list:
         for object_coordinates in objact_list:
            value = world.grid.get_distance(am_coordinates, object_coordinates)
            if min is None or (value < min):
                min = value
                if am_coordinates in world.particle_map_coordinates:
                    closest_subject = world.particle_map_coordinates[am_coordinates]
                closest_object_coordinate = object_coordinates
    return closest_subject, min, closest_object_coordinate


def get_shortest_path(lcoordinates, tcoordinates, world):
    coord_lists = [[lcoordinates]]
    visited_coordinates = [lcoordinates]
    counter = 10000
    while len(coord_lists) > 0 and counter >0:
        current_list = coord_lists.pop(0)
        length = len(current_list)
        if are_aim_coordinates_reachable(tcoordinates, current_list[length - 1], world):
            if current_list[0] == lcoordinates:
                current_list.pop(0)
            current_list.append(tcoordinates)
            return current_list
        else:
            around_last = get_all_surounding_coordinates(current_list[length - 1], world)
            for tmp in around_last:
                if is_coord_unvisited_and_free(tmp, visited_coordinates, world):
                    new_list = deepcopy(current_list)
                    new_list.append(tmp)
                    coord_lists.append(new_list)
                    visited_coordinates.append(tmp)
        counter -=1
    if counter <= 0:
        leader.world.csv_round.update_valid(0)
        print("Time Out Breadth Search ", " from ", lcoordinates, " to ", tcoordinates)
        world.set_unsuccessful_end()


def are_aim_coordinates_reachable(acoordinates, bcoordinates, world):
    if acoordinates == bcoordinates:
        return True
    around = get_all_surounding_coordinates(acoordinates, world)
    for tmp in around:
        if tmp == bcoordinates:
            return True
    return False


def is_coord_unvisited_and_free(coord, visited_coordinates, world):
    if coord in visited_coordinates:
        return False
    if coord in world.get_particle_map_coordinates():
        return False
    if coord in world.get_tile_map_coordinates():
        return False
    return True


def get_all_surounding_coordinates(pcoordinates, world):
    surrounding_coordinates = []
    for direction in world.grid.get_directions_list():
        surrounding_coordinates.append(world.grid.get_coordinates_in_direction(pcoordinates, direction))
    return surrounding_coordinates


def get_distance_to_closest_tile(source, world):
    distance = None
    for tile in world.get_tiles_list():
        value = world.grid.get_distance(source, tile.coordinates)
        if distance is None or (value < distance):
            distance = value
    return distance


def reached_aim(aim, leader):
    if leader.shortest_path:
        next_location = leader.shortest_path.pop(0)
        if next_location != aim :
            move_to(get_direction_for(leader.coordinates, next_location), leader)
            return False
    return True