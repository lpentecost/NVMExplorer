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
  elif (cell_type == 'eDRAM'):
      pass
  else: # default back to RRAM if somehow tech is not provided
      temp_df = pd.read_pickle("{}/NVM_data/RRAM_data.pkl".format(output_path))
  

  if (cell_type != 'SRAM'):
      temp_df.replace('', np.nan, inplace = True) # fill empty cells with NAN to make processing easier

  return temp_df


def set_sim_input_config(simulator, cfg_path, process_node, _opt_target, word_width, device_roadmap, _capacity, banks, _stacked_die_count, _monolithic_layer_count, _temperature, cell_cfg):
  """ Returns best-case and worst-case input configs for either DESTINY or NVSim based
  on user configuration

  :param simulator: which simulator is used (destiny or nvsim)
  :type simulator: String
  :param cfg_path: path to cell config file
  :type cfg_path: String
  :param process_node: the process node for the memory under question
  :type process_node: Int
  :param _opt_target: the optimization target to be used with the simulator
  :type _opt_target: String
  :param word_width: the word width used for the memory under question in bytes 
  :type word_width: Int
  :param _capacity: the memory capacity in MB
  :type _capacity: Int
  :param cell_cfg: Cell config file to be used with the NVM simulator
  :type cell_cfg: :NVSimCellConfig:
  :return: best-case and worst-case input configs to be run under the NVM simulator
  :rtype: :NVSimInputConfig: or :DestinyInputConfig:
  """
  if simulator == "destiny":
      sim_input_cfg = nvmexplorer_src.input_defs.destiny_interface.DestinyInputConfig(mem_cfg_file_path = cfg_path, process_node = process_node,
                                       opt_target = _opt_target,
                                       word_width = word_width,
                                       device_roadmap = device_roadmap,
                                       retention_time = retention_time,
                                       capacity = _capacity,
                                       stacked_die_count = _stacked_die_count,
                                       monolithic_layer_count = _monolithic_layer_count,
                                       cell_type = cell_cfg)

  elif simulator == "cryomem":
      sim_input_cfg = nvmexplorer_src.input_defs.cryomem_interface.CryoMEMInputConfig(mem_cfg_file_path = cfg_path, process_node = process_node,
                                       capacity = _capacity,
                                       word_width = word_width,
                                       banks = banks,
                                       temperature = _temperature,
                                       cell_type = cell_cfg)
  else: # nvsim
      sim_input_cfg = nvmexplorer_src.input_defs.nvsim_interface.NVSimInputConfig(mem_cfg_file_path = cfg_path, process_node = process_node,
                                       opt_target = _opt_target,
                                       word_width = word_width,
                                       capacity = _capacity,
                                       cell_type = cell_cfg)

  return sim_input_cfg

def run_sim_wrapper(simulator, output_paths, log_dir, stdout_logs, stderr_logs, nvsim_path, destiny_path, cryomem_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, temperature, output_dir):
  """ Wrapper for the run_sim() function

  :param simulator: which simulator is used (destiny or nvsim)
  :type simulator: String
  :param output_paths: paths for pickled outputs
  :type output_paths: Array of Strings
  :param log_dir: directory containing log files from NVSim runs
  :type log_dir: String
  :param stdout_logs: paths to stdout from NVSim runs
  :type stdout_logs: Array of Strings
  :param stderr_logs: paths to stderr from NVSim runs
  :type stderr_logs: Array of Strings
  :param nvsim_path: path to NVSim version
  :type nvsim_path: String
  :param cfg_paths: paths to cfg files for NVSim run
  :type cfg_paths: Array of Strings
  :param sim_input_cfgs: Array of :class:`NVSimIntputConfig` object that were 
  used to create the NVSim outputs
  :type sim_input_cfgs: Array of :class:`NVSimIntputConfig` or :class:`DestinyIntputConfig`
  :param output_dir: path to output dir for pickled NVSim output
  :type output_dir: String
  :return: Array of Strings pointing to NVSim output files
  :rtype: Array of Strings
  """

  if simulator == "destiny":
      sim_outputs = run_sim(simulator, output_paths, log_dir, stdout_logs, stderr_logs, destiny_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, temperature, output_dir)
  elif simulator == "cryomem":
      sim_outputs = run_sim(simulator, output_paths, log_dir, stdout_logs, stderr_logs, cryomem_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, temperature, output_dir)
  else: #nvsim
      sim_outputs = run_sim(simulator, output_paths, log_dir, stdout_logs, stderr_logs, nvsim_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, temperature, output_dir)

  return sim_outputs


