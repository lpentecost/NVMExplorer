import numpy as np
import torch
import random
import pickle
import sys
import os
import time
import cProfile, pstats

if torch.cuda.is_available():
  pt_device = "cuda"
  if Debug:
    print("CUDA is available")
else:
  pt_device = "cpu"

def get_afloat_bias(num_float, n_exp):
    """
    Extract bias term for AdaptivFloat data format https://arxiv.org/abs/1909.13271

    :param num_float: input value as float
    :param n_exp: number of exponential bits for adaptivFloar data format
    """
    # supprt for AdaptivFloat [cite]
    bias_temp = np.frexp(num_float.max().item())[1]-1
    bias = bias_temp - (2**n_exp -1)
    
    return bias

def get_q_afloat(num_float, n_bits, n_exp, bias):
    """
    Conversion to AdaptivFloat data format https://arxiv.org/abs/1909.13271

    :param num_float: input value as float
    :param n_bits: total number of bits per value (mantissa bits = n_bits - n_exp)
    :param n_exp: number of exponential bits for adaptivFloar data format
    :param bias: input bias term
    """
    # support for AdaptivFloat [cite]
    n_mant = n_bits-1-n_exp
  
    # 1. store sign value and do the following part as unsigned value
    sign = torch.sign(num_float)
    num_float = abs(num_float)

    # 2. limits the range of output float point
    min_exp = 0+bias
    max_exp = 2**(n_exp)-1+bias 
    #print("min(exp) =",min_exp,"max(exp) =",max_exp,"bias =",bias) 
    ## min and max values of adaptivfloat
    min_value = 2.0**min_exp*(1+2.0**(-n_mant))
    max_value = (2.0**max_exp)*(2.0-2.0**(-n_mant))
    
    #print(min_value, max_value)
    ## 2.1. reduce too small values to zero
    num_float[num_float < 0.5*min_value] = 0
    num_float[(num_float > 0.5*min_value)*(num_float < min_value)] = min_value
     
     
    ## 2.2. reduce too large values to max value of output format
    num_float[num_float > max_value] = max_value
    
    # 3. get mant, exp (the format is different from IEEE float)
    mant, exp = np.frexp(num_float.cpu().numpy())
    mant = torch.tensor(mant, dtype=torch.float32, device=pt_device)
    exp = torch.tensor(exp, dtype=torch.float32, device=pt_device)

    mant = 2*mant
    exp = exp - 1

    ## 4. quantize mantissa
    scale = 2**(-n_mant) ## e.g. 2 bit, scale = 0.25
    mant = ((mant/scale).round())*scale
    
    if False:
      power_exp = torch.exp2(exp)
      float_out = sign*power_exp*mant
      print("Adaptive float rebuild")
      print(float_out)
      print("Mantissa")
      print(mant)
      print("Exponent")
      print(exp-bias)
      print("Power")
      print(power_exp)
    
    return (sign < 0).type(torch.float32), (abs(mant)-1), exp+abs(bias), bias

def get_binary_array_mat(orig_flt, rep_conf, int_bits, frac_bits, exp_bias, q_type):
  """
  Format an input float value into binary array for bit-level fault injection

  :param orig_flt: input value (floating point)
  :param rep_conf: mapping from number of bits in input value to number of levels per NVM storage cell (e.g., [2, 2] for a 2 bit input into SLCs)
  :param int_bits: number of integer bits for data format (if applicable)
  :param frac_bits: number of fractional bits for data format (if applicable)
  :param exp_bias: exponent bias for data format (if applicable)
  :param q_type: data format choice (e.g., signed, unsigned, adaptive floating point)
  """

  # format into binary array according to data format
  x = torch.zeros(orig_flt.size()[0], int_bits+frac_bits, device=pt_device, dtype=torch.float32)
  current_ =  torch.zeros(orig_flt.size()[0], device=pt_device, dtype=torch.float32)
  xid = 0
  if q_type == 'afloat':
    sign, mant, exp, bias = get_q_afloat(orig_flt, int_bits+frac_bits, frac_bits, exp_bias) 
    mant_bits = int_bits-1
    x[:, 0] = sign
    xid = 1
    for mid in range(1, mant_bits+1):
      x[:, xid] = torch.sign(current_ + 0.5**(mid) - mant) <= 0
      current_ = current_ + 0.5**(mid)*x[:, xid]
      xid += 1
    
    current_ =  torch.zeros(orig_flt.size()[0], device=pt_device, dtype=torch.float32)
    for eid in list(reversed(range(frac_bits))):
      x[:, xid] = torch.sign(current_ + 2.**(eid) - exp) <= 0
      current_ = current_ + 2.**(eid)*x[:, xid]
      xid += 1
  else:
    if q_type == 'signed':
      x[:, 0] = torch.sign(orig_flt) < 0
      current_ = -1.*2**(int_bits-1)*x[:, 0]
      xid = 1
    for iid in list(reversed(range(int_bits-xid))):
      x[:, xid] = torch.sign(current_ + 2.**(iid) - orig_flt) <= 0
      current_ = current_ + 2.**(iid)*x[:, xid]
      xid += 1
    for fid in range(1, frac_bits+1):
      x[:, xid] = torch.sign(current_ + 0.5**(fid) - orig_flt) <= 0
      current_ = current_ + 0.5**(fid)*x[:, xid]
      xid += 1

  return x


