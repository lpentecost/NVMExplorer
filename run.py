import pickle
import json
import time
import os
import nvmexplorer_src.input_defs
import pandas as pd
import numpy as np
import math
import argparse
import sys
import subprocess
from nvmexplorer_src.eval_utils import *
from nvmexplorer_src.combine_csv import *
from data.workload_data.spec_inputs import *
from data.workload_data.graph_inputs import *
from data.workload_data.dnn_inputs import *
from nvmexplorer_src.traffic import *
from nvmexplorer_src.tentpoles import *


def load_spreadsheet_data(cell_type, output_path):
  """ Returns a pandas dataframe object containing data for a particular NVM technology
  specified by cell_type from the NVM spreadsheet

  :param cell_type: String indicating which NVM technology to use
  :type cyll_type: String
  :return: pandas dataframe object containing the spreadsheet data
  :rtype: pandas dataframe 
  """
  if (cell_type == 'STT'):
      temp_df = pd.read_pickle("{}/NVM_data/STTRAM_data.pkl".format(output_path))
  elif (cell_type == 'RRAM'):
      temp_df = pd.read_pickle("{}/NVM_data/RRAM_data.pkl".format(output_path))
  elif (cell_type == 'PCM'):
      temp_df = pd.read_pickle("{}/NVM_data/PCM_data.pkl".format(output_path))
  elif (cell_type == 'CTT'): #BIG CAVEAT not including MLC capacity / details at this time
      temp_df = pd.read_pickle("{}/NVM_data/CTT_data.pkl".format(output_path))
  elif (cell_type == 'FeFET'): #BIG CAVEAT not including MLC capacity / details at this time
      temp_df = pd.read_pickle("{}/NVM_data/FeFET_data.pkl".format(output_path))
  else: # default back to RRAM if somehow tech is not provided
      temp_df = pd.read_pickle("{}/NVM_data/RRAM_data.pkl".format(output_path))
  

  if (cell_type != 'SRAM'):
      temp_df.replace('', np.nan, inplace = True) # fill empty cells with NAN to make processing easier

  return temp_df


def run_nvsim_tentpoles(worst_output_path, best_output_path, log_dir, best_case_stdout_log, best_case_stderr_log, worst_case_stdout_log, worst_case_stderr_log, nvsim_path, best_case_cfg_path, worst_case_cfg_path, nvsim_best_case_input_cfg, nvsim_worst_case_input_cfg, output_dir):
  """ Returns NVSim output from simulating user-specified, tentpole-based memory arrays
  in parallel and pickles the output. NVSim is only run if pickles do not already
  exist

  :param worst_output_path: path for pickled output of worst-case NVSim output
  :type worst_output_path: String
  :param best_output_path: path for pickled output of best-case NVSim output
  :type best_output_path: String
  :param log_dir: directory containing log files from NVSim runs
  :type log_dir: String
  :param best_case_stdout_log: path to stdout from best-case NVSim run
  :type best_case_stdout_log: String
  :param best_case_stderr_log: path to stderr from best-case NVSim run
  :type best_case_stderr_log: String
  :param worst_case_stdout_log: path to stdout from worst-case NVSim run
  :type worst_case_stdout_log: String
  :param worst_case_stderr_log: path to stderr from worst-case NVSim run
  :type worst_case_stderr_log: String
  :param nvsim_path: path to NVSim version
  :type nvsim_path: String
  :param best_case_cfg_path: path to best-case cfg file for NVSim run
  :type best_case_cfg_path: String
  :param worst_case_cfg_path: path to worst-case cfg file for NVSim run
  :type worst_case_cfg_path: String
  :param nvsim_best_case_input_cfg: :class:`NVSimIntputConfig` object that was 
  used to create the best-case NVSim output 
  :type nvsim_best_case_input_cfg: :class:`NVSimIntputConfig`
  :param nvsim_worst_case_input_cfg: :class:`NVSimIntputConfig` object that was 
  used to create the worst-case NVSim output 
  :type nvsim_worst_case_input_cfg: :class:`NVSimIntputConfig`
  :param output_dir: path to output dir for pickled NVSim output
  :type output_dir: String
  :return: tuple of Strings pointing to NVSim output files for best- and worst-
  case runs
  :rtype: tuple of Strings
  """
  if not os.path.exists(worst_output_path) and not os.path.exists(best_output_path):
    if not os.path.exists(log_dir): 
        os.makedirs(log_dir)

    # NVSim execution in parallel 
    nvsim_processes = []

    with open(best_case_stdout_log, "w") as f_best_case:
      with open(best_case_stderr_log, "w") as f_best_case_error:
        p1 = subprocess.Popen([nvsim_path, best_case_cfg_path],  stdout=f_best_case, stderr=f_best_case_error)

    with open(worst_case_stdout_log, "w") as f_worst_case:
      with open(worst_case_stderr_log, "w") as f_worst_case_error:
        p2 = subprocess.Popen([nvsim_path, worst_case_cfg_path],  stdout=f_worst_case, stderr=f_worst_case_error)

    nvsim_processes.append(p1)
    nvsim_processes.append(p2)

    for proc in nvsim_processes:
        proc.wait()

    nvsim_best_case_output = nvmexplorer_src.input_defs.nvsim_interface.parse_nvsim_output(best_case_stdout_log, input_cfg=nvsim_best_case_input_cfg)
    nvsim_worst_case_output = nvmexplorer_src.input_defs.nvsim_interface.parse_nvsim_output(worst_case_stdout_log, input_cfg=nvsim_worst_case_input_cfg)

    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    pickle.dump(nvsim_best_case_output,open(best_output_path, 'wb'))
    pickle.dump(nvsim_worst_case_output,open(worst_output_path, 'wb'))
  
  # Output already exists - load the pickle(s)
  else:
    nvsim_best_case_output = pickle.load(open(best_output_path, 'rb')) 
    nvsim_worst_case_output = pickle.load(open(worst_output_path, 'rb')) 

  return nvsim_best_case_output, nvsim_worst_case_output

