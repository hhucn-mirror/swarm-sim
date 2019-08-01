import subprocess
import os
import configparser
from datetime import datetime
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

    local_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]

    search_algorithms = 1
    sq_size_start = 2
    sq_size_end = 10

    child_processes = []
    round = 0
    for search_algorithm in range(0, search_algorithms + 1):
        config_data.search_algorithm = search_algorithm
        if config_data.search_algorithm == 0:
            search = "BFS"
        elif config_data.search_algorithm == 1:
            search = "DFS"
        elif config_data.search_algorithm == 2:
            search = "MIXED"
        dir_name = "./outputs/multiple/" + \
                   str(local_time) + \
                   "_" + scenario + \
                   "_" + solution + \
                   "_" + str(search)

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        out = open(dir_name + "/multiprocess.txt", "w")

        for i in range(sq_size_start, sq_size_end + 1):



            process = "python3.6", \
                      "run.py", \
                      "-w" + scenario, \
                      "-s" + solution, \
                      "-n" + str(max_round), \
                      "-m 1", \
                      "-d" + str(local_time), \
                      "-q" + str(i), \
                      "-v" + str(0), \
                      "-a" + str(search_algorithm)

            p = subprocess.Popen(process, stdout=out, stderr=out)
            child_processes.append(p)
            round += 1
            print("Round Nr. ", round, "started")
            if len(child_processes) == os.cpu_count():
                for cp in child_processes:
                    cp.wait()
                child_processes.clear()

        for cp in child_processes:
            cp.wait()

        fout = open(dir_name + "/all_aggregates.csv", "w+")

        for line in open(dir_name+"/"+str(sq_size_start)+"/aggregate_rounds.csv"):
            fout.write(line)

        # now the rest:
        for sq in range(sq_size_start+1, sq_size_end+1):
            f = open(dir_name+"/"+str(sq)+"/aggregate_rounds.csv")
            f.__next__()  # skip the header

            for line in f:
                fout.write(line)

            f.close()  # not really needed
        fout.close()


if __name__ == "__main__":
    main()
