from nvmexplorer_src.nvmFI import fault_injection
import numpy as np

def main():
  """ Runs an example fault injection experiment on a matrix of random numbers stored using MLC RRAM (3 bits per cell; 6b fixed point datatype)
  Please see nvmexplorer_src/nvmFI for more details and examples
  """
  print("Test for single matrix fault generation\n\n")

  test_size = (1000,1000)

  mat = np.random.uniform(-1,1,size=test_size)
  print(mat)

  for i in range(2):  

    mat = fault_injection.mat_fi(mat, seed=i, int_bits=2, frac_bits=4, q_type='signed', rep_conf = np.array([8, 8]), encode = 'dense')
    print("Matrix after injection with seed"+str(i))
    print(mat)


if __name__=="__main__":
  main()

