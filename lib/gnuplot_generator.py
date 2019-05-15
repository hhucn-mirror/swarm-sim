import subprocess
import pandas as pd


def generate_gnuplot(directory):

    # ################################## rounds.csv graphs ##################################
    round_data = pd.read_csv(directory+"/rounds.csv")
    plot = subprocess.Popen(['gnuplot', '--persist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    plot.stdin.write("set datafile separator ',' \n")
    plot.stdin.write('set xlabel "Rounds" \n')

    i = 1
    for column in round_data.columns:
        if i > 8:
            plot.stdin.write('set ylabel "%s" \n' % column)
            plot.stdin.write("set output '" + directory + "/rounds_%s.png' \n" % column)
            plot.stdin.write("set term png giant size 800,600 font 'Helvetica,15' \n")
            plot.stdin.write("set yrange [0:*] \n")
            plot.stdin.write("unset key \n")
            plot.stdin.write("set style line 1 lw 1.5 lc rgb '" + "black" + "'\n")
            plot.stdin.write(
                "plot '" + directory + "/rounds.csv' using 4:" + str(i) + " title '" + column + "' with lines ls 1\n")
            plot.stdin.write("set terminal pdf monochrome font 'Helvetica,10' \n")
            plot.stdin.write("set output '" + directory + "/rounds_%s.pdf' \n" % column)
            plot.stdin.write("replot \n")
        i += 1
    # ########################################################################################

    # ################################## particle.csv graphs ###################################
    particle_data = pd.read_csv(directory+"/particle.csv")
    plot = subprocess.Popen(['gnuplot', '--persist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    plot.stdin.write("set datafile separator ',' \n")
    plot.stdin.write('set xlabel "Particle" \n')

    i = 1
    for column in particle_data.columns:
        if i > 3:
            plot.stdin.write('set ylabel "%s" \n' % column)
            plot.stdin.write("set term png giant size 800,600 font 'Helvetica,15' \n")
            plot.stdin.write("set boxwidth 0.30 \n")
            plot.stdin.write("set style fill solid \n")
            plot.stdin.write("set yrange [0:*] \n")
            plot.stdin.write("unset key \n")
            plot.stdin.write("set style line 1 lc rgb '" + "black" + "' \n")
            plot.stdin.write("set output '" + directory + "/particle_%s.png' \n" % column)
            plot.stdin.write(
                "plot '" + directory + "/particle.csv' using 2:" + str(i) + ":xticlabels(2) with boxes ls 1 \n")
            plot.stdin.write("set terminal pdf monochrome font 'Helvetica,10' \n")
            plot.stdin.write("set output '" + directory + "/particle_%s.pdf' \n" % column)
            plot.stdin.write("replot \n")
        i += 1
    # #########################################################################################

    # ################################## movement.csv graphs ##################################
    movement_data = pd.read_csv(directory + "/particle.csv")
    plot = subprocess.Popen(['gnuplot', '--persist'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    plot.stdin.write("set datafile separator ',' \n")

    for i in range(1, int(len(movement_data.index) + 1)):
        # 2D plots
        plot.stdin.write('set xlabel "Particle X coord" \n')
        plot.stdin.write('set ylabel "Particle Y coord" \n')
        plot.stdin.write("set term png giant size 800,600 font 'Helvetica,15' \n")
        plot.stdin.write("set style line 1 lc rgb '" + "black" + "'\n")
        plot.stdin.write("set output '" + directory + "/particle_%s_movement_2D.png' \n" % str(i))
        plot.stdin.write("set ticslevel 0\n")
        plot.stdin.write(
            "plot '" + directory + "/movement.csv' using " + str(2 * i) + ":" + str(2 * i + 1) + " title 'Particle " + str(i) + "' with lines ls 1 \n")
        plot.stdin.write("set terminal pdf monochrome font 'Helvetica,10' \n")
        plot.stdin.write("set output '" + directory + "/particle_%s_movement_2D.pdf' \n" % str(i))
        plot.stdin.write("replot \n")

        # 3D plots
        plot.stdin.write('set xlabel "X" \n')
        plot.stdin.write('set ylabel "Round" \n')
        plot.stdin.write('set zlabel "Y" \n')
        plot.stdin.write("set term png giant size 800,600 font 'Helvetica,10' \n")
        plot.stdin.write("set style line 1 lc rgb '" + "black" + "'\n")
        plot.stdin.write("set output '" + directory + "/particle_%s_movement_3D.png' \n" % str(i))
        plot.stdin.write("set ticslevel 0 \n")
        plot.stdin.write("splot '" + directory + "/movement.csv' using " + str(2 * i) + ":1:" +
                         str(2 * i + 1) + " title 'Particle " + str(i) + "' with lines ls 1 \n")
        # plot.stdin.write("splot '" + directory + "/movement.csv' using 1:" + str(2 * i) + ":" + str(2 * i + 1) + " with lines\n")
        # plot.stdin.write("splot '" + directory + "/movement.csv' using " + str(2 * i) + ":" + str(2 * i + 1) + ":1 with lines ls 1\n")
        plot.stdin.write("set terminal pdf monochrome font 'Helvetica,10' \n")
        plot.stdin.write("set output '" + directory + "/particle_%s_movement_3D.pdf' \n" % str(i))
        plot.stdin.write("replot \n")
    # #########################################################################################

    plot.stdin.write('quit\n')



