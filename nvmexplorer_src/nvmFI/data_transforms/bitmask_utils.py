import numpy as np
import random
import torch

if torch.cuda.is_available():
  pt_device = "cuda"
  if Debug:
    print("CUDA is available")
else:
  pt_device = "cpu"

#assumes operation on flattened matrix

def from_bitmask(wmb, data):
  """
  Translate bitmask encoded data back to original matrix M

  :param wmb: weight mask bits -- bit vectors to indicate non-zero values in original weight matrix M

  :param data: Data corresponding to the non-zero elements of matrix M
  """
  M = torch.zeros(wmb.size()[0], device=pt_device, dtype=torch.float32)

  M[wmb == 1] = data

  return M

def to_bitmask(M):
  """
  Returns the bitmask sparse format of matrix 'M'

  :param M: original weight matrix M
  """

  wmb = (M != 0).float()
  data = M[torch.nonzero(M, as_tuple=True)]

  return wmb, data


def encoded_capacity(wmb, data, num_bits):
  """
  Returns the total capacity in bits of the bitmask + data

  :param wmb: weight mask bits -- bit vectors to indicate non-zero values in original weight matrix M

  :param data: Data corresponding to the non-zero elements of matrix M

  :param num_bits: number of bits per data value to use

  """
  return (data.size()[0]*num_bits + wmb.size()[0])
