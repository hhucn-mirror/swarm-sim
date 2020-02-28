
import matplotlib.pyplot as plt
import csv
import numpy as np

def plot_generator(file,directory,start, name, plot_type="line"):
    with open(directory+"/"+file, 'r') as data:
        plotter(data, directory, start, name, plot_type)

def plotter(data, directory, start, name, plot_type):
    csv_object = csv.reader(data, delimiter=',')
    a = next(csv_object)
    x = []
    y = []
    for col in range(start+1, len(a)):
        x.clear()
        y.clear()
        for row in csv_object:
            if plot_type == "line":
                x.append(int(row[start]))
            elif plot_type == "bar":
                x.append(str(row[start]))
            if row[col] != "nan":
                y.append(int(float(row[col])))
            else:
                y.append(np.nan)
        if plot_type == "line":
            plt.plot(x, y, 'ro')
        elif plot_type == "bar":
            plt.bar(x, y)
        plt.xlabel(a[start])
        plt.ylabel(a[col])
        plt.savefig(directory + '/'+ name + '_' + a[col] + '.png')
        plt.clf()
        data.seek(0)
        plot = csv.reader(data, delimiter=',')
        next(plot)
