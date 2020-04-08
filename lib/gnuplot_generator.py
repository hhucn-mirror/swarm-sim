import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pn

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
            plt.plot(x, y, 'ro')
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
        csv_object = pn.read_csv(data, delimiter=',')
        #csv_object.plot.bar(0)
        fig, ax = plt.subplots()
        # for key, grp in csv_object.groupby(['Scenario']):
        #     ax = grp.plot(ax=ax, kind='line', x='Particles', y='Steps', label=key)
        # #plt.show()
        # plt.ylabel('Steps')
        # plt.savefig(directory + '/' +'steps' + '.pdf')

        # for key, grp in csv_object.groupby(['Scenario']):
        #     ax = grp.plot(ax=ax, kind='line', x='Particles', y='AVG Steps per Tile', label=key)
        # plt.ylabel('AVG Steps per Particle')
        # plt.savefig(directory + '/' +'forParticleSteps' + '.pdf')
        #print(csv_object[['Layer']])

        for key, grp in csv_object.groupby(['Scenario']):
            layer = 0

            #key = key + "("+str(grp['Tiles'].values)+")"
            #print(grp['Particles'].values)
            #rounds=int(round(grp['Rounds'].mean(),2))
            #grp.plot(ax=ax, kind='bar', x=grp['Particles'].values[0],  y=rounds, label=key)
            grp['bla'] = grp['Layer'].diff()
            df_filtered = grp[grp['bla'] != 0]
            for a, b in df_filtered.groupby(['Scenario']):
                grp.plot(ax=ax, kind='line', x='Particles', y='Steps', label=key)
                b.plot.scatter(ax=ax, x='Particles', y='Steps')
                ax.grid()
            plt.ylabel('Steps')
            plt.savefig(directory + '/' + key + '.pdf')
            plt.savefig(directory + '/' + key + '.png')

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


panders_plotter("aggregate.csv", "../outputs/multiple/c", "bar")
#panders_plotter("test.csv", "../outputs/multiple/working_multi_layer_2020-02-29_14:34:1_leader_coating", 1,0, "Multi_Layer: 60 Particles", "bar")