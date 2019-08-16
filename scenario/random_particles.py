import csv
import random

from lib.colors import Colors


def scenario(sim):

    x_min, x_max = -sim.get_sim_x_size(), sim.get_sim_x_size()
    y_min, y_max = -sim.get_sim_y_size(), sim.get_sim_y_size()

    particle_count = 200

    csv_file = open(sim.directory + '/particle_coords.csv', 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(["x", "y"])

    scenario_file = open(sim.directory + '/random_{}.py'.format(particle_count), 'w', newline='\n')
    scenario_file.writelines(['def scenario(sim):\n'])

    coords = []
    for _ in range(particle_count):
        x, y = random.randint(x_min, x_max), random.randrange(y_min, y_max, 2)
        while [x, y] in coords:
            x, y = random.randint(x_min, x_max), random.randrange(y_min, y_max, 2)
        sim.add_particle(x, y, Colors.black.value)

        coords.append([x, y])

        writer.writerow([x, y])
        scenario_file.writelines(['\tsim.add_particle({}, {}, Colors.black.value)\n'.format(x, y)])

    csv_file.close()
    scenario_file.close()


