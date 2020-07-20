import csv
import math

from lib.oppnet.util import get_max_flock_radius, flock_spread, \
    flock_uniformity, get_distance_from_coordinates, all_pairs_flock_distance_metrics


class CsvFlockRoundData:
    """
    Collects metrics about a flock for each round.
    Contains :class:`~csv_generator.FlockData` objects.
    """

    def __init__(self, grid, directory="outputs/", solution=""):
        """
        :param grid: the simulation grid object
        :param solution: The simulator solution used
        :type: solution: str
        :param directory: The directory for the csv to be put in.
        :type directory: str
        """
        self.solution = solution
        self.flock_data = []
        self.directory = directory
        self.grid = grid
        self._predators = set()
        self._predator_coordinates = []

    def add_flock(self, flock):
        self.flock_data.append(FlockRoundData(flock))

    def add_predator(self, predator):
        self._predators.add(predator)

    def __del__(self):
        """
        Destructor that writes the csv rows.
        """
        self.write_rows()

    def write_rows(self):
        """
        Writes rows for all flocks.
        """
        for flock_number, flock_round_data in enumerate(self.flock_data):
            file_name = self.directory + '/flock_{}.csv'.format(flock_number)
            data_rows = self.get_data_rows(flock_round_data)
            self.write_csv_file(file_name, data_rows)

    def write_csv_file(self, file_name, data_rows):
        with open(file_name, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(self.get_header_row())
            csv_writer.writerows(data_rows)

    def get_data_rows(self, flock_round_data):
        data_rows = []
        for sim_round in range(0, flock_round_data.get_recorded_rounds()):
            data_rows.append(self.get_data_row(sim_round, flock_round_data.get_round_directions(sim_round),
                                               flock_round_data.get_round_coordinates(sim_round)))
        return data_rows

    def get_data_row(self, sim_round, particle_directions, particle_coordinates):
        particles_count = len(particle_directions)
        flock_radius, _ = get_max_flock_radius(particles_count)

        sum_all_pairs, min_all_pairs, max_all_pairs, median_all_pairs = \
            all_pairs_flock_distance_metrics(particle_coordinates)
        spread_euclidean, spread_hops, center_coordinates = flock_spread(particle_coordinates, self.grid)

        min_predator_distance = self._get_min_predator_distance(sim_round, particle_coordinates)

        return [sim_round + 1, particles_count, flock_radius,
                sum_all_pairs, min_all_pairs, max_all_pairs, median_all_pairs,
                flock_uniformity(particle_directions), spread_euclidean, spread_hops, center_coordinates,
                min_predator_distance]

    def update_metrics(self):
        for flock_round_data in self.flock_data:
            flock_round_data.update()
        self._predator_coordinates.append([predator.coordinates for predator in self._predators])

    def _get_min_predator_distance(self, sim_round, particle_coordinates):
        predator_coordinates = self._predator_coordinates[sim_round]
        min_distance = math.inf
        for p_1 in predator_coordinates:
            for p_2 in particle_coordinates:
                distance = get_distance_from_coordinates(p_1, p_2)
                if distance < min_distance:
                    min_distance = distance
        return min_distance

    @staticmethod
    def get_header_row():
        return ['Round', 'Flock Size', 'Flock Radius', 'Actual All-Pairs Distance', 'Minimum Pairs Distance',
                'Maximum Pairs Distance', 'Median Pairs Distance',
                'Uniformity', 'Euclidean Spread', 'Hop Spread', 'Flock Center',
                'Minimum Distance flock member to predators']


class FlockRoundData:
    def __init__(self, particles):
        self._particles = particles
        self.particles_round_coordinates = []
        self.particles_directions = []

    def update(self):
        self.particles_round_coordinates.append([particle.coordinates for particle in self._particles])
        self.particles_directions.append([particle.mobility_model.current_dir for particle in self._particles])

    def get_round_coordinates(self, sim_round):
        return self.particles_round_coordinates[sim_round]

    def get_round_directions(self, sim_round):
        return self.particles_directions[sim_round]

    def get_recorded_rounds(self):
        return len(self.particles_directions)
