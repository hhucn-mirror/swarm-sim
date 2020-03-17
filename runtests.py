import pandas
import shutil
import os
import sys
import time
from glob import glob
import random
import importlib
from multiprocessing import Pool, Queue, Process, Manager
from queue import Empty

NUMBER_OF_PROCESSES = 3

NUMBER_OF_SEEDS = 50
SEEDS = [1005452923949099817, 104729571718011065, 1151522834903635200, 135691580820658646, 1500385114400036822,
         1757090061937575188, 1784647508577935808, 2039726448634163130, 2166279188521729848, 2382258227726526776,
         239895843343948783, 2465231629035308954, 3023534726851758369, 3042134290703503464, 3195374428520842592,
         3605860666315517243, 3871570327581174452, 4145153237065709152, 4728114858318564273, 4814746228620134542,
         4833615556434205377, 5073531332002539401, 5095606951029691221, 5141005627055929417, 5200664720089049428,
         5257365277667067163, 5576987183874749062, 5671404872469712192, 5894081778140307249, 6047742730548401955,
         6188382242110290117, 6406019102658191314, 6579115118694624540, 6734093137683196141, 6989065390847802654,
         706135037950337258, 729212062188970625, 743915707375033600, 7619309402902287165, 7641818786393216428,
         7674667646562244311, 82162779224662555, 8279579456414977604, 8311339547884988640, 8445994089275729783,
         846607075699250924, 8756480475294688387, 9168466799227518454, 9190667985687051790, 9216123937619767538]
MIN_PARTICLE_COUNT = 20
MAX_PARTICLE_COUNT = 200
STEPSIZE_PARTICLE_COUNT = 20
USE_PARTICLE_COUNT = True
MAX_ROUNDS = 10000
SCENARIOS = ["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave",
             "giant_cave", "bottle", "small_bottle"]
            #["single_tile_few_particles", "concave_shape", "simple_shape", "tube_island", "small_cave", "strange_cave", "giant_cave", "bottle", "small_bottle"]
SOLUTIONS = ["p_max_lifetime.main"]#, "base.main", "basebetter.main", "p_max_lifetime.main", "send_free_location_info.main", "only_move_if_best_match.main", "p_max_with_id.main",
             #"prevent_circle_walking.main"]


def progress_counter_func(taskqueue, test_count):
    tests_done = 0
    while tests_done < test_count:
        try:
            taskqueue.get(False)
            tests_done += 1
            print(str(tests_done / test_count * 100) + "%", "done.")
        except Empty:
            pass
        time.sleep(5)


def run_test(args):
    simulator = importlib.import_module("swarm-sim")
    solution = args[0]
    scenario = args[1]
    seed = args[2]
    particle_count = args[3]
    taskqueue = args[4]
    simulator.swarm_sim(["-r", str(seed), "-w", scenario, "-s", solution, "-v", "0",
                         "-n", str(MAX_ROUNDS), "-d", "1337-01-11_13-37-42", "-m", "1", "-p", particle_count])
    taskqueue.put(seed)


def eval_test(solution_scenario):
    solution = solution_scenario[0]
    scenario = solution_scenario[1]
    files = glob("./outputs/mulitple/1337-01-11_13-37-42_" + scenario + "_" +
                 solution.split(".")[0] + "/*/aggregate_rounds.csv")
    data_by_particle_count = {}
    for file in files:
        data = pandas.read_csv(file)
        particle_count = data["Particle Counter"].values[0]
        if data_by_particle_count.get(particle_count) is None:
            data_by_particle_count[particle_count] = []
        data_by_particle_count[particle_count].append(data)
    output_map = {} # particle_count -> output data
    for particle_count, data_list in data_by_particle_count.items():
        sum = 0
        failures = 0
        failed_seeds = []
        successful_seeds = []
        for data in data_list:
            rounds_taken = data["Rounds Total"].values[0]
            if rounds_taken < MAX_ROUNDS:
                sum += rounds_taken
                successful_seeds.append(data["Seed"].values[0])
            else:
                failures += 1
                failed_seeds.append(data["Seed"].values[0])
        avg = MAX_ROUNDS
        if (len(data_list) - failures) > 0:
            avg = sum / (len(data_list) - failures)
        output_map[particle_count] = {"avg": avg, "fails": failures, "failed_seeds": failed_seeds,
                                      "successful_seeds": successful_seeds}
    print("Solution", solution, "in Scenario", scenario, "done.")
    return {"solution": solution, "scenario": scenario,
            "output_data": output_map}


def output_sorter(test):
    return SOLUTIONS.index(test["solution"]) + SCENARIOS.index(test["scenario"]) * len(SOLUTIONS)


if __name__ == "__main__":
    pandas.set_option("display.max_columns", 100)
    if os.path.isdir("./outputs"):
        shutil.rmtree("./outputs")
    taskmanager = Manager()
    taskqueue = taskmanager.Queue()
    solutions_scenarios = ((solution, scenario) for scenario in SCENARIOS for solution in SOLUTIONS)
    if USE_PARTICLE_COUNT:
        args = ((solution, scenario, seed, particle_count, taskqueue)
                for scenario in SCENARIOS
                for solution in SOLUTIONS
                for seed in SEEDS
                for particle_count in range(MIN_PARTICLE_COUNT, MAX_PARTICLE_COUNT + 1, STEPSIZE_PARTICLE_COUNT))
    else:
        args = ((solution, scenario, random.randint(0, sys.maxsize), -1, taskqueue)
                for scenario in SCENARIOS
                for solution in SOLUTIONS
                for _ in range(NUMBER_OF_SEEDS))
    args = list(args)
    test_count = len(args)
    print("number of tests:", test_count)
    progress_process = Process(target=progress_counter_func, args=(taskqueue, test_count))
    progress_process.daemon = True
    progress_process.start()
    with Pool(processes=NUMBER_OF_PROCESSES) as pool:
        print("starting")
        list(pool.map(run_test, args))
        print("tests done, starting evaluation")
        output = list(pool.map(eval_test, solutions_scenarios))
        output.sort(key=output_sorter)
    progress_process.join()
    outfile = open("./outputs/output.txt", "w+")
    for test in output:
        outfile.write("Solution: " + str(test["solution"]) + "\n")
        outfile.write("scenario: " + str(test["scenario"]) + "\n")
        sorted_output = sorted(list(test["output_data"].items()), key=lambda x: x[0])
        for particle_count, test_data in sorted_output:
            outfile.write(" Particle count: " + str(particle_count) + "\n")
            outfile.write("     avg rounds taken: " + str(test_data["avg"]) + "\n")
            if test_data["avg"] < MAX_ROUNDS:
                outfile.write("     successful seeds: " + str(test_data["successful_seeds"]) + "\n")
            outfile.write("     failed simulations: " + str(test_data["fails"]) + "\n")
            if test_data["fails"] > 0:
                outfile.write("     failed seeds: " + str(test_data["failed_seeds"]) + "\n")
