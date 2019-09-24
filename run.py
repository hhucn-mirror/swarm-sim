"""This is the main module of the Opportunistic Robotics Network Simulator"""


import configparser
import getopt
import logging
import os
import sys
import matplotlib.pyplot as plt
from lib.oppnet.messagestore import BufferStrategy
from datetime import datetime
from lib.oppnet.mobility_model import Mode
from lib.oppnet.routing import Algorithm



from lib import  sim

class ConfigData():

    def __init__(self, config):
        self.seedvalue = config.getint("Simulator", "seedvalue")
        self.max_round = config.getint("Simulator", "max_round")
        self.random_order = config.getboolean("Simulator", "random_order")
        self.visualization = config.getint("Simulator", "visualization")
        try:
            self.scenario = config.get("File", "scenario")
        except (configparser.NoOptionError) as noe:
            self.scenario = "init_scenario.py"

        try:
            self.solution = config.get("File", "solution")
        except (configparser.NoOptionError) as noe:
            self.solution = "solution.py"
        try:
            self.csv_generator_path = config.get("File", "csv_generator")
        except configparser.NoOptionError as noe:
            self.csv_generator_path = "lib.csv_generator.py"

        try:
            self.particle_path = config.get("File", "particle")
        except configparser.NoOptionError as noe:
            self.particle_path = "lib.particle.py"

        self.size_x = config.getfloat("Simulator", "size_x")
        self.size_y = config.getfloat("Simulator", "size_y")
        self.window_size_x = config.getint("Simulator", "window_size_x")
        self.window_size_y = config.getint("Simulator", "window_size_y")
        self.border = config.getfloat("Simulator", "border")
        self.max_particles = config.getint("Simulator", "max_particles")
        self.mm_limitation = config.getboolean("Matter", "mm_limitation")
        self.particle_mm_size = config.getint("Matter", "particle_mm_size")
        self.tile_mm_size = config.getint("Matter", "tile_mm_size")
#        self.marker_mm_size = config.getint("Matter", "marker_mm_size")

        self.scan_radius = config.getint("Routing", "scan_radius")

        self.dir_name = None #TODO
        self.mm_limit = config.getint("Matter", "mm_limitation") #TODO
        self.mm_size = config.getint("Matter", "particle_mm_size") #TODO
        self.seed = config.getint("Simulator", "seedvalue") #TODO

        self.ms_size = config.getint("Routing", "ms_size")
        self.ms_strategy = BufferStrategy(config.getint("Routing", "ms_strategy"))
        self.delivery_delay = config.getint("Routing", "delivery_delay")
        self.routing_algorithm = Algorithm(config.getint("Routing", "algorithm"))
        self.mobility_model_mode = Mode(config.getint("MobilityModel", "mode"))
        self.message_ttl = config.getint("Routing", "message_ttl")

def swarm_sim( argv ):
    """In the main function first the config is getting parsed and than
    the simulator and the sim object is created. Afterwards the run method of the simulator
    is called in which the simlator is going to start to run"""
    config = configparser.ConfigParser(allow_no_value=True)

    config.read("config.ini")
    config_data=ConfigData(config)

    multiple_sim=0
    local_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[:-1]
    try:
        opts, args = getopt.getopt(argv, "hs:w:r:n:m:d:v:", ["solution=", "scenario="])
    except getopt.GetoptError:
        print('Error: run.py -r <seed> -w <scenario> -s <solution> -n <maxRounds>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -r <seed> -w <scenario> -s <solution> -n <maxRounds>')
            sys.exit()
        elif opt in ("-s", "--solution"):
            config_data.solution = arg
        elif opt in ("-w", "--scenario"):
            config_data.scenario = arg
        elif opt in ("-r", "--seed"):
            config_data.seedvalue = int(arg)
        elif opt in ("-n", "--maxrounds"):
           config_data.max_round = int(arg)
        elif opt in ("-m"):
           multiple_sim = int(arg)
        elif opt in ("-v"):
            config_data.visualization = int(arg)
        elif opt in ("-d"):
            local_time = str(arg)

    logging.basicConfig(filename='system.log', filemode='w', level=logging.INFO, format='%(message)s')

    if multiple_sim == 1:
        config_data.dir_name= local_time + "_" + config_data.scenario.rsplit('.', 1)[0] + \
               "_" + config_data.solution.rsplit('.', 1)[0] + "/" + \
               str(config_data.seedvalue)

        config_data.dir_name = "./outputs/mulitple/"+ config_data.dir_name

    else:
        config_data.dir_name= local_time + "_" + config_data.scenario.rsplit('.', 1)[0] + \
               "_" + config_data.solution.rsplit('.', 1)[0] + "_" + \
               str(config_data.seedvalue)
        config_data.dir_name = "./outputs/" + config_data.dir_name
    if not os.path.exists(config_data.dir_name):
        os.makedirs(config_data.dir_name)

    logging.info('Started')
    simulator = sim.Sim( config_data )
    simulator.run()
    #plt.plot([1, 2, 3, 4])
    #plt.ylabel('some numbers')
    plt.show()
    logging.info('Finished')


if __name__ == "__main__":
    swarm_sim(sys.argv[1:])
