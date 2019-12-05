import pandas
import shutil
import os
import sys
from glob import glob
import random
import importlib
simulator = importlib.import_module("swarm-sim")
pandas.set_option("display.max_columns", 100)
NUMBER_OF_SEEDS = 5

scenarios = ["single_tile_particle_line", "single_tile_few_particles", "single_tile_many_particles", "concave_shape",
             "simple_shape", "tube_island", "strange_cave", "giant_cave"]
solutions = ["base.main", "send_free_location_info.main", "only_move_if_best_match.main"]
leel = []
for solution in solutions:
    for scenario in scenarios:
        if os.path.isdir("/Users/Gorden/Python/swarm-sim/outputs"):
            shutil.rmtree("/Users/Gorden/Python/swarm-sim/outputs")
        for i in range(NUMBER_OF_SEEDS):
            simulator.swarm_sim(["-r", str(random.randint(0, sys.maxsize)), "-w", scenario, "-s", solution])
        files = glob("/Users/Gorden/Python/swarm-sim/outputs/*/rounds.csv")
        sum = 0
        failures = 0
        for file in files:
            data = pandas.read_csv(file)
            line = data.tail(1)["Round Number"].values
            if len(line > 0):
                if line[0] < 1000:
                    sum += line[0]
                else:
                    failures += 1
        avg = 1000
        if (len(files) - failures) > 0:
            avg = sum / (len(files) - failures)
        leel.append({"solution": solution, "scenario": scenario,
                     "avg": avg, "fails": failures})
        print("test", solution, ",", scenario, "done")

for test in leel:
    print("Solution:", test["solution"])
    print("scenario:", test["scenario"])
    print("avg rounds taken:", test["avg"])
    print("failed simulations:", test["fails"])
