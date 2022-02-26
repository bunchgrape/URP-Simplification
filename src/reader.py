import numpy as np



def reader(path):
    file = open(path, "r")
    num_var = int(file.readline())
    num_line = int(file.readline())
    
    cube_list = np.zeros((num_line, num_var))
    for i in range(num_line):
        line = file.readline()
        cube = np.array(list(line[:num_var]))
        cube_list[i] = cube
    
    return cube_list
    

def write(path, cube_list):
    file = open(path, "w")
    num_cube, num_var = cube_list.shape
    file.write(str(num_var)+'\n')
    file.write(str(num_cube)+'\n')
    
    list = []
    for cube in cube_list:
        count = 0
        for var in cube:
            count = int(var) + count * 10
        list.append(count)
    list.sort()
    for cube in list:
        file.write(str(cube).zfill(num_var))
        file.write('\n')