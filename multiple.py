import sys, getopt, subprocess
from datetime import datetime
from multiprocessing import Pool
import os
import configparser
from lib.gnuplot_generator import plot_generator


def main(argv):

    seed_start = 1
    seed_end = 2
    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    #os.rmdir("scenario/__pycache__")
    file_list = os.listdir("scenario")
    scenarios = []
    if "particleGroups.py" in file_list:
        file_list.remove("particleGroups.py")
    if "__pycache__" in file_list:
        file_list.remove("__pycache__")
    for file in file_list:
        scenarios.append(file.split('.', 1)[0])
    scenarios.sort()
    try:
        scenario_file = config.get ("File", "scenario")
    except (configparser.NoOptionError) as noe:
        scenario_file = "init_scenario.py"

    try:
        solution_file = config.get("File", "solution")
    except (configparser.NoOptionError) as noe:
        solution_file = "solution.py"

    n_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]
    try:
        opts, args = getopt.getopt(argv, "hs:w:r:n:v:", ["scenaro=", "solution="])
    except getopt.GetoptError:
        print('Error: multiple.py -r <randomeSeed> -w <scenario> -s <solution> -n <maxRounds>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('multiple.py -ss <seed_start> -se <seed_end> -w <scenario> -s <solution>  -n <maxRounds>')
            sys.exit()
        elif opt in ("-s", "--solution"):
            solution_file = arg
        elif opt in ("-w", "--scenario"):
            scenario_file = arg
        elif opt in ("-ss", "--seed_start"):
            seed_start = int(arg)
        elif opt in ("-se", "--seed_end"):
            seed_end = int(arg)
        elif opt in ("-n", "--maxrounds"):
            max_round = int(arg)
    folder = "./outputs/multiple/" + str(n_time) + "_" + solution_file.rsplit('.', 1)[0]
    if not os.path.exists(folder):
        os.makedirs(folder)
    out = open("./"+folder + "/multiprocess.txt", "w")
    child_processes = []
    process_cnt=0
    #scenarios = ["tube_10", "tube_20"]
    min_radius = 0
    max_radius = 19
    #
    for scenario in scenarios:
        folder_name = folder  + "/" + scenario
        for radius in range(min_radius, max_radius):
            folder_name_sub = folder_name+"/"+str(3*(radius*radius + radius)+1)
            process ="python3.6", "swarm-sim.py",'-w' + scenario,'-b' +folder_name_sub, "-m 1", "-d"+str(n_time),\
                                  "-r"+ str(radius), "-v" + str(0)
            p = subprocess.Popen(process, stdout=out, stderr=out)
            child_processes.append(p)
            process_cnt += 1
            #print("Process Nr. ", process_cnt, "started")
            #p.wait()
            #child_processes.clear()
            if len(child_processes) == os.cpu_count():
                while len(child_processes) == os.cpu_count():
                    for cp in child_processes:
                        if cp.poll() != None:
                            #print("finished")
                            child_processes.remove(cp)
                            break
        for cp in child_processes:
            cp.wait()
        fout = open(folder_name+"/aggregate_rounds.csv","w+")
        first=True
        #for scenario in scenarios:
        for radius in range(min_radius, max_radius):
            #f = open(folder+"/"+str(scenario)+"/aggregate_rounds.csv")
            f = open(folder_name+"/"+str(3*(radius*radius + radius)+1)+"/aggregate_rounds.csv")
            if not first:
                f.__next__() # skip the header
            else:
                first=False
            for line in f:
                fout.write(line)
            f.close() # not really needed
        fout.close()
    fout = open(folder+ "/aggregate.csv", "w+")
    first = True
    for scenario in scenarios:
            f = open(folder+"/"+scenario+"/aggregate_rounds.csv")
            if not first:
                f.__next__() # skip the header
            else:
                first=False
            for line in f:
                fout.write(line)
            f.close() # not really needed
    fout.close()


    #plot_generator("all_aggregates.csv", folder, 4,0, "aggregate", "bar")


if __name__ == "__main__":
    main(sys.argv[1:])



