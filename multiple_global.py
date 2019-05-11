import subprocess
import os
import configparser
from lib import config_data as cd
import importlib


def main():
    seed_start = 1
    seed_end = 20

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    config_data = cd.ConfigData(config)

    scenario = config.get ("File", "scenario")
    solution = config.get("File", "solution")
    max_round = config_data.max_round
    search = None
    scenario_mod = importlib.import_module('scenario.' + config_data.scenario)
    particles_num = config_data.particles_num
    search_algorithms = 2
    start_positions = scenario_mod.get_starting_positions()

    child_processes = []

    for particle in range(1, particles_num + 1):
        for search_algorithm in range(0, search_algorithms + 1):
            config_data.search_algorithm = search_algorithm

            if particle == 1 and search_algorithm == 2:
                continue

            for start_position in start_positions:
                round = 1

                if config_data.search_algorithm == 0:
                    search = "BFS"
                elif config_data.search_algorithm == 1:
                    search = "DFS"
                elif config_data.search_algorithm == 2:
                    search = "MIXED"

                dir_name = "./outputs/multiple/" + \
                           scenario + \
                           "_" + str(particle) + "Part" + \
                           "_" + solution + \
                           "_" + str(search) + \
                           "_" + start_position

                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)

                out = open(dir_name + "/multiprocess.txt", "w")

                for seed in range(seed_start, seed_end + 1):
                    process = "python3.6", \
                              "run.py", \
                              "-w" + scenario, \
                              "-s" + solution, \
                              "-n" + str(max_round), \
                              "-m 1", \
                              "-r" + str(seed), \
                              "-v" + str(0), \
                              "-b" + str(start_position), \
                              "-p" + str(particle), \
                              "-a" + str(search_algorithm)

                    p = subprocess.Popen(process, stdout=out, stderr=out)
                    print("Round Nr. ", round, "finished")
                    child_processes.append(p)
                    round += 1
                    p.wait()

                fout = open(dir_name+"/all_aggregates.csv","w+")

                # first file:
                for line in open(dir_name+"/"+str(1)+"/aggregate_rounds.csv"):
                    fout.write(line)

                # now the rest:
                for seed in range(seed_start+1, seed_end+1):
                    f = open(dir_name+"/"+str(seed)+"/aggregate_rounds.csv")
                    f.__next__()  # skip the header

                    for line in f:
                        fout.write(line)

                    f.close()  # not really needed
                fout.close()


if __name__ == "__main__":
    main()