def run_sim(simulator, output_paths, log_dir, stdout_logs, stderr_logs, sim_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, temperature, output_dir):
  """ Returns NVSim or DESTINY output from simulating user-specified cell definitions
  in parallel and pickles the output. NVSim is only run if pickles do not already
  exist

  :param simulator: which simulator is used (destiny or nvsim)
  :type simulator: String
  :param output_paths: paths for pickled outputs
  :type output_paths: Array of Strings
  :param log_dir: directory containing log files from NVSim runs
  :type log_dir: String
  :param stdout_logs: paths to stdout from NVSim runs
  :type stdout_logs: Array of Strings
  :param stderr_logs: paths to stderr from NVSim runs
  :type stderr_logs: Array of Strings
  :param nvsim_path: path to NVSim version
  :type nvsim_path: String
  :param cfg_paths: paths to cfg files for NVSim run
  :type cfg_paths: Array of Strings
  :param sim_input_cfgs: Array of :class:`NVSimIntputConfig` object that were 
  used to create the NVSim outputs
  :type sim_input_cfgs: Array of :class:`NVSimIntputConfig` or :class:`DestinyIntputConfig`
  :param output_dir: path to output dir for pickled NVSim output
  :type output_dir: String
  :return: Array of Strings pointing to NVSim output files
  :rtype: Array of Strings
  """
  for i in range(len(output_paths)):
    sim_processes = []

    if not os.path.exists(output_paths[i]): 
      with open(stdout_logs[i], "w") as f_out:
        with open(stderr_logs[i], "w") as f_error:
          if simulator == "cryomem":
            p1 = subprocess.Popen(["python3.8 {} {} {}".format(sim_path, cfg_paths[i], extra_cryomem_args[i])], stdout=f_out, stderr=f_error, shell=True)
          else:
            p1 = subprocess.Popen([sim_path, cfg_paths[i]],  stdout=f_out, stderr=f_error)
          p1.wait()


      #nvsim_processes.append(p1)

  #for proc in nvsim_processes:
  #  proc.wait()
  
  sim_outputs = []
  for i in range(len(output_paths)):
    if simulator == "destiny":
      sim_output = nvmexplorer_src.input_defs.destiny_interface.parse_destiny_output(stdout_logs[i], input_cfg=sim_input_cfgs[i])
    elif simulator == "cryomem":
      sim_output = nvmexplorer_src.input_defs.cryomem_interface.parse_cryomem_output(stdout_logs[i], input_cfg=sim_input_cfgs[i])
    else:
      sim_output = nvmexplorer_src.input_defs.nvsim_interface.parse_nvsim_output(stdout_logs[i], input_cfg=sim_input_cfgs[i])
    if not os.path.exists(output_dir): 
      os.makedirs(output_dir)
    sim_outputs.append(sim_output)
    pickle.dump(sim_output,open(output_paths[i], 'wb'))
    # Output already exists - load the pickle(s)
    #else:
    #  sim_output = pickle.load(open(output_paths[i], 'rb')) 
    #  sim_outputs.append(sim_output)

  return sim_outputs

