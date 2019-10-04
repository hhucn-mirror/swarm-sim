import random
import numpy as np
import matplotlib.pylab as plt
import itertools
from mpl_toolkits import mplot3d
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D


#direction = [NE, E, SE, SW, W, NW]

x_offset = [0.5, 1,  0.5,   -0.5,   -1, -0.5 ]
y_offset = [ 1, 0, -1,   -1,    0,  1]

def solution(world):
    global arr

    if world.get_actual_round()==1:
        rows, cols = (1 + 2 * int(world.get_world_y_size()), 1 + 4 * int(world.get_world_x_size()))
        arr = [[int(0) for i in range(cols)] for j in range(rows)]
        print(arr)

    if world.get_actual_round()%1==0:
        for particle in world.get_particle_list():
            dir=search_personal_space(particle, world)
            if(dir!=-1):
                particle.move_to(dir)
            print(particle.coords)

            #if (abs(particle.coords[0]) <= world.get_world_x_size() and abs(particle.coords[1]) <= world.get_world_y_size()):
            arr[abs(int(particle.coords[1])-int(world.get_world_y_size()))][int(2*particle.coords[0])+2*int(world.get_world_x_size())]+=1
            print(arr)


    if world.get_actual_round()==world.get_max_round():
        y = np.arange(world.get_world_y_size(), -world.get_world_y_size()-1, -1)
        x = np.arange(-world.get_world_x_size(), world.get_world_x_size()+0.5, 0.5)


        Y, X = np.meshgrid(x, y)
        print(Y)
        print(X)

        arr2 = np.copy(arr)

        for i in range(0,len(arr)):
            for j in range(0,len(arr[i])):
                if arr[i][j]==0:
                    arr[i][j]=None
        arr=np.array(arr)
        print(arr)
        fig5, ax5 = plt.subplots()
        a5 = ax5.scatter(Y, X, c=arr2,  cmap='gray_r')
        fig5.colorbar(a5)

        ax5.set_xlabel('X coord')
        ax5.set_ylabel('Y coord')

        x=[]
        y=[]
        z=[]
        dx=[]
        dy=[]
        dz=[]
        for i in range(0, len(Y)):
            for j in range(0, len(Y[i])):
                if arr2[i][j]>0:
                    x.append(Y[i][j])
                    dx.append(0.2)
        for i in range(0,len(X)):
            for j in range(0,len(X[i])):
                if arr2[i][j]>0:
                    y.append(X[i][j])
                    dy.append(0.2)
        for i in range(0, len(arr)):
            for j in range(0,len(arr[i])):
                if arr2[i][j]>0:
                    z.append(0)
                    dz.append(arr2[i][j])


        fig4 = plt.figure()
        ax4 = fig4.add_subplot(111, projection='3d')

        dzc=np.array(dz)
        colors = plt.cm.Greys(dzc / float(arr2.max()))

        ax4.bar3d(x, y, z, dx, dy, dz, color=colors)
        ax4.set_xlabel('X coord')
        ax4.set_ylabel('Y coord')
        ax4.set_zlabel('Austausche')


        plt.show()


def search_personal_space(particle, world):
    dir = [0, 1, 2, 3, 4, 5]
    while len(dir) != 0:
        rnd_dir = random.choice(dir)
        if particle.particle_in(rnd_dir) or\
                abs(particle.coords[0]+x_offset[rnd_dir])>world.get_world_x_size() or\
                abs(particle.coords[1]+y_offset[rnd_dir])>world.get_world_y_size():
            dir.remove(rnd_dir)
        else:
            return rnd_dir
    return -1