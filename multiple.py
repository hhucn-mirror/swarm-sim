import sys, getopt, subprocess
from datetime import datetime
import os
import configparser

import lib.csv_generator as cs


def runflac(idx, out, max_round, nTime ):
    """Use the flac(1) program to convert a music file to FLAC format.

    Arguments:
        idx: track index (starts from 0)
        data: album data dictionary

    Returns:
        A tuple containing the track index and return value of flac.
    """

    num = idx + 1
    process = "python3.6", "run.py", "-n" + str(max_round), "-m 1", "-d" + str(nTime), \
                                 "-r"+ str(num), "-v" + str(0)
    #     #p = subprocess.Popen(process, stdout=out, stderr=out)

    rv = subprocess.call(process, stdout=out, stderr=out)
    return (idx, rv)


def main(argv):
    nTime = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')[:-1]
    max_round = 5000
    seed_start = 1
    seed_end = 10
    param_lambda_min = 128
    param_lambda_max = 128

    config = configparser.ConfigParser(allow_no_value=True)
    config.read("config.ini")
    try:
        scenario_file = config.get ("File", "scenario")
    except (configparser.NoOptionError) as noe:
        scenario_file = "init_scenario.py"

    try:
        solution_file = config.get("File", "solution")
    except (configparser.NoOptionError) as noe:
        solution_file = "solution.py"

    try:
        opts, args = getopt.getopt(argv, "hs:w:r:n:v:", ["scenaro=", "solution="])
    except getopt.GetoptError:
        print('Error: multiple.py -r <randomeSeed> -w <scenario> -s <solution> -n <maxRounds>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('multiple.py -r <randomeSeed> -w <scenario> -s <solution>  -n <maxRounds>')
            sys.exit()
        elif opt in ("-s", "--solution"):
            solution_file = arg
        elif opt in ("-w", "--scenario"):
            sim_file = arg
        elif opt in ("-r", "--seed"):
            seedvalue = int(arg)
        elif opt in ("-n", "--maxrounds"):
           max_round = int(arg)
    round=1
    dir = "./outputs/multiple/charged"

    if not os.path.exists(dir):
        os.makedirs(dir)
    out = open(dir + "/multiprocess.txt", "w")
    child_processes = []
    # #idx=1
    # # with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
    # #     print(os.cpu_count() )
    # #     for idx in range(seedvalue):
    # #         tp.map(runflac, idx, out, max_round, nTime)
    round = 0
    round_cnt=0
    for param_lambda in range(param_lambda_min, param_lambda_max + 1):
        folder_name = dir + "/" + str(param_lambda)
        for seed in range(seed_start, seed_end+1):
            folder_name_sub = folder_name + "/" + str(seed)
            process ="python3.6", "run.py", "-n"+ str(max_round), "-m 1", "-d "+str(nTime),\
                                  "-r "+ str(seed), "-v " + str(0), "-p " + str(param_lambda), "-q"  + folder_name_sub,\
                                    "-s" + "self_charged" #"battery_powered"
            p = subprocess.Popen(process, stdout=out, stderr=out)
            round += 1
            round_cnt += 1
            print("Particle Number: " + str(param_lambda) + " | " + "Seed: " + str(seed) + " | " + " -- Round " + str(
                round_cnt) + " started!")
            child_processes.append(p)            # print("Process Nr. ", process_cnt, "started")
            # p.wait()
            # child_processes.clear()
            if len(child_processes) == 4:
                while len(child_processes) == 4:
                    for cp in child_processes:
                        if cp.poll() != None:
                            # print("finished")
                            child_processes.remove(cp)
                            break
        for cp in child_processes:
            cp.wait()

        try:
            fout = open(folder_name + "/aggregate_rounds.csv", "w+")
            first = True
            # for scenario in scenarios:
            for seed in range(seed_start, seed_end + 1):
                # f = open(folder+"/"+str(scenario)+"/aggregate_rounds.csv")
                # f = open(folder_name+"/"+str(3*(radius*radius + radius)+1)+"/aggregate_rounds.csv")
                try:
                    f = open(folder_name + "/" + str(seed) + "/aggregate_rounds.csv")
                    if not first:
                        f.__next__()  # skip the header
                    else:
                        first = False
                    for line in f:
                        fout.write(line)
                    f.close()  # not really neede
                except:
                    pass
            fout.close()
        except:
            pass
        cs.changing(folder_name, param_lambda)
        cs.all_aggregate_metrics(folder_name,param_lambda )

    fout=open(dir+"/all_aggregates.csv","w+")
    # first file:
    first = True

    # now the rest:
    for param_lambda in range(param_lambda_min, param_lambda_max + 1):
        f = open(dir+"/"+str(param_lambda) +"/all_aggregate_rounds.csv")
        if not first:
            f.__next__()  # skip the header
        else:
            first = False
        for line in f:
             fout.write(line)
        f.close() # not really needed
    fout.close()


if __name__ == "__main__":
    main(sys.argv[1:])
