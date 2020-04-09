
ENTRANCE_LABEL = 100
PREVIOUS_LOCATION_LABEL = 11
BESIDE_PREVIOUS_LOCATION_LABEL = 19
FREE_LOCATION_LABEL = 103
FREE_L = 17
FOUR_MATTERS = 4
FIVE_MATTERS = 5
TWO_MATTERS = 2
THREE_MATTERS = 3
PL_BP_EL_FL = PREVIOUS_LOCATION_LABEL + BESIDE_PREVIOUS_LOCATION_LABEL \
                    + ENTRANCE_LABEL + FREE_LOCATION_LABEL
PL_BP_FL_FL = PREVIOUS_LOCATION_LABEL + BESIDE_PREVIOUS_LOCATION_LABEL + 2 * FREE_LOCATION_LABEL
PL_BP_EL = BESIDE_PREVIOUS_LOCATION_LABEL + ENTRANCE_LABEL \
                                                    + PREVIOUS_LOCATION_LABEL
PL_FL_FL = PREVIOUS_LOCATION_LABEL + 2* FREE_LOCATION_LABEL

PL_BP= PREVIOUS_LOCATION_LABEL + BESIDE_PREVIOUS_LOCATION_LABEL

PL_BP_FL = BESIDE_PREVIOUS_LOCATION_LABEL + PREVIOUS_LOCATION_LABEL \
                                                    + FREE_LOCATION_LABEL


def get_directions_list():
    """
    returns a list of the direction vectors
    :return: list of 3d tuples - '(float, float, float)'
    """

    directions= [(0.5, 1, 0),
            (1, 0, 0),
             (0.5, -1, 0),
             (-0.5, -1, 0),
             (-1, 0, 0),
             (-0.5, 1, 0)]
    return directions

def matter_in(direction):
    matter_dict = {(0.5, 1, 0): True, (1, 0, 0): True, (0.5, -1, 0): False, (-0.5, -1, 0): False, (-1, 0, 0): False,
                   (-0.5, 1, 0): True}
    return matter_dict[direction]


def matter_in(direction):
    matter_dict = {(0.5, 1, 0): False, (1, 0, 0): False, (0.5, -1, 0): False, (-0.5, -1, 0): True, (-1, 0, 0): False,
                   (-0.5, 1, 0): True}
    return matter_dict[direction]

def get_coordinates_in_direction(position, direction):
    """
    calculates a new position from current position and direction
    :param position: coordinates, (float, float, float) tuple, current position
    :param direction: coordinates, (float, float, float) tuple, direction
    :return: coordinates, (float, float, float) tuple, new position
    """
    new_pos = []
    for i in range(len(position)):
        new_pos.append(position[i]+direction[i])
    return tuple(new_pos)

def get_distance(start,end):
    if start[1] == end[1] and start[0] != end[0]:
        return abs(end[0] - start[0])
    elif abs(end[0] - start[0]) - (abs(end[1] - start[1]) * 0.5) > 0:
        return abs(end[1] - start[1]) + abs(end[0] - start[0]) - ( abs(end[1] - start[1]) * 0.5 )
    return abs(end[1] - start[1]
               )
def test_get_sorted_list():
    #assert leader_coated.get_sorted_list((0,0,0), [(5,0,0), (3,0,0), (4,0,0), (1,0,0), (2,0,0)], get_distance) == [(1,0,0), (2,0,0), (3,0,0), (4,0,0), (5,0,0)]
    #assert leader_coated.get_sorted_list((0, 0, 0), [(5, 0, 0), (3, 0, 0), (4, 0, 0), (1, 0, 0), (2, 0, 0)], get_distance, True) ==  [(5,0,0), (4,0,0), (3,0,0), (2,0,0), (1,0,0)]
    #facing_direction=(1, 0, 0)
    #assert leader_coated.get_location_label(facing_direction, (0.5,   1, 0), (0.5,  -1, 0), matter_in, get_coordinates_in_direction) == ENTRANCE_LABEL
    #assert leader_coated.get_location_label((-1,  0, 0),  (-0.5, -1, 0),  (-0.5,  1, 0), matter_in, get_coordinates_in_direction, (0,0,0), (-1,0,0)) == PREVIOUS_LOCATION_LABEL
    assert leader_coated.scan_neighbors(get_directions_list(), matter_in) == THREE_MATTERS