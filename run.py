"""This is the main module of the Opportunistic Robotics Network Simulator"""


import configparser
import getopt
import logging
import os
import sys
from datetime import datetime

from lib import sim, config_data as cd


def swarm_sim( argv ):
    """In the main function first the config is getting parsed and than
    the simulator and the sim object is created. Afterwards the run method of the simulator
    is called in which the simlator is going to start to run"""
    config = configparser.ConfigParser(allow_no_value=True)

    config.read("config.ini")
    config_data = cd.ConfigData(config)

    multiple_sim=0
    local_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]
    try:
        opts, args = getopt.getopt(argv, "hs:w:r:n:m:d:v:", ["solution=", "scenario="])
    except getopt.GetoptError:
        print('Error: run.py -r <randomeSeed> -w <scenario> -s <solution> -n <maxRounds>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run.py -r <randomeSeed> -w <scenario> -s <solution> -n <maxRounds>')
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


    #logging.basicConfig(filename='myapp.log', filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')
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
    logging.info('Finished')


if __name__ == "__main__":
    swarm_sim(sys.argv[1:])