def convert_mlc_mat(num_float, rep_conf, int_bits, frac_bits, exp_bias, q_type):
  """
  Format an entire input matrix into per-memory-cell array under MLC config for bit-level fault injection

  :param num_float: input value (floating point)
  :param rep_conf: mapping from number of bits in input value to number of levels per NVM storage cell (e.g., [2, 2] for a 2 bit input into SLCs)
  :param int_bits: number of integer bits for data format (if applicable)
  :param frac_bits: number of fractional bits for data format (if applicable)
  :param exp_bias: exponent bias for data format (if applicable)
  :param q_type: data format choice (e.g., signed, unsigned, adaptive floating point)
  """
  # format data into MLCs according to data format
  rep_conf_ = torch.from_numpy(rep_conf)
  x_bin = get_binary_array_mat(num_float, rep_conf_, int_bits, frac_bits, exp_bias, q_type)
  x_mlc = torch.zeros(num_float.size()[0], len(rep_conf), device=pt_device)
  idx = 0

  rep_conf = torch.tensor(rep_conf, dtype=torch.float32, device=pt_device)
  for i in range(len(rep_conf)):
    idx_end = idx + int(torch.log2(rep_conf[i]))
    x_mlc[:, i] = torch.sum(x_bin[:, idx:idx_end]*(2**(torch.arange(int(torch.log2(rep_conf[i])), 0, -1, device=pt_device, dtype=torch.float32)-1)), 1)
    idx = idx_end
  return x_mlc


def convert_f_mat(v_mlc, conf, int_bits, frac_bits, exp_bias, q_type):
  """
  Convert MLC-packed per-storage-cell values back to floating point values

  :param v_mlc: vector of per-storage-cell values (possible MLC encoding)
  :param conf: mapping from number of bits in input value to number of levels per NVM storage cell (e.g., [2, 2] for a 2 bit input into SLCs)
  :param int_bits: number of integer bits for data format (if applicable)
  :param frac_bits: number of fractional bits for data format (if applicable)
  :param exp_bias: exponent bias for data format (if applicable)
  :param q_type: data format choice (e.g., signed, unsigned, adaptive floating point)
  """
  current = torch.zeros(v_mlc.size()[0], device=pt_device, dtype = torch.float32)
  x = torch.zeros(v_mlc.size()[0], int_bits+frac_bits)
  
  idx = 0
  conf = torch.tensor(conf, dtype = torch.float32, device=pt_device)
  bin_lut = torch.tensor([[0., 0., 0., 0.], 
                          [0., 0., 0., 1.], 
                          [0., 0., 1., 0.], 
                          [0., 0., 1., 1.], 
                          [0., 1., 0., 0.], 
                          [0., 1., 0., 1.], 
                          [0., 1., 1., 0.], 
                          [0., 1., 1., 1.], 
                          [1., 0., 0., 0.], 
                          [1., 0., 0., 1.], 
                          [1., 0., 1., 0.], 
                          [1., 0., 1., 1.], 
                          [1., 1., 0., 0.], 
                          [1., 1., 0., 1.], 
                          [1., 1., 1., 0.], 
                          [1., 1., 1., 1.]]) 

  
  for i in range(len(conf)):
    idx_end = idx + int(torch.log2(conf[i]))
    x[:, idx:idx_end] = bin_lut[v_mlc[:, i].long(), (4-int(torch.log2(conf[i]))):]
    idx = idx_end
  xid = 0
  
  if q_type == 'afloat':
    mant_bits = int_bits-1
    is_valid = torch.tensor(x[:, 0] == 0, dtype = torch.float32, device = pt_device)
    sign = is_valid*2 - 1
    xid = 1
    mant = torch.zeros(v_mlc.size()[0], device=pt_device, dtype = torch.float32)
    for mid in range(1, mant_bits+1):
      is_valid = torch.tensor(x[:, xid] == 1, dtype = torch.float32, device = pt_device)
      mant = mant + (0.5**(mid))*is_valid
      xid += 1
    mant = mant + 1
    exp = torch.zeros(v_mlc.size()[0], device=pt_device, dtype = torch.float32)
    for eid in list(reversed(range(frac_bits))):
      is_valid = torch.tensor(x[:,xid] == 1, dtype = torch.float32, device = pt_device)
      exp = exp + (2.**(eid))*is_valid
      xid += 1
    power_exp = torch.exp2(exp+exp_bias) 
    current = sign*power_exp*mant

  else:
    if q_type == 'signed':
      is_valid = torch.tensor(x[:, 0] == 1, dtype = torch.float32, device = pt_device)
      current = current - (2.**(int_bits-1))*is_valid
      xid = 1
    for iid in list(reversed(range(int_bits-xid))):
      is_valid = torch.tensor(x[:, xid] == 1, dtype = torch.float32, device = pt_device)
      current = current + (2.**(iid))*is_valid
      xid += 1
    for fid in range(1, frac_bits+1):
      is_valid = torch.tensor(x[:, xid] == 1, dtype = torch.float32, device = pt_device)
      current = current + (0.5**(fid))*is_valid
      xid += 1
  #print(current)
  return current

