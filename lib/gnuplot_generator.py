from codecs import xmlcharrefreplace_errors

import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pn
import seaborn as sns

def plot_generator(file,directory, start, x_index, name, plot_type="line"):
    with open(directory+"/"+file, 'r') as data:
        plotter(data, directory, start, x_index, name, plot_type)


def plotter(data, directory, start, x_index, name, plot_type):
    csv_object = csv.reader(data, delimiter=',')
    a = next(csv_object)
    x = []
    y = []
    plt.figure(figsize=(20, 12))
    for col in range(start, len(a)):
        x.clear()
        y.clear()
        for row in csv_object:
            if plot_type == "line":
                x.append(int(row[x_index]))
            elif plot_type == "bar":
                x.append(str(row[x_index]))
            if row[col] != "nan":
                y.append(int(float(row[col])))
            else:
                y.append(np.nan)
        if plot_type == "line":
            plt.plot(x, y)
        elif plot_type == "bar":
            plt.bar(x, y, align='edge', width=0.5)
        plt.xlabel(a[x_index], fontsize=4)
        plt.xticks(rotation=45)
        plt.ylabel(a[col])
        plt.savefig(directory + '/' + name + '_' + a[col] + '.png')
        plt.clf()
        data.seek(0)
        plot = csv.reader(data, delimiter=',')
        next(plot)



def panders_plotter(file, directory, name):
    with open(directory + "/" + file, 'r') as data:

        plt.clf()
        csv_object = csv.reader(data, delimiter=',')
        next(csv_object)

        # csv_object = csv.reader(data, delimiter=',')
        i = 0
        x = []
        y = []
        e = []
        plt.ylabel('Percentage')
        plt.xlabel('Agent Numbers')
        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[17]) * 100)
            i += 1
            if i == 30:
                break
        plt.plot(x, y, marker='.', color='r', label="Success rate")
        plt.savefig(directory + '/' + "SuccesRate_" + name + '.png')

        x=[]
        y=[]
        e=[]
        i=0
        data.seek(0)
        next(csv_object)
        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[23]))
            e.append(float(row[24]))
            i+=1
            if i == 30:
                break
        #plt.errorbar(x, y, yerr=e)
        plt.axhline(y=5, color='orange', linestyle='-', label="5\% line")
        plt.errorbar(x, y, yerr=e, ecolor='black', label="Changes with SD")
        #plt.plot(x, y)
        #plt = csv_object.plot( kind='line', x='Particle Counter',  y='Rounds Avg')
        plt.ylabel('Percentage')
        plt.xlabel('Agent Numbers')
        plt.legend(loc="upper right")
        #plt.legend()
        #plt.savefig(directory + '/' + "rounds" + '.pdf')
        #plt.savefig(directory + '/' +"error_rounds" + '.png')
        #plt.plot(x, y)
        plt.savefig(directory + '/' +"PCARPA_"+name + '.png')

        plt.clf()
        data.seek(0)
        next(csv_object)

        # csv_object = csv.reader(data, delimiter=',')
        i = 0
        x = []
        y = []
        e = []
        plt.ylabel('Percentage changed (\%)')
        plt.xlabel('Agent Numbers')

        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[17]) * 100)
            i += 1
            if i == 30:
                break
        plt.plot(x, y, marker='.', color='r', label="Success rate")
        data.seek(0)
        next(csv_object)
        plt.ylabel('Percentage changed (\%)')
        plt.xlabel('Agent Numbers')
        plt.axhline(y=5, color='orange', linestyle='-', label="5\% line")
        i = 0
        x = []
        y = []
        e = []
        # csv_object = csv.reader(data, delimiter=',')
        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[21]))
            e.append(float(row[22]))
            i += 1
            if i == 30:
                break
        plt.errorbar(x, y, yerr=e, ecolor='black', label="Changes with SD")
        plt.legend(loc="upper right")
        plt.savefig(directory + '/' + "PCAR_" + name + '.png')

        plt.clf()
        data.seek(0)
        next(csv_object)
        #csv_object = csv.reader(data, delimiter=',')
        i = 0
        x = []
        y = []
        e = []
        plt.ylabel('Rounds')
        plt.xlabel('Agent Numbers')
        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[1]))
            e.append(float(row[2]))
            i+=1
            if i == 30:
                break
        plt.bar(x, y, yerr=e, ecolor='black')
        plt.savefig(directory + '/' +"AR_"+name + '.png')

        plt.clf()
        data.seek(0)
        next(csv_object)
        #csv_object = csv.reader(data, delimiter=',')
        i = 0
        x = []
        y = []
        e = []
        plt.ylabel('Rounds')
        plt.xlabel('Agent Numbers')

        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[5]))
            e.append(float(row[6]))
            i+=1
            if i == 30:
                break
        plt.bar(x, y, yerr=e, ecolor='black')
        plt.savefig(directory + '/' +"ARPA_"+name + '.png')

        plt.clf()
        data.seek(0)
        next(csv_object)
        # csv_object = csv.reader(data, delimiter=',')
        i = 0
        x = []
        y = []
        e = []
        plt.ylabel('Percentage')
        plt.xlabel('Agent Numbers')

        for row in csv_object:
            x.append(int(row[0]))
            y.append(float(row[17])*100)
            i += 1
            if i == 30:
                break
        plt.plot(x, y,  marker='.')
        plt.savefig(directory + '/' + "SuccesRate" + name + '.png')

        # for l  in grp['Layer'].values:
            #     if int(l)>layer:
            #         index= csv_object.index(grp['Layer'].values[l])
            #         print(l, index)
            #         layer = l



# def double_bar(data, directory, start, x_index, name, plot_type):
#     csv_object = csv.reader(data, delimiter=',')
#     a = next(csv_object)
#     x = []
#     d = []
#     e = []
#     f = []
#     y = [[]]
#     #plt.figure(figsize=(30, 20))
#     for row in csv_object:
#             x.append(str(row[0]))
#             d.append(int(float(row[1])))
#             e.append(int(float(row[2])))
#             f.append(int(float(row[3])))
#
#     # if plot_type == "line":
#         #     plt.plot(x, y, 'ro')
#         # elif plot_type == "bar":
#         #     plt.bar(x, y, align='edge', width=0.5)
#         #
#         # plt.xlabel(a[x_index], fontsize=4)
#         # plt.title(name)
#         # plt.xticks(rotation=45)
#         # plt.ylabel(a[col])
#         # plt.savefig(directory + '/'+ name + '_' + a[col] + '.png')
#         # plt.clf()
#         # data.seek(0)
#         # plot = csv.reader(data, delimiter=',')
#         # next(plot)
#     fig, ax = plt.subplots()
#     fig.set_figheight(15)
#     fig.set_figwidth(30)
#     ind = np.arange(len(x))  # the x locations for the groups
#     width = 0.2  # the width of the bars
#     p = ax.bar(ind + width, d, align='center', width=width)
#     r = ax.bar(ind , e, align='center', width=width)
#     s = ax.bar(ind - width, f, align='center', width=width)
#     # ax.set_xlim(-width, len(ind) + width)
#     # ax.set_ylim(0, 45)
#     # ax.set_ylabel('Scores')
#     # ax.set_title('Scores by group and gender')
#     #xTickMarks = ['Group' + str(i) for i in range(1, 6)]
#     #ax.set_xticks(ind + width)
#     #xtickNames = ax.set_xticklabels(xTickMarks)
#     #plt.setp(xtickNames, rotation=45, fontsize=10)
#     fig.legend((p[0], r[0], s[0]),  # The line objects
#               ("# of Particles", "AVG Rounds/Particle", "AVG Steps/Particle"),  # The labels for each line
#                loc="upper left",  # Position of legend
#                #borderaxespad=0.1,  # Small spacing around legend box
#                title="Legend Title", prop={'size': 20}  # Title for the legend
#                )
#     ## add a legend
#     #ax.legend((rects1[0], rects2[0]), ('Men', 'Women')
#     #plt.subplots_adjust(right=0.85)
#     plt.title(name)
#     plt.xticks(rotation=45)
#     plt.xticks(ind, x)
#     plt.ylabel('rounds')
#     #plt.legend()
#     plt.savefig(directory + '/testi' +'.png')
#     # plt.clf()
#     # data.seek(0)
#     # plot = csv.reader(data, delimiter=',')
#     # next(plot)


#plot_generator("all_aggregates.csv", "../outputs/multiple/working_multi_layer_2020-02-29_14:34:1_leader_coating", 4,0, "Multi_Layer: 60 Particles", "bar")


#plot_generator("all_aggregates.csv", "../outputs/multiple/battery", 1, 0, "all", "bar")
panders_plotter("all_aggregates.csv", "../outputs/multiple/battery", "b")
panders_plotter("all_aggregates.csv", "../outputs/multiple/charged", "c")
#panders_plotter("result_sd.csv", "../")
#panders_plotter("test.csv", "../outputs/multiple/working_multi_layer_2020-02-29_14:34:1_leader_coating", 1,0, "Multi_Layer: 60 Particles", "bar")
