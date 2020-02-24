def solution(world):
    if len(world.particles) == 1:
        leader = world.particles[0]
        leader.prev_aim = (-0.5, 1.0, 0.0)
        if len(world.locations) > 0:
            for location in world.locations[:]:
                world.remove_location(location.get_id())
                world.vis.remove_location(location)
        leader.directions_list = world.grid.get_directions_list()
        check_for_cave(leader)


def check_for_cave(leader):
    location_cnt = 0
    cnt_cnter = 0
    dir_especial = []
    neighbors = {}
    dir_entry = None
    dir_exit = None
    for idx in range(len(leader.directions_list)):
        cnt = 0
        dire = leader.directions_list[(idx) % len(leader.directions_list)]
        dire_left = leader.directions_list[(idx - 1) % len(leader.directions_list)]
        dire_right = leader.directions_list[(idx + 1) % len(leader.directions_list)]
        if leader.matter_in(dire_left) is True:
            cnt += 1
        if leader.matter_in(dire_right) is True:
            cnt += 1
        if leader.matter_in(dire) is False:
            cnt_cnter += cnt
            if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
                cnt = 10
            elif leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_left) \
                    and leader.matter_in(dire_left) is False:
                cnt = 5
            elif leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_right) \
                    and leader.matter_in(dire_right) is False:
                cnt = 5
            neighbors[dire] = cnt
            location_cnt += 1
            if cnt == 2:
                dir_especial.append(dire)

    if dir_especial and location_cnt > 2:
        for dire in dir_especial:
            if leader.prev_aim != leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire) :
                dir_entry = dire
            for dire in neighbors :
                if neighbors[dire] == 1 and location_cnt == 4:
                    dir_exit = dire
                elif neighbors[dire] == 5 and location_cnt == 3:
                    dir_exit = dire

    elif location_cnt == cnt_cnter and location_cnt == 4:
        for dire in neighbors:
            if neighbors[dire] == 10:
                continue
            elif neighbors[dire] == 5:
                dir_exit = dire
            else:
                if leader.matter_in(dire) is False:
                    dir_entry = dire
    elif location_cnt == 2 and cnt_cnter == 4:
            dir_entry = dir_especial[0]
            dir_exit = dir_especial[1]
    if dir_entry is not None and  dir_exit is not None:
        leader.create_location_in(dir_entry).set_color((0,1,1,1))
        leader.create_location_in(dir_exit).set_color((1, 0, 1, 1))
    return dir_entry, dir_exit
