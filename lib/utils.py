class Utils:

    # Refer to phototaxing_2_particles_algorithm.py for documentation
    def determine_direction_from_coords(coords_a, coords_b):
        delta_x = coords_a[0] - coords_b[0]
        delta_y = coords_a[1] - coords_b[1]

        if delta_x == 0 and delta_y == 0:
            return -1
        elif delta_x == -0.5 and delta_y == -1:
            return 0
        elif delta_x == -1 and delta_y == 0:
            return 1
        elif delta_x == -0.5 and delta_y == 1:
            return 2
        elif delta_x == 0.5 and delta_y == 1:
            return 3
        elif delta_x == 1 and delta_y == 0:
            return 4
        elif delta_x == 0.5 and delta_y == -1:
            return 5
        else:
            return -1

    # Refer to phototaxing_2_particles_algorithm.py for documentation
    @staticmethod
    def determine_coords_from_direction(coords, dirval):
        coords_new = (coords[0], coords[1])
        x = coords[0]
        y = coords[1]

        if dirval == 0:
            coords_new = (x + 0.5, y + 1)
        elif dirval == 1:
            coords_new = (x+1, y)
        elif dirval == 2:
            coords_new = (x + 0.5, y - 1)
        elif dirval == 3:
            coords_new = (x - 0.5, y - 1)
        elif dirval == 4:
            coords_new = (x - 1, y)
        elif dirval == 5:
            coords_new = (x - 0.5, y + 1)
        return coords_new

    def compare_coords(self, coords_a, coords_b):
        if len(coords_a) == 2 and len(coords_b) == 2:
            if coords_a[0] == coords_b[0] and coords_a[1] == coords_b[1]:
                return True

        return False

    def inv_dir(self, dir):
        return (dir+3) % 6