## Initialize objects based on config file and run eval
if __name__ == '__main__':
  
  exp_name = "default"
  read_frequency = 100000
  read_size = 8
  write_frequency = 10
  write_size = 8
  working_set = 1
  cell_type = ["SRAM"]
  device_roadmap = "LOP"
  retention_time = 40
  process_node = 22
  opt_target = ["ReadLatency"]
  word_width = 64
  capacity = 1
  banks = [1]
  bits_per_cell = [1]
  stacked_die_count = [1]
  monolithic_layer_count = [1]
  temperature = [350]
  traffic = ["generic"]
  nvsim_path = "nvmexplorer_src/nvsim/nvsim"
  destiny_path = "../destiny/destiny"
  cryomem_path = "../CryoModel/CryoMEM/run.py"
  output_path = "output"
  cell_tentpoles = True #by default, run a "tentpole" style study

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
  if "device_roadmap" in config["experiment"]:
      if config["experiment"]["device_roadmap"]:
          device_roadmap = config["experiment"]["device_roadmap"]
  if "retention_time" in config["experiment"]:
      if config["experiment"]["retention_time"]:
          retention_time = config["experiment"]["retention_time"]
  if "bits_per_cell" in config["experiment"]:
      if config["experiment"]["bits_per_cell"]:
          bits_per_cell = config["experiment"]["bits_per_cell"]
  if "stacked_die_count" in config["experiment"]:
      if config["experiment"]["stacked_die_count"]:
          stacked_die_count = config["experiment"]["stacked_die_count"]
  if "monolithic_layer_count" in config["experiment"]:
      if config["experiment"]["monolithic_layer_count"]:
          monolithic_layer_count = config["experiment"]["monolithic_layer_count"]
  if "temperature" in config["experiment"]:
      if config["experiment"]["temperature"]:
          temperature = config["experiment"]["temperature"]
  if "traffic" in config["experiment"]:
      if config["experiment"]["traffic"]:
          traffic = config["experiment"]["traffic"]
  if "banks" in config["experiment"]:
      if config["experiment"]["banks"]:
          banks = config["experiment"]["banks"]
  if "simulator" in config["experiment"]:
      if config["experiment"]["simulator"]:
          simulator = config["experiment"]["simulator"]
  if "nvsim_path" in config["experiment"]:
      if config["experiment"]["nvsim_path"]:
          nvsim_path = config["experiment"]["nvsim_path"]
  if "destiny_path" in config["experiment"]:
      if config["experiment"]["destiny_path"]:
          destiny_path = config["experiment"]["destiny_path"]
  if "cryomem_path" in config["experiment"]:
      if config["experiment"]["cryomem_path"]:
          cryomem_path = config["experiment"]["cryomem_path"]
  if "output_path" in config["experiment"]:
      if config["experiment"]["output_path"]:
          output_path = config["experiment"]["output_path"]
  if "custom_cells" in config["experiment"]:
      cell_tentpoles = False
   
  print("Successfully Loaded Config File")
  
  # The main loop of NVMExplorer
  for _cell_type in cell_type:
      for _process_node in process_node:
          for _opt_target in opt_target:
              for _capacity in capacity:
                  for _banks in banks:
                      for _bits_per_cell in bits_per_cell:
                          for _stacked_die_count in stacked_die_count:
                              for _monolithic_layer_count in monolithic_layer_count:
                                  for _temperature in temperature:
                                      access_pattern = nvmexplorer_src.input_defs.access_pattern.PatternConfig(exp_name = exp_name,
                                          read_freq = read_frequency,
                                          read_size = read_size,
                                          write_freq = write_frequency,
                                          write_size = write_size,
                                          workingset = working_set)
                                      
                                      # Loads data from NVM database
                                      if _cell_type != "eDRAM":
                                          data_df = load_spreadsheet_data(_cell_type, output_path)
                                          
                                      ## Define the paths
                                      log_dir = "{}/logs".format(output_path) # This is where we'll store stdout and stderr for each NVSim run for debugging and/or post-processing purposes
                                      output_dir = "{}/sim_output".format(output_path) # This is where we'll store the pickled results. In case we are doing a run that doesn't require re-running NVSim
                                      if not os.path.exists(log_dir): 
                                          os.makedirs(log_dir)
                                      if not os.path.exists(output_dir): 
                                          os.makedirs(output_dir)
                                      if not os.path.exists("{}/results".format(output_path)): 
                                          os.makedirs("{}/results".format(output_path))
                                      if not os.path.exists("data/mem_cfgs"): 
                                          os.makedirs("data/mem_cfgs")

                                      results_csv = "{}/results/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}-{}.csv".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, simulator, exp_name)    
                                      if os.path.exists(results_csv):
                                          os.remove(results_csv)


                                      if (cell_tentpoles == True): #set up default, tentpole-style study per cell type
                                          # Creates the tentpoles per technology
                                          best_case_cell_path, worst_case_cell_path, best_case_cell_cfg, worst_case_cell_cfg = form_tentpoles(data_df, _cell_type, _bits_per_cell)

                                          best_case_cfg_path = "data/mem_cfgs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-best_case.cfg".format(_cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)
                                          worst_case_cfg_path = "data/mem_cfgs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-worst_case.cfg".format(_cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)
                                          best_case_stdout_log = "{}/logs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-best_case_output".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)
                                          best_case_stderr_log = "{}/logs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-best_case_error".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)
                                          worst_case_stdout_log = "{}/logs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-worst_case_output".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)
                                          worst_case_stderr_log = "{}/logs/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K-worst_case_error".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature)

                                          ## Generate corresponding mem cfgs
                                          sim_best_case_input_cfg = set_sim_input_config(simulator, best_case_cfg_path, _process_node, _opt_target, word_width, device_roadmap, _capacity, _banks, _stacked_die_count, _monolithic_layer_count, _temperature, best_case_cell_cfg)
                                          sim_worst_case_input_cfg = set_sim_input_config(simulator, worst_case_cfg_path, _process_node, _opt_target, word_width, device_roadmap, _capacity, _banks, _stacked_die_count, _monolithic_layer_count, _temperature, worst_case_cell_cfg)
                                          sim_worst_case_input_cfg.generate_mem_cfg()
                                          sim_best_case_input_cfg.generate_mem_cfg()

                                          worst_output_path = "{}/sim_output/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}b-worst_case_sim_output.pkl".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, word_width)
                                          best_output_path = "{}/sim_output/{}_{}MB_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}b-best_case_sim_output.pkl".format(output_path, _cell_type, _capacity, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, word_width)
                                          #group paths to be compatible with run_nvsim parallelism
                                          cell_paths = [worst_case_cell_path, best_case_cell_path]
                                          cell_cfgs = [worst_case_cell_cfg, best_case_cell_cfg]
                                          output_paths = [worst_output_path, best_output_path]
                                          stdout_logs = [worst_case_stdout_log, best_case_stdout_log]
                                          stderr_logs = [worst_case_stderr_log, best_case_stderr_log]
                                          cfg_paths = [worst_case_cfg_path, best_case_cfg_path]
                                          sim_input_cfgs = [sim_worst_case_input_cfg, sim_best_case_input_cfg]
                                      else: #initialize cell configs according to input over-rides or default settings
                                          cell_paths = []
                                          cell_cfgs = []
                                          output_paths = []
                                          stdout_logs = []
                                          stderr_logs = []
                                          cfg_paths = []
                                          sim_input_cfgs = []
                                          extra_cryomem_args = []

                                          if len(config["custom_cells"]) == 0: #use default values per technology
                                            extra_args = "{} {} 1 0.4 {} cache".format(_temperature, _process_node, 1024*1024*_capacity) # for cryomem only; use cacti config corresponding to cell type
                                            this_cell_path, this_cell_cfg = gen_custom_cell(_cell_type, {"name":"default", "bits_per_cell":_bits_per_cell}, simulator)
                                            this_cfg_path = "data/mem_cfgs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}.cfg".format(_cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, "default")
                                            sim_input_cfg = set_sim_input_config(simulator, this_cfg_path, _process_node, _opt_target, word_width, device_roadmap, _capacity, _banks, _stacked_die_count, _monolithic_layer_count, _temperature, this_cell_cfg)
                                            sim_input_cfg.generate_mem_cfg()
                                            #assign paths for default cell
                                            cell_paths.append(this_cell_path)
                                            cell_cfgs.append(this_cell_cfg)
                                            cfg_paths.append(this_cfg_path)
                                            sim_input_cfgs.append(sim_input_cfg)
                                            extra_cryomem_args.append(extra_args)
                                            output_paths.append("{}/sim_output/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}b_{}_{}_output.pkl".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, word_width, "default", simulator))
                                            stdout_logs.append("{}/logs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}_output".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, "default"))
                                            stderr_logs.append("{}/logs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}_error".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, "default"))
                                          else:
                                            for i in range(len(config["custom_cells"])):
                                              this_custom_cell_input = config["custom_cells"][i]
                                              #if no name, assign a unique one
                                              if this_custom_cell_input["cell_type"] == _cell_type:
                                                if not "name" in this_custom_cell_input:
                                                  this_custom_cell_input["name"] = "custom"+_cell_type+str(i)
                                                this_cell_path, this_cell_cfg = gen_custom_cell(_cell_type, this_custom_cell_input, simulator)
                                                this_cfg_path = "data/mem_cfgs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}K_{}.cfg".format(_cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, _temperature, this_custom_cell_input["name"])
                                                sim_input_cfg = set_sim_input_config(simulator, this_cfg_path, _process_node, _opt_target, word_width, device_roadmap, _capacity, _banks, _stacked_die_count, _monolithic_layer_count, _temperature, this_cell_cfg)

                                                sim_input_cfg.generate_mem_cfg()
                                                #assign paths for custom cell
                                                cell_paths.append(this_cell_path)
                                                cell_cfgs.append(this_cell_cfg)
                                                cfg_paths.append(this_cfg_path)
                                                sim_input_cfgs.append(sim_input_cfg)
                                                output_paths.append("{}/sim_output/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}b_{}_{}_output.pkl".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, word_width, this_custom_cell_input["name"], simulator))
                                                stdout_logs.append("{}/logs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}_output".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, this_custom_cell_input["name"]))
                                                stderr_logs.append("{}/logs/{}_{}MB_{}banks_{}_{}BPC_{}nm_{}stackeddies_{}monolithiclayers_{}_error".format(output_path, _cell_type, _capacity, _banks, _opt_target, _bits_per_cell, _process_node, _stacked_die_count, _monolithic_layer_count, this_custom_cell_input["name"]))

                                      # Run modified nvsim or destiny on cell configs
                                      sim_outputs = run_sim_wrapper(simulator, output_paths, log_dir, stdout_logs, stderr_logs, nvsim_path, destiny_path, cryomem_path, cfg_paths, sim_input_cfgs, extra_cryomem_args, _temperature, output_dir)
                                      
                                      # Report results, add cell config params, mem config params, and whatever we are sweeping to the header
                                      for i in range(len(sim_outputs)):
                                          result = ExperimentResult(access_pattern, sim_input_cfgs[i], sim_outputs[i])
                                          result.evaluate() 
 
                                          print("Retrieved Array-Level Results; Running Analytical Model")
                                         
                                          # Run application-level sweeps and save results
                                          #FIXME also add conditional for customized traffic inputs
                                          if len(traffic) > 0:
                                              # First function call prints header to the spreadsheet, second one prints to csv. Only need to report the header once
                                              result.report_header_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], simulator) 
                                              
                                              if "generic" in traffic:
                                                  # GENERIC traffic sweep; report all outputs  
                                                  generic_traffic(access_pattern, sim_input_cfgs, sim_outputs, results_csv, cell_paths, cfg_paths, simulator)
                                                  
                                              if "graph" in traffic:
                                                  # Graph traffic sweep
                                                  graph_traffic(graph8MB, access_pattern, sim_input_cfgs, sim_outputs, results_csv, cell_paths, cfg_paths, simulator)

                                              if "dnn" in traffic:
                                                  # DNN traffic sweep
                                                  dnn_traffic(DNN_weights, DNN_weights_acts, access_pattern, sim_input_cfgs, sim_outputs, results_csv, cell_paths, cfg_paths, simulator)

                                              if "spec" in traffic:
                                                  # SPEC2017 traffic
                                                  spec_traffic(spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC, access_pattern, sim_input_cfgs, sim_outputs, results_csv, cell_paths, cfg_paths, simulator)

                                              if "generic_write_buff" in traffic:
                                                  #next, run generic traffic with write buffer proxy
                                                  generic_traffic_with_write_buff(access_pattern, sim_input_cfgs, sim_outputs, results_csv, cell_paths, cfg_paths, simulator)
              
      combine_csv(_cell_type, _bits_per_cell, simulator, exp_name)
      print("Reported Results; Evaluation Complete")
