
square = [(0,0), (0,2), (2,2),(2,0)]

def scenario(sim, config_data):
    starting_point=(0,0)
    square_size = 10
    end_point_on_x = () #stores the last point on the first x line
    end_point_on_y = () #stores the last point on the first y line

    #creates locations on the x coordinate from the starting_point
    for i in range (0, 2*square_size+1):
        end_point_on_x = (starting_point[0] + i, starting_point[1])
        sim.add_location(end_point_on_x[0], end_point_on_x[1])

    #creates locations on the y coordinate from the starting_point
    for i in range (1, square_size*2 +1):
        end_point_on_y = (starting_point[0], (starting_point[1] + i))
        if i % 2 == 1:
            sim.add_location(end_point_on_y[0] - 0.5, end_point_on_y[1] )
            continue
        sim.add_location(end_point_on_y[0], end_point_on_y[1])

    #creates locations on the y coordinate from the ending point of the x coordinate
    for i in range (1, 2* square_size+1):
        if i % 2 == 1:
            sim.add_location(end_point_on_x[0] + 0.5, end_point_on_x[1] + i)
            continue
        sim.add_location(end_point_on_x[0], end_point_on_x [1]+i )

    #creates locations on the x coordinate from the ending point of the y coordinate
    for i in range (1, 2*square_size+1):
        sim.add_location(end_point_on_y[0] + i, end_point_on_y[1] )


