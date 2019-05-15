"""This is the main module of the Opportunistic Robotics Network Simulator"""

import configparser
import argparse
import logging
import os
from datetime import datetime
from lib import sim, config_data as cd


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--solution", dest="solution", help="Solution Name")
    parser.add_argument("-w", "--scenario", dest="scenario", help="Scenario Name")
    parser.add_argument("-r", "--seed", dest="seed", help="Seed Value")
    parser.add_argument("-n", "--maxround", dest="maxround", help="Maximum Number of Rounds")
    parser.add_argument("-m", "--multiple", dest="multiple", help="Multiple Runs: 0=off, 1=on")
    parser.add_argument("-v", "--visualization", dest="visualization", help="Visualization: 0=off, 1=on")
    parser.add_argument("-d", "--time", dest="time", help="Time")
    parser.add_argument("-b", "--startpos", dest="startpos", help="Starting Position")
    parser.add_argument("-p", "--particles", dest="particles", help="Number of Particles: 1 -> 6")
    parser.add_argument("-a", "--searchalgorithm", dest="searchalgorithm",
                        help="Searching Algorithm: 0=BFS, 1=DFS, 2=MIXED")
    options = parser.parse_args()
    return options


def swarm_sim(options):
    """In the main function first the config is getting parsed and than
    the simulator and the sim object is created. Afterwards the run method of the simulator
    is called in which the simulator is going to start to run

    Example: python3.6 run.py -w square -s global -n 1000 -m 0 -r 13 -v 1 -b Top -p 2 -a 1

    """

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    config_data = cd.ConfigData(config)

    search_algorithm = None
    multiple_sim = 0
    local_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]

    if options.solution:
        config_data.solution = options.solution
    if options.scenario:
        config_data.scenario = options.scenario
    if options.seed:
        config_data.seedvalue = int(options.seed)
    if options.maxround:
        config_data.max_round = int(options.maxround)
    if options.multiple:
        multiple_sim = int(options.multiple)
    if options.visualization:
        config_data.visualization = int(options.visualization)
    if options.time:
        local_time = options.time
    if options.searchalgorithm:
        config_data.search_algorithm = int(options.searchalgorithm)
    if options.startpos:
        config_data.start_position = str(options.startpos)
    if options.particles:
        config_data.particles_num = int(options.particles)

    logging.basicConfig(filename='system.log', filemode='w', level=logging.INFO, format='%(message)s')

    if config_data.search_algorithm == 0:
        search_algorithm = "BFS"
    elif config_data.search_algorithm == 1:
        search_algorithm = "DFS"
    elif config_data.search_algorithm == 2:
        search_algorithm = "MIXED"

    if multiple_sim == 1:
        config_data.dir_name = config_data.scenario.rsplit('.', 1)[0] + \
                               "_" + str(config_data.particles_num) + "Part" + \
                               "_" + config_data.solution.rsplit('.', 1)[0] + \
                               "_" + search_algorithm + \
                               "_" + config_data.start_position + \
                               "/" + str(config_data.seedvalue)

        config_data.dir_name = "./outputs/multiple/" + config_data.dir_name

    else:
        config_data.dir_name = local_time + "_" + \
                               config_data.scenario.rsplit('.', 1)[0] + \
                               "_" + str(config_data.particles_num) + "Part" + \
                               "_" + config_data.solution.rsplit('.', 1)[0] + \
                               "_" + search_algorithm + \
                               "_" + config_data.start_position + \
                               "_" + str(config_data.seedvalue)

        config_data.dir_name = "./outputs/" + config_data.dir_name

    if not os.path.exists(config_data.dir_name):
        os.makedirs(config_data.dir_name)

    logging.info('Started')
    simulator = sim.Sim(config_data)
    simulator.run(config_data)
    logging.info('Finished')


if __name__ == "__main__":
    options = get_options()
    swarm_sim(options)


