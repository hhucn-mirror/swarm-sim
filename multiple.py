import sys, getopt, subprocess
from datetime import datetime
import os
import configparser
import multiprocessing
import concurrent.futures

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
    max_round = 2500
    seed_start = 1
    seed_end = 50
    param_lambda_min = 1
    param_lambda_max = 5
    param_delta_min = -2
    param_delta_max = 1
    for param_lambda in range(param_lambda_min, param_lambda_max + 1):
        for param_delta in range(param_delta_min, param_delta_max + 1):

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
            dir = "./outputs/mulitple/" + str(nTime) + "_" + scenario_file.rsplit('.', 1)[0] + "_" + \
                  solution_file.rsplit('.', 1)[0]

            if not os.path.exists(dir):
                os.makedirs(dir)
            out = open(dir + "/multiprocess.txt", "w")
            child_processes = []
            #idx=1
            # with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as tp:
            #     print(os.cpu_count() )
            #     for idx in range(seedvalue):
            #         tp.map(runflac, idx, out, max_round, nTime)
            round = 0
            round_cnt=0
            for seed in range(seed_start, seed_end+1):
                process ="python3.6", "run.py", "-n"+ str(max_round), "-m 1", "-d"+str(nTime),\
                                      "-r"+ str(seed), "-v" + str(0), "-p" + str(param_lambda), "-q" + str(param_delta)
                if round == os.cpu_count():
                    for cp in child_processes:
                        cp.wait()
                    round = 0
                p = subprocess.Popen(process, stdout=out, stderr=out)
                #p = multiprocessing.Process(target=process)
                round += 1
                round_cnt += 1
                print("Seed: " + str(seed) + " | " + "Lambda: " + str(param_lambda) + " | " + "Delta: " + str(param_delta) + " -- Round " + str(round_cnt) + " started!")
                child_processes.append(p)


            for cp in child_processes:
                cp.wait()


    fout=open(dir+"/all_aggregates.csv","w+")
    # first file:
    for line in open(dir+"/"+str(seed_start)+ "_" + str(param_lambda) + "_" + str(param_delta) + "/aggregate_rounds.csv"):
        fout.write("Lambda,Delta," + line)
        break
    # now the rest:
    for param_lambda in range(param_lambda_min, param_lambda_max + 1):
        for param_delta in range(param_delta_min, param_delta_max + 1):
            for seed in range(seed_start, seed_end+1):
                f = open(dir+"/"+str(seed)+"_" + str(param_lambda) + "_" + str(param_delta) +"/aggregate_rounds.csv")
                f.__next__() # skip the header
                for line in f:
                     fout.write(str(param_lambda) + "," + str(param_delta) + "," + line)
                f.close() # not really needed
    fout.close()


if __name__ == "__main__":
    main(sys.argv[1:])
