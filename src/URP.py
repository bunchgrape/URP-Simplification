import selectors
import numpy as np




class URP:
    def __init__(self, cube_list):
        self.cube_list = cube_list
        self.num_cube, self.num_var = cube_list.shape
        self.var_marker = np.ones(self.num_var)
    
    
    def Simplify(self, cube_list):     
        # 1.terminatioin: all variable have been simplified
        dont_care = cube_list == 2
        num_dont_care = dont_care.sum(axis = 1)
        if (num_dont_care.max() == self.num_var):
            return np.expand_dims(2 * np.ones(self.num_var), axis=0)
        # 2.terminatioin: cube list is unate
        pos = cube_list == 1
        neg = cube_list == 0
        pos_sum = pos.sum(axis = 0)
        neg_sum = neg.sum(axis = 0)
        unate = pos_sum * neg_sum
        if (unate.sum() == 0):
            return self.DirectSimplify(cube_list)
        
        # 3.otherwise start URP
        # select a variable and mark it
        var_idx = self.selector(cube_list)
        self.var_marker[var_idx] = 0
        
        # split the cube_list
        p_cube = np.zeros((1, self.num_var))
        n_cube = np.zeros((1, self.num_var))
        for cube in cube_list:
            if (cube[var_idx] == 0):
                cube[var_idx] = 2
                cube = np.expand_dims(cube, axis=0)
                n_cube = np.append(n_cube, cube, axis=0)
            elif (cube[var_idx] == 1):
                cube[var_idx] = 2
                cube = np.expand_dims(cube, axis=0)
                p_cube = np.append(p_cube, cube, axis=0)
            else:
                cube = np.expand_dims(cube, axis=0)
                n_cube = np.append(n_cube, cube, axis=0)
                p_cube = np.append(p_cube, cube, axis=0)
        
        # TODO:
        p_cube = p_cube[1:]
        n_cube = n_cube[1:]
        
        # Solve empty cube list
        if n_cube.size == 0:
            P = self.Simplify(p_cube)
            P[:,var_idx] = 1
            return P
        elif p_cube.size == 0:
            N = self.Simplify(n_cube)
            N[:,var_idx] = 0
            return N
        else:
            P = self.Simplify(p_cube)
            N = self.Simplify(n_cube)

            return self.merge(P, N, var_idx)
    
    def merge(self, P, N, var_idx):
        # Cube list to receive result
        cube_merge = np.zeros((1, self.num_var))
        add_flag_N = np.ones(N.shape[0])      
        for i in range(P.shape[0]):
            # Traverse the cube list
            cube_add_flag = True
            cube = P[i]
            for j in range(N.shape[0]):
                if add_flag_N[j] == 0:
                    continue
                # Cube to compare with
                cube_ref = N[j]
                contain_flag = self.Contain(cube, cube_ref)
                
                if contain_flag != 0:
                    # 1.The cube is contained by cube j, add d
                    if contain_flag == -1:
                        cube_add = np.expand_dims(cube, axis=0)
                        cube_merge = np.append(cube_merge, cube_add, axis=0)
                        # Added already, break
                        cube_add_flag = False
                        break
                    # 2. The cube contains cube j, add e
                    elif contain_flag == 1:
                        cube_add = np.expand_dims(cube_ref, axis=0)
                        cube_merge = np.append(cube_merge, cube_add, axis=0)
                        add_flag_N[j] = 0
                        # Identical cubes
                        if (cube - cube_ref).sum() == 0:
                            add_flag_N[j] = 0
                            cube_add_flag = False
                        # Continue to mark other cubes
                        continue
                    # Prevent double add
                    
  
            # 3.Otherwise the cube is neither contained nor containing another cube 
            if (cube_add_flag):
                # Add x * d to list
                cube[var_idx] = 1
                cube_add = np.expand_dims(cube, axis=0)
                cube_merge = np.append(cube_merge, cube_add, axis=0)
        
        # Add the rest of cube_list N    
        for j in range(N.shape[0]):
            if add_flag_N[j] == 1:
                cube_ref = N[j]
                cube_ref[var_idx] = 0
                cube_add = np.expand_dims(cube_ref, axis=0)
                cube_merge = np.append(cube_merge, cube_add, axis=0)
        return cube_merge[1:]
    
    def DirectSimplify(self, cube_list):
        # Cube list to receive result
        cube_simplified = np.zeros((1, self.num_var))
        add_flag = np.ones(cube_list.shape[0])
        for i in range(cube_list.shape[0]):
            # Traverse the cube list
            cube_add_flag = True
            cube = cube_list[i]
            for j in range(i+1,cube_list.shape[0]):
                if add_flag[j] == 0:
                    continue
                # Cube to compare with
                cube_ref = cube_list[j]
                contain_flag = self.Contain(cube, cube_ref)
                
                if contain_flag != 0:
                    # 1.The cube is contained by cube j
                    if contain_flag == -1:
                        cube_add = np.expand_dims(cube_ref, axis=0)
                        if add_flag[j] != 0:
                            cube_simplified = np.append(cube_simplified, cube_add, axis=0)
                            add_flag[j] = 0
                    # 2. The cube contains cube j
                    elif contain_flag == 1:
                        cube_add = np.expand_dims(cube, axis=0)
                        if add_flag[i] != 0:
                            cube_simplified = np.append(cube_simplified, cube_add, axis=0)
                            add_flag[i] = 0
                            add_flag[j] = 0
                    # Prevent double add
                    cube_add_flag = False
                    break
  
            # 3.Otherwise the cube is neither contained nor containing another cube 
            if (add_flag[i] != 0 and cube_add_flag):
                cube_add = np.expand_dims(cube, axis=0)
                cube_simplified = np.append(cube_simplified, cube_add, axis=0)
                add_flag[i] = 0
                 
        return cube_simplified[1:]
    
    def Contain(self, cube, cube_ref):
        # Variable-wise comparation
        dif = cube - cube_ref       
        # Dont care information
        dont_care     = cube == 2
        dont_care_ref = cube_ref == 2
        dont_care_all = dont_care * dont_care_ref
        
        # A cube is contained by another
        # 1.The difference can only have either -1,-2 or 1,2
        # 2.If a variable is different, it must have a 2
        if ((dif.min() * dif.max()) == 0):
            if ((dif * dont_care_all).sum() == 0):
                # 1.The cube is contained by cube j
                if (dif.min() < 0):
                    return -1
                # 2.The cube contains cube j
                else:
                    return 1
        # 3.Neither one contains the other
        return 0
    
    def selector(self, cube_list):
        # sum the number of binate cubes
        pos = cube_list == 1
        neg = cube_list == 0
        
        # number of terms depend on the variable
        pos_sum = pos.sum(axis = 0)
        neg_sum = neg.sum(axis = 0)
        dep_sum = pos_sum + neg_sum
        binate  = pos_sum - neg_sum
        
        # select a variable
        dep_max = dep_sum.max()
        var_selector = np.where(dep_sum == dep_max)[0]
        
        # 1. select the variable with maximum terms dependent on it
        # 2. otherwise select the variable with maximum positive terms
        dif = -self.num_var-1
        var_idx = 0
        for idx in var_selector:
            if (binate[idx] > dif):
                var_idx = idx
    
        return var_idx
    
        