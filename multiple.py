import subprocess
from datetime import datetime
import os
import configparser
from lib import config_data as cd


def main():
    seed_start = 1
    seed_end = 20

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    config_data = cd.ConfigData(config)

    scenario = config.get ("File", "scenario")
    solution = config.get("File", "solution")
    local_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]
    max_round = config_data.max_round
    search_algorithm = None
    start_position = config_data.start_position
    particles_num = config_data.particles_num

    if config_data.search_algorithm == 0:
        search_algorithm = "BFS"
    elif config_data.search_algorithm == 1:
        search_algorithm = "DFS"
    elif config_data.search_algorithm == 2:
        search_algorithm = "MIXED"

    dir_name = "./outputs/multiple/" + \
               str(local_time) + \
               "_" + scenario + \
               "_" + str(particles_num) + "Part" + \
               "_" + solution + \
               "_" + str(search_algorithm) + \
               "_" + start_position

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    out = open(dir_name+"/multiprocess.txt", "w")
    child_processes = []

    round = 1

    for seed in range(seed_start, seed_end + 1):
        process = "python3.6", \
                  "run.py", \
                  "-w" + scenario, \
                  "-s" + solution, \
                  "-n" + str(max_round), \
                  "-m 1", \
                  "-d" + str(local_time), \
                  "-r" + str(seed), \
                  "-v" + str(0)

        p = subprocess.call(process, stdout=out, stderr=out)
        print("Round Nr. ", round, "finished")
        child_processes.append(p)
        round += 1

    fout = open(dir_name+"/all_aggregates.csv", "w+")

    # first file:
    for line in open(dir_name+"/"+str(1)+"/aggregate_rounds.csv"):
        fout.write(line)

    # now the rest:
    for seed in range(seed_start + 1, seed_end + 1):
        f = open(dir_name+"/"+str(seed)+"/aggregate_rounds.csv")
        f.__next__()  # skip the header

        for line in f:
            fout.write(line)

        f.close()  # not really needed
    fout.close()


if __name__ == "__main__":
    main()