def run_nvsim(output_path, log_dir, stdout_log, stderr_log, nvsim_path, cfg_path, nvsim_input_cfg, output_dir):
  """ Returns NVSim output from simulating user-specified, tentpole-based memory arrays
  in parallel and pickles the output. NVSim is only run if pickles do not already
  exist

  :param worst_output_path: path for pickled output of worst-case NVSim output
  :type worst_output_path: String
  :param best_output_path: path for pickled output of best-case NVSim output
  :type best_output_path: String
  :param log_dir: directory containing log files from NVSim runs
  :type log_dir: String
  :param best_case_stdout_log: path to stdout from best-case NVSim run
  :type best_case_stdout_log: String
  :param best_case_stderr_log: path to stderr from best-case NVSim run
  :type best_case_stderr_log: String
  :param worst_case_stdout_log: path to stdout from worst-case NVSim run
  :type worst_case_stdout_log: String
  :param worst_case_stderr_log: path to stderr from worst-case NVSim run
  :type worst_case_stderr_log: String
  :param nvsim_path: path to NVSim version
  :type nvsim_path: String
  :param best_case_cfg_path: path to best-case cfg file for NVSim run
  :type best_case_cfg_path: String
  :param worst_case_cfg_path: path to worst-case cfg file for NVSim run
  :type worst_case_cfg_path: String
  :param nvsim_best_case_input_cfg: :class:`NVSimIntputConfig` object that was 
  used to create the best-case NVSim output 
  :type nvsim_best_case_input_cfg: :class:`NVSimIntputConfig`
  :param nvsim_worst_case_input_cfg: :class:`NVSimIntputConfig` object that was 
  used to create the worst-case NVSim output 
  :type nvsim_worst_case_input_cfg: :class:`NVSimIntputConfig`
  :param output_dir: path to output dir for pickled NVSim output
  :type output_dir: String
  :return: tuple of Strings pointing to NVSim output files for best- and worst-
  case runs
  :rtype: tuple of Strings
  """
  if not os.path.exists(output_path):
    nvsim_processes = []

    with open(stdout_log, "w") as f_out:
      with open(stderr_log, "w") as f_error:
        p1 = subprocess.Popen([nvsim_path, cfg_path],  stdout=f_out, stderr=f_error)

    nvsim_processes.append(p1)

    for proc in nvsim_processes:
      proc.wait()
    
    nvsim_output = nvmexplorer_src.input_defs.nvsim_interface.parse_nvsim_output(stdout_log, input_cfg=nvsim_input_cfg)
    if not os.path.exists(output_dir): 
      os.makedirs(output_dir)

    pickle.dump(nvsim_output,open(output_path, 'wb'))
  # Output already exists - load the pickle(s)
  else:
    nvsim_output = pickle.load(open(output_path, 'rb')) 

  return nvsim_output

