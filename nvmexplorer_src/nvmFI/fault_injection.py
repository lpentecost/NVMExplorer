import numpy as np
import torch
import random
import scipy.stats as ss
import pickle
import sys
import time
import cProfile, pstats
from .fi_utils import *
from .fi_config import *
from .data_transforms import *

def mat_fi(mat, seed=0, int_bits=2, frac_bits=6, rep_conf = np.array([2, 2, 2, 2, 2, 2, 2, 2]), q_type = 'signed', encode = 'dense'):
  """ Single fault injection experiment for an input matrix with provided quantization, datatype, optional envocing per value to MLCs, and optional sparse encoding


  :param mat: input matrix (can be 1,2,N-dimensional; will be flattened into NVM storage)
  :param seed: random seed for use in fault modeling
  :param int_bits: number of integer bits per value in data format (if applicable)
  :param frac_bits: number of fractional or decimal bits per value in data format (if applicable)
  :param rep_conf: array of number of levels per cell used for storage per data value (SLC default would be np.array([2, 2, 2, 2, 2, 2, 2, 2]) for 8-bit datatype, for example)
  :param q_type: datatype specification (e.g., signed or unsigned, or AdaptivFloat)
  :param encode: indicate whether the data should be mapped into NVM using a sparse encoding (e.g., bitmask) or in standard format (dense)
  """
    
  np.random.seed(seed)
  
  error_map = get_error_map(max(rep_conf))

  shape = mat.shape

  flattened_mat = torch.from_numpy(mat).view(-1).float()
  if pt_device == "cuda":
    flattened_mat = flattened_mat.to(torch.device(pt_device))
  exp_bias = 0
  if q_type == 'afloat': #support for adaptive float
    exp_bias = get_afloat_bias(abs(flattened_mat), frac_bits)

  if encode == 'dense': #no sparse encoding, just inject on dense weight matrix
    mlc_values = torch.zeros((flattened_mat.size()[0], rep_conf.size), device=pt_device, dtype=torch.float32)
    mlc_values = convert_mlc_mat(flattened_mat, rep_conf, int_bits, frac_bits, exp_bias, q_type)
    mlc_values = inject_faults(mlc_values, rep_conf, error_map)
    flattened_mat = convert_f_mat(mlc_values, rep_conf, int_bits, frac_bits, exp_bias, q_type)
  elif encode == 'bitmask': #encode data with bitmask FIXME assumed bitmask always stored with SLC and inject on bitmask and non-zero data
    bitmask, data = to_bitmask(flattened_mat)
    #optional check capcity of encoded version
    #print(encoded_capacity(bitmask, data, int_bits+frac_bits)/8.0/1024.0, "KB")
    #set up and inject weights
    mlc_values=torch.zeros((data.size()[0], rep_conf.size), device=pt_device, dtype=torch.float32)
    mlc_values=convert_mlc_mat(data, rep_conf, int_bits, frac_bits, exp_bias, q_type)
    mlc_values = inject_faults(mlc_values, rep_conf, error_map)
    data = convert_f_mat(mlc_values, rep_conf, int_bits, frac_bits, exp_bias, q_type)
    #set up and inject bitmask
    mlc_bitmask=convert_mlc_mat(bitmask, np.array([2]), 1, 0, 0, 'unsigned')
    mlc_bitmask = inject_faults(mlc_bitmask, np.array([2]), error_map)
    bitmask = convert_f_mat(mlc_bitmask, np.array([2]), 1, 0, 0, 'unsigned')
    #decode
    flattened_mat = from_bitmask(bitmask, data)

  mat = np.reshape(flattened_mat.cpu().data.numpy(), shape)

  return mat

def dnn_fi(model, seed=0, int_bits=2, frac_bits=6, rep_conf = np.array([2, 2, 2, 2, 2, 2, 2, 2]), q_type = 'signed', encode = 'dense'):
  """ Single fault injection experiment for an input DNN model with provided quantization, datatype, optional envocing per value to MLCs, and optional sparse encoding


  :param model: input dnn model (injection on all weights across entire test set by default)
  :param seed: random seed for use in fault modeling
  :param int_bits: number of integer bits per value in data format (if applicable)
  :param frac_bits: number of fractional or decimal bits per value in data format (if applicable)
  :param rep_conf: array of number of levels per cell used for storage per data value (SLC default would be np.array([2, 2, 2, 2, 2, 2, 2, 2]) for 8-bit datatype, for example)
  :param q_type: datatype specification (e.g., signed or unsigned, or AdaptivFloat)
  :param encode: indicate whether the data should be mapped into NVM using a sparse encoding (e.g., bitmask) or in standard format (dense)
  """ 
  np.random.seed(seed)
  
  error_map = get_error_map(max(rep_conf))
  for name, weights in model.named_parameters():
    w = weights.data
    flattened_weights = w.view(-1)
      
    exp_bias = 0
    if q_type == 'afloat': #support for adaptive float
      exp_bias = get_afloat_bias(abs(flattened_weights), frac_bits)

    if encode == 'dense': #no sparse encoding, just inject on dense weight matrix
      mlc_weights=torch.zeros((flattened_weights.size()[0], rep_conf.size), device=pt_device, dtype=torch.float32)
      mlc_weights=convert_mlc_mat(flattened_weights, rep_conf, int_bits, frac_bits, exp_bias, q_type)
      mlc_weights = inject_faults(mlc_weights, rep_conf, error_map)
      flattened_weights = convert_f_mat(mlc_weights, rep_conf, int_bits, frac_bits, exp_bias, q_type)
      model.state_dict()[name].data.copy_(flattened_weights.view(w.size()))
    elif encode == 'bitmask': #encode data with bitmask FIXME assumed bitmask always stored with SLC and inject on bitmask and non-zero data
      bitmask, data = to_bitmask(flattened_weights)
      #optional check capcity of encoded version
      #print(encoded_capacity(bitmask, data, int_bits+frac_bits)/8.0/1024.0, "KB")
      #set up and inject weights
      mlc_weights=torch.zeros((data.size()[0], rep_conf.size), device=pt_device, dtype=torch.float32)
      mlc_weights=convert_mlc_mat(data, rep_conf, int_bits, frac_bits, exp_bias, q_type)
      mlc_weights = inject_faults(mlc_weights, rep_conf, error_map)
      data = convert_f_mat(mlc_weights, rep_conf, int_bits, frac_bits, exp_bias, q_type)
      #set up and inject bitmask
      mlc_bitmask=convert_mlc_mat(bitmask, np.array([2]), 1, 0, 0, 'unsigned')
      mlc_bitmask = inject_faults(mlc_bitmask, np.array([2]), error_map)
      bitmask = convert_f_mat(mlc_bitmask, np.array([2]), 1, 0, 0, 'unsigned')
      #decode
      flattened_weights = from_bitmask(bitmask, data)
      model.state_dict()[name].data.copy_(flattened_weights.view(w.size()))
        
  return model

