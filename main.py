import sys
import warnings
from src import *
    


def main(argv):
    try:
        input_path = argv[1]
        result_path = argv[2]
        print(input_path)
    except:
        warnings.warn("Input format incorrect")

    cube_list = reader(input_path)
    
    simplifier = URP(cube_list)
    
    cube_list_simplified = simplifier.Simplify(cube_list)
    
    write(result_path, cube_list_simplified)
 
if __name__ == '__main__':
    main(sys.argv)