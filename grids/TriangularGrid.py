import math

from grids.Grid import Grid


class TriangularGrid(Grid):

    def __init__(self, size):
        super().__init__()
        self._size = size

    @property
    def size(self):
        return self._size

    @property
    def directions(self):
        return {"NE":  (0.5,   1, 0),
                "E":   (1,     0, 0),
                "SE":  (0.5,  -1, 0),
                "SW":  (-0.5, -1, 0),
                "W":   (-1,    0, 0),
                "NW":  (-0.5,  1, 0)}

    def get_box(self, width):
        locs = []
        for y in range(-width, width+1):
            for x in range(-width, width+1):
                if y % 2 == 0:
                    locs.append((x, y, 0.0))
                else:
                    locs.append((x+0.5, y, 0.0))

        return locs

    def are_valid_coordinates(self, coordinates):
        if not coordinates[2] == 0.0:
            return False
        if coordinates[1] % 2.0 == 0.0:
            if coordinates[0] % 1.0 == 0.0:
                return True
        else:
            if coordinates[0] % 1.0 == 0.5:
                return True
        return False

    def get_nearest_valid_coordinates(self, coordinates):
        nearest_y = round(coordinates[1])
        if nearest_y % 2 == 0:
            nearest_x = round(coordinates[0])
        else:
            if coordinates[0] < 0:
                nearest_x = int(coordinates[0]) - 0.5
            else:
                nearest_x = int(coordinates[0]) + 0.5

        return nearest_x, nearest_y, 0

    def get_directions_dictionary(self):
        return self.directions

    def get_dimension_count(self):
        return 2


    def get_center(self):
        return 0, 0, 0

    def get_scaling(self):
        return 1.0, math.sqrt(3/4), 1.0


    def get_next_dir_to(self, src_x, src_y, dest_x, dest_y):
        """
        :param src_x: x coordinate of the source
        :param src_y: y coordinate of the source
        :param dest_x: x coordinate of the destiny
        :param dest_y: y coordinate of the destiny
        :return: the next direction that brings the matter closer to the destiny
        """
        next_dir = ()
        if (src_x < dest_x or src_x == dest_x) and src_y < dest_y:
            next_dir = (0.5,   1, 0)
        elif src_y < dest_y and src_x > dest_x:
            next_dir = (-0.5,  1, 0)
        elif src_y > dest_y and src_x < dest_x:
            next_dir = (0.5,  -1, 0)
        elif (src_x > dest_x or src_x == dest_x) and src_y > dest_y :
            next_dir = (-0.5, -1, 0)
        elif src_y == dest_y and src_x > dest_x:
            next_dir = (-1,    0, 0)
        elif src_y == dest_y and src_x < dest_x:
            next_dir = (1,     0, 0)
        return next_dir


    def get_distance(self,start,end):
        if start[1] == end[1] and start[0] != end[0]:
            return abs(end[0] - start[0])
        elif (abs(end[0] - start[0]) - abs(end[1] - start[1])) * 0.5 > 0:
            return abs(end[1] - start[1]) + (abs(end[0] - start[0]) - abs(end[1] - start[1])) * 0.5
        return abs(end[1] - start[1])

    def get_nearest_direction(self, start, end):
        best = None
        best_direction  = None
        for d in self.get_directions_list():
            next_coords =self.get_coordinates_in_direction(start, d)
            tmp_best = self.get_distance(next_coords, end)
            if best is None:
                best = tmp_best
                best_direction = d
            else:
                if tmp_best < best:
                    best = tmp_best
                    best_direction = d
        return best_direction
