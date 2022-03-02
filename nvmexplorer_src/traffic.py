from data.workload_data.spec_inputs import *
from data.workload_data.graph_inputs import *
from data.workload_data.dnn_inputs import *
from nvmexplorer_src.eval_utils import *


def generic_traffic(access_pattern, nvsim_input_cfgs, nvsim_outputs, results_csv, cell_paths, cfg_paths, simulator):
  """  Evaluates and writes results for scenarios from apre-set, generic traffic sweep

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_input_cfgs: :class:`NVSimInputConfig` objects which were used for array simulation
  :param nvsim_outputs: paths to NVSim output files
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param cell_paths: paths to NVSim input cell files
  :param cfg_paths: paths to NVSim input config files
  """
  # this is a helper function to use existing, arbitrary range of traffic pattern inputs
  write_accesses = [0, 1, 2, 1e1, 2e1, 1e2, 2e2, 1e3, 2e3, 1e4, 2e4, 1e5, 2e5, 1e6, 2e6, 1e7]
  read_accesses = [0, 1, 2, 1e1, 2e1, 1e2, 2e2, 1e3, 2e3, 1e4, 2e4, 1e5, 2e5, 1e6, 2e6, 1e7, 2e7, 1e8, 2e8, 1e9, 2e9, 1e10]
  for wr in write_accesses:
    for rd in read_accesses:
      access_pattern.write_freq = wr
      access_pattern.read_freq = rd
      for i in range(len(cell_paths)):
          this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
          this_result.evaluate()
          # These print to csv
          this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)


def graph_traffic(graph8MB, access_pattern, nvsim_input_cfgs, nvsim_outputs, results_csv, cell_paths, cfg_paths, simulator):
  """  Evaluates and writes results for scenarios from a graph application traffic sweep

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_input_cfgs: :class:`NVSimInputConfig` objects which were used for array simulation
  :param nvsim_outputs: paths to NVSim output files
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param cell_paths: paths to NVSim input cell files
  :param cfg_paths: paths to NVSim input config files
  """
  # this is a helper function to use existing graph workload template inputs
  for (i, name) in enumerate(graph8MB["names"]):
      access_pattern.benchmark_name = name
      if (graph8MB["read_freq"][i] > 0):
        access_pattern.name = name
        access_pattern.write_freq = graph8MB["write_freq"][i] 
        access_pattern.read_freq = graph8MB["read_freq"][i]
        for i in range(len(cell_paths)):
            this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
            this_result.evaluate()
            # These print to csv
            this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)
  

def dnn_traffic(DNN_weights, DNN_weights_acts, access_pattern, nvsim_input_cfgs, nvsim_outputs, results_csv, cell_paths, cfg_paths, simulator):
  """  Evaluates and writes results for scenarios from a dnn application traffic sweep

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_input_cfgs: :class:`NVSimInputConfig` objects which were used for array simulation
  :param nvsim_outputs: paths to NVSim output files
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param cell_paths: paths to NVSim input cell files
  :param cfg_paths: paths to NVSim input config files
  """
  # this is a helper function to use existing dnn workload template inputs
  dnns = [ DNN_weights, DNN_weights_acts ]
  for dnn in dnns:
    for (i, name) in enumerate(dnn["names"]):
      access_pattern.benchmark_name = name
      if (dnn["reads"][i] > 0):
        access_pattern.name = name
        access_pattern.read_freq = dnn["reads"][i] * dnn["ips"][i]
        access_pattern.write_freq = dnn["writes"][i] * dnn["ips"][i]
        for i in range(len(cell_paths)):
            this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
            this_result.evaluate()
            # These print to csv
            this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)


def spec_traffic(spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC, access_pattern, nvsim_input_cfgs, nvsim_outputs, results_csv, cell_paths, cfg_paths, simulator):
  """  Evaluates and writes results for scenarios from SPEC2017 Cache Profiling traffic sweep

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_input_cfgs: :class:`NVSimInputConfig` objects which were used for array simulation
  :param nvsim_outputs: paths to NVSim output files
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param cell_paths: paths to NVSim input cell files
  :param cfg_paths: paths to NVSim input config files
  """
  # this is a helper function to use existing SPEC2017 benchmark template inputs
  for benchmark in [spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC]:
    for (i, name) in enumerate(benchmark["names"]):  
      access_pattern.benchmark_name = name
      if (benchmark["reads"][i] > 0):
        access_pattern.name = name
        access_pattern.write_freq = benchmark["writes"][i] / benchmark["ex_time"][i]
        access_pattern.read_freq = benchmark["reads"][i] / benchmark["ex_time"][i]
        for i in range(len(cell_paths)):
            this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
            this_result.evaluate()
            # These print to csv
            this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)

def generic_traffic_with_write_buff(access_pattern, nvsim_input_cfgs, nvsim_outputs, results_csv, cell_paths, cfg_paths, simulator):
  """  Evaluates and writes results for pre-defined case study scenarios from a generic application traffic sweep with write buffering that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_input_cfgs: :class:`NVSimInputConfig` objects which were used for array simulation
  :param nvsim_outputs: paths to NVSim output files
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param cell_paths: paths to NVSim input cell files
  :param cfg_paths: paths to NVSim input config files
  """
  rd_base_spec = 3.7e6 #geomean of SPEC CPU2017 16MB cache accesses
  wr_base_spec = 2.3e6 #geomean of SPEC CPU2017
  rd_base_graph = 4.2e7 # FB BFS
  wr_base_graph = 1.9e5 # FB BFS

  percent_write_traffic_reduction = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1.0]
  percent_write_latency_mask = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1.0]

  for pct_traffic in percent_write_traffic_reduction:
    for pct_mask in percent_write_latency_mask:
      for i in range(len(cell_paths)):
        #create temp write latency, scale just for eval, reset
        temp_write_latency = nvsim_outputs[i].write_latency
        #set updated write latency
        nvsim_outputs[i].write_latency = temp_write_latency * pct_mask
        #repeat for spec geomean, graph example      
        access_pattern.write_freq = wr_base_spec * pct_traffic
        access_pattern.read_freq = rd_base_spec
        access_pattern.benchmark_name = "spec_"+str(pct_traffic)+"_"+str(pct_mask)
        this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
        this_result.evaluate()
        # These print to csv
        this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)
        #graph example start
        access_pattern.write_freq = wr_base_graph * pct_traffic
        access_pattern.read_freq = rd_base_graph
        access_pattern.benchmark_name = "fbbfs_"+str(pct_traffic)+"_"+str(pct_mask)
        this_result = ExperimentResult(access_pattern, nvsim_input_cfgs[i], nvsim_outputs[i])
        this_result.evaluate()
        # These print to csv
        this_result.report_result_benchmark(1, results_csv, cell_paths[i], cfg_paths[i], access_pattern, simulator)
        #reset write latency
        nvsim_outputs[i].write_latency = temp_write_latency

