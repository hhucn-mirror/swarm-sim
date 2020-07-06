import subprocess

import pandas as pd


def generate_gnuplot(directory):
    data = pd.read_csv(directory + "/rounds.csv")
    plot = subprocess.Popen(['gnuplot', '--persist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            universal_newlines=True)
    plot.stdin.write("set datafile separator ',' \n")

    plot.stdin.write('set xlabel "Rounds" \n')
    for i, data_points in enumerate(data.columns[3:]):
        plot.stdin.write('set ylabel "%s" \n' % data_points)
        plot.stdin.write("set output '" + directory + "/rounds_%s.png' \n" % data_points)
        plot.stdin.write("set term png giant size 800,600 font 'CMU Serif,20' \n")
        plot.stdin.write(
            "plot '" + directory + "/rounds.csv' using 1:" + str(
                i + 4) + " title '" + data_points + "' with lines axis x1y1 smooth unique \n")
        plot.stdin.write("set terminal pdf monochrome font 'CMU Serif,10' \n")
        plot.stdin.write("set output '" + directory + "/rounds_%s.pdf' \n" % data_points)
        plot.stdin.write("replot \n")

    data = pd.read_csv(directory + "/particle.csv")
    plot = subprocess.Popen(['gnuplot', '--persist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            universal_newlines=True)
    plot.stdin.write("set datafile separator ',' \n")

    plot.stdin.write('set xlabel "Particle" \n')
    for i, data_points in enumerate(data.columns[2:]):
        plot.stdin.write('set ylabel "%s" \n' % data_points)
        plot.stdin.write("set term png giant size 800,600 font 'CMU Serif,20' \n")
        plot.stdin.write("set output '" + directory + "/particle_%s.png' \n" % data_points)
        plot.stdin.write(
            "plot '" + directory + "/particle.csv' using 2:" + str(
                i + 3) + " title '" + data_points + "' with lines axis x1y1 smooth unique \n")
        plot.stdin.write("set terminal pdf monochrome font 'CMU Serif,10' \n")
        plot.stdin.write("set output '" + directory + "/particle_%s.pdf' \n" % data_points)
        plot.stdin.write("replot \n")

    plot.stdin.write('quit\n')