## Initialize objects based on config file and run eval
if __name__ == '__main__':
  
  exp_name = "default"
  read_frequency = 100000
  read_size = 8
  write_frequency = 10
  write_size = 8
  working_set = 1
  cell_type = ["SRAM"]
  process_node = 22
  opt_target = ["ReadLatency"]
  word_width = 64
  capacity = 1
  bits_per_cell = [1]
  traffic = []
  nvsim_path = "nvmexplorer_src/nvsim/nvsim"
  output_path = "output"

  # Load config file
  with open(sys.argv[1]) as f:
      config = json.load(f)
 
  # Override default values of local variables if needed
  if "exp_name" in config["experiment"]:
      if config["experiment"]["exp_name"]:
          exp_name = config["experiment"]["exp_name"]
  if "read_frequency" in config["experiment"]:
      if config["experiment"]["read_frequency"]:
          read_frequency = config["experiment"]["read_frequency"]
  if "write_frequency" in config["experiment"]:
      if config["experiment"]["write_frequency"]:
          write_frequency = config["experiment"]["write_frequency"]
  if "read_size" in config["experiment"]:
      if config["experiment"]["read_size"]:
          read_size = config["experiment"]["read_size"]
  if "write_size" in config["experiment"]:
      if config["experiment"]["write_size"]:
          write_size = config["experiment"]["write_size"]
  if "working_set" in config["experiment"]:
      if config["experiment"]["working_set"]:
          working_set = config["experiment"]["working_set"]
  if "cell_type" in config["experiment"]:
      if config["experiment"]["cell_type"]:
          cell_type = config["experiment"]["cell_type"]
  if "process_node" in config["experiment"]:
      if config["experiment"]["process_node"]:
          process_node = config["experiment"]["process_node"]
  if "opt_target" in config["experiment"]:
      if config["experiment"]["opt_target"]:
          opt_target = config["experiment"]["opt_target"]
  if "word_width" in config["experiment"]:
      if config["experiment"]["word_width"]:
          word_width = config["experiment"]["word_width"]
  if "capacity" in config["experiment"]:
      if config["experiment"]["capacity"]:
          capacity = config["experiment"]["capacity"]
  if "bits_per_cell" in config["experiment"]:
      if config["experiment"]["bits_per_cell"]:
          bits_per_cell = config["experiment"]["bits_per_cell"]
  if "traffic" in config["experiment"]:
      if config["experiment"]["traffic"]:
          traffic = config["experiment"]["traffic"]
  if "nvsim_path" in config["experiment"]:
      if config["experiment"]["nvsim_path"]:
          nvsim_path = config["experiment"]["nvsim_path"]
  if "output_path" in config["experiment"]:
      if config["experiment"]["output_path"]:
          output_path = config["experiment"]["output_path"]
   
  print("Successfully Loaded Config File")
  
  # The main loop of NVMExplorer
  for _cell_type in cell_type:
      for _opt_target in opt_target:
          for _capacity in capacity:
              for _bits_per_cell in bits_per_cell:
                  access_pattern = nvmexplorer_src.input_defs.access_pattern.PatternConfig(exp_name = exp_name,
                      read_freq = read_frequency,
                      read_size = read_size,
                      write_freq = write_frequency,
                      write_size = write_size,
                      workingset = working_set)
                  
                  # Loads data from NVM database
                  data_df = load_spreadsheet_data(_cell_type, output_path)

                  # TODO: conditional for tentpole study or default values study
                  # Creates the tentpoles per technology
                  best_case_cell_path, worst_case_cell_path, best_case_cell_cfg, worst_case_cell_cfg = form_tentpoles(data_df, _cell_type, _bits_per_cell)

                  ## Define the paths
                  log_dir = "{}/logs".format(output_path) # This is where we'll store stdout and stderr for each NVSim run for debugging and/or post-processing purposes
                  output_dir = "{}/nvsim_output".format(output_path) # This is where we'll store the pickled results. In case we are doing a run that doesn't require re-running NVSim
                  if not os.path.exists(log_dir): 
                      os.makedirs(log_dir)
                  if not os.path.exists(output_dir): 
                      os.makedirs(output_dir)
                  if not os.path.exists("{}/results".format(output_path)): 
                      os.makedirs("{}/results".format(output_path))
                  if not os.path.exists("data/mem_cfgs"): 
                      os.makedirs("data/mem_cfgs")
                  best_case_cfg_path = "data/mem_cfgs/{}_{}MB_{}_{}BPC-optimized_best_case.cfg".format(_cell_type, _capacity, _opt_target, _bits_per_cell)
                  worst_case_cfg_path = "data/mem_cfgs/{}_{}MB_{}_{}BPC-optimized_worst_case.cfg".format(_cell_type, _capacity, _opt_target, _bits_per_cell)
                  best_case_stdout_log = "{}/logs/{}_{}MB_{}_{}BPC-optimized_best_case_output".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell)
                  best_case_stderr_log = "{}/logs/{}_{}MB_{}_{}BPC-optimized_best_case_error".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell)
                  worst_case_stdout_log = "{}/logs/{}_{}MB_{}_{}BPC-optimized_worst_case_output".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell)
                  worst_case_stderr_log = "{}/logs/{}_{}MB_{}_{}BPC-optimized_worst_case_error".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell)

                  ## Generate corresponding mem cfgs
                  nvsim_best_case_input_cfg = nvmexplorer_src.input_defs.nvsim_interface.NVSimInputConfig(mem_cfg_file_path = best_case_cfg_path, process_node = process_node,
                        opt_target = _opt_target,
                        word_width = word_width,
                        capacity = _capacity,
                        cell_type = best_case_cell_cfg)

                  nvsim_worst_case_input_cfg = nvmexplorer_src.input_defs.nvsim_interface.NVSimInputConfig(mem_cfg_file_path = worst_case_cfg_path, process_node = process_node,
                        opt_target = _opt_target,
                        word_width = word_width,
                        capacity = _capacity,
                        cell_type = worst_case_cell_cfg)

                  nvsim_worst_case_input_cfg.generate_mem_cfg()
                  nvsim_best_case_input_cfg.generate_mem_cfg()

                  worst_output_path = "{}/nvsim_output/{}_{}MB_{}_{}BPC_{}b-optimized_worst_case_nvsim_output.pkl".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, word_width)
                  best_output_path = "{}/nvsim_output/{}_{}MB_{}_{}BPC_{}b-optimized_best_case_nvsim_output.pkl".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, word_width)
                      
                  # Runs modified nvsim on tentpoles
                  nvsim_best_case_output, nvsim_worst_case_output = run_nvsim_tentpoles(worst_output_path, best_output_path, log_dir, best_case_stdout_log, best_case_stderr_log, worst_case_stdout_log, worst_case_stderr_log, nvsim_path, best_case_cfg_path, worst_case_cfg_path, nvsim_best_case_input_cfg, nvsim_worst_case_input_cfg, output_dir)
                      
                  # Report results, add cell config params, mem config params, and whatever we are sweeping to the header
                  results_csv = "{}/results/{}_{}MB_{}_{}BPC-{}.csv".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, exp_name)
                      
                  if os.path.exists(results_csv):
                      os.remove(results_csv)

                  worst_case_result = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
                  best_case_result = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
                      
                  worst_case_result.evaluate()
                  best_case_result.evaluate()
 
                  print("Retrieved Array-Level Results; Running Analytical Model")
                     
                  # Run application-level sweeps and save results
                  #FIXME also add conditional for customized traffic inputs
                  if len(traffic) > 0:
                      # First function call prints header to the spreadsheet, second one prints to csv. Only need to report the header once
                      best_case_result.report_header_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path) 
                          
                      if "generic" in traffic:
                          # GENERIC traffic sweep; report all outputs  
                          generic_traffic(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path)
                              
                      if "graph" in traffic:
                          # Graph traffic sweep
                          graph_traffic(graph8MB, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path)

                      if "dnn" in traffic:
                          # DNN traffic sweep
                          dnn_traffic(DNN_weights, DNN_weights_acts, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path)

                      if "spec" in traffic:
                          # SPEC2017 traffic
                          spec_traffic(spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path)

                      if "generic_write_buff" in traffic:
                          #next, run generic traffic with write buffer proxy
                          generic_traffic_with_write_buff(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path)
      
      combine_csv(_cell_type, _bits_per_cell)
      print("Reported Results; Evaluation Complete")
