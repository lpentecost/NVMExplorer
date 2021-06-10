from data.workload_data.spec_inputs import *
from data.workload_data.graph_inputs import *
from data.workload_data.dnn_inputs import *
from nvmexplorer_src.eval_utils import *


def generic_traffic(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path):
  """  Returns a tuple of :class:`ExperimentResult` objects containing results for best-case and 
  worst-case scenarios from a generic application traffic sweep that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_best_case_input_cfg: :class:`NVSimInputConfig` object which was used for best-case simulation
  :type nvsim_best_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_best_case_output: path to NVSim output file for best-case simulation
  :type nvsim_best_case_output: String
  :param nvsim_worst_case_input_cfg: :class:`NVSimInputConfig` object which was used for worst-case simulation
  :type nvsim_worst_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_worst_case_output: path to NVSim output file for worst-case simulation
  :type nvsim_worst_case_output: String
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param best_case_cell_path: path to NVSim input cell file for best-case scenario
  :type best_case_cell_path: String
  :param best_case_config_path: path to NVSim input config file for best-case scenario
  :type best_case_config_path: String
  :param worst_case_cell_path: path to NVSim input cell file for worst-case scenario
  :type worst_case_cell_path: String
  :param worst_case_config_path: path to NVSim input config file for worst-case scenario
  :type worst_case_config_path: String
  :return: tuple of :class:`ExperimentResult` object containing parsed NVSim results
  :rtype: list
  """
  write_accesses = [0, 1, 2, 1e1, 2e1, 1e2, 2e2, 1e3, 2e3, 1e4, 2e4, 1e5, 2e5, 1e6, 2e6, 1e7]
  read_accesses = [0, 1, 2, 1e1, 2e1, 1e2, 2e2, 1e3, 2e3, 1e4, 2e4, 1e5, 2e5, 1e6, 2e6, 1e7, 2e7, 1e8, 2e8, 1e9, 2e9, 1e10]
  for wr in write_accesses:
    for rd in read_accesses:
      access_pattern.write_freq = wr
      access_pattern.read_freq = rd
      this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
      this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
      this_result_best_case.evaluate()
      this_result_worst_case.evaluate()
      # These print to csv
      this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
      this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)


def graph_traffic(graph8MB, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path):
  """  Returns a tuple of :class:`ExperimentResult` objects containing results for best-case and 
  worst-case scenarios from a graph application traffic sweep that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_best_case_input_cfg: :class:`NVSimInputConfig` object which was used for best-case simulation
  :type nvsim_best_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_best_case_output: path to NVSim output file for best-case simulation
  :type nvsim_best_case_output: String
  :param nvsim_worst_case_input_cfg: :class:`NVSimInputConfig` object which was used for worst-case simulation
  :type nvsim_worst_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_worst_case_output: path to NVSim output file for worst-case simulation
  :type nvsim_worst_case_output: String
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param best_case_cell_path: path to NVSim input cell file for best-case scenario
  :type best_case_cell_path: String
  :param best_case_config_path: path to NVSim input config file for best-case scenario
  :type best_case_config_path: String
  :param worst_case_cell_path: path to NVSim input cell file for worst-case scenario
  :type worst_case_cell_path: String
  :param worst_case_config_path: path to NVSim input config file for worst-case scenario
  :type worst_case_config_path: String
  :return: tuple of :class:`ExperimentResult` object containing parsed NVSim results
  :rtype: list
  """
  for (i, name) in enumerate(graph8MB["names"]):
      access_pattern.benchmark_name = name
      if (graph8MB["read_freq"][i] > 0):
        access_pattern.name = name
        access_pattern.write_freq = graph8MB["write_freq"][i] 
        access_pattern.read_freq = graph8MB["read_freq"][i]
        this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
        this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
        this_result_best_case.evaluate()
        this_result_worst_case.evaluate()
        # These print to csv
        this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
        this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)
  

def dnn_traffic(DNN_weights, DNN_weights_acts, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path):
  """  Returns a tuple of :class:`ExperimentResult` objects containing results for best-case and 
  worst-case scenarios from a DNN application traffic sweep that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_best_case_input_cfg: :class:`NVSimInputConfig` object which was used for best-case simulation
  :type nvsim_best_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_best_case_output: path to NVSim output file for best-case simulation
  :type nvsim_best_case_output: String
  :param nvsim_worst_case_input_cfg: :class:`NVSimInputConfig` object which was used for worst-case simulation
  :type nvsim_worst_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_worst_case_output: path to NVSim output file for worst-case simulation
  :type nvsim_worst_case_output: String
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param best_case_cell_path: path to NVSim input cell file for best-case scenario
  :type best_case_cell_path: String
  :param best_case_config_path: path to NVSim input config file for best-case scenario
  :type best_case_config_path: String
  :param worst_case_cell_path: path to NVSim input cell file for worst-case scenario
  :type worst_case_cell_path: String
  :param worst_case_config_path: path to NVSim input config file for worst-case scenario
  :type worst_case_config_path: String
  :return: tuple of :class:`ExperimentResult` object containing parsed NVSim results
  :rtype: list
  """
  dnns = [ DNN_weights, DNN_weights_acts ]
  for dnn in dnns:
    for (i, name) in enumerate(dnn["names"]):
      access_pattern.benchmark_name = name
      if (dnn["reads"][i] > 0):
        access_pattern.name = name
        access_pattern.read_freq = dnn["reads"][i] * dnn["ips"][i]
        access_pattern.write_freq = dnn["writes"][i] * dnn["ips"][i]
        this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
        this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
        this_result_best_case.evaluate()
        this_result_worst_case.evaluate()
        # These print to csv
        this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
        this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)


def spec_traffic(spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC, access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path):
  """  Returns a tuple of :class:`ExperimentResult` objects containing results for best-case and 
  worst-case scenarios from SPEC2017 L3 traffic that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_best_case_input_cfg: :class:`NVSimInputConfig` object which was used for best-case simulation
  :type nvsim_best_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_best_case_output: path to NVSim output file for best-case simulation
  :type nvsim_best_case_output: String
  :param nvsim_worst_case_input_cfg: :class:`NVSimInputConfig` object which was used for worst-case simulation
  :type nvsim_worst_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_worst_case_output: path to NVSim output file for worst-case simulation
  :type nvsim_worst_case_output: String
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param best_case_cell_path: path to NVSim input cell file for best-case scenario
  :type best_case_cell_path: String
  :param best_case_config_path: path to NVSim input config file for best-case scenario
  :type best_case_config_path: String
  :param worst_case_cell_path: path to NVSim input cell file for worst-case scenario
  :type worst_case_cell_path: String
  :param worst_case_config_path: path to NVSim input config file for worst-case scenario
  :type worst_case_config_path: String
  :return: tuple of :class:`ExperimentResult` object containing parsed NVSim results
  :rtype: list
  """
  for benchmark in [spec8MBLLC, spec16MBLLC, spec16MBDRAM, spec16MBL2, spec32MBLLC, spec64MBLLC]:
    for (i, name) in enumerate(benchmark["names"]):  
      access_pattern.benchmark_name = name
      if (benchmark["reads"][i] > 0):
        access_pattern.name = name
        access_pattern.write_freq = benchmark["writes"][i] / benchmark["ex_time"][i]
        access_pattern.read_freq = benchmark["reads"][i] / benchmark["ex_time"][i]
        this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
        this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
        this_result_best_case.evaluate()
        this_result_worst_case.evaluate()
        # These print to csv
        this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
        this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)


def generic_traffic_with_write_buff(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output, nvsim_worst_case_input_cfg, nvsim_worst_case_output, results_csv, best_case_cell_path, best_case_cfg_path, worst_case_cell_path, worst_case_cfg_path):
  """  Returns a tuple of :class:`ExperimentResult` objects containing results for best-case and 
  worst-case scenarios from a generic application traffic sweep with write buffering that is evaluated

  :param access_pattern: :class:`AccessPattern` object
  :type access_pattern: :class:`AccessPattern`
  :param nvsim_best_case_input_cfg: :class:`NVSimInputConfig` object which was used for best-case simulation
  :type nvsim_best_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_best_case_output: path to NVSim output file for best-case simulation
  :type nvsim_best_case_output: String
  :param nvsim_worst_case_input_cfg: :class:`NVSimInputConfig` object which was used for worst-case simulation
  :type nvsim_worst_case_input_cfg: :class:`NVSimInputConfig`
  :param nvsim_worst_case_output: path to NVSim output file for worst-case simulation
  :type nvsim_worst_case_output: String
  :param results_csv: path to CSV file containing results
  :type results_csv: String
  :param best_case_cell_path: path to NVSim input cell file for best-case scenario
  :type best_case_cell_path: String
  :param best_case_config_path: path to NVSim input config file for best-case scenario
  :type best_case_config_path: String
  :param worst_case_cell_path: path to NVSim input cell file for worst-case scenario
  :type worst_case_cell_path: String
  :param worst_case_config_path: path to NVSim input config file for worst-case scenario
  :type worst_case_config_path: String
  :return: tuple of :class:`ExperimentResult` object containing parsed NVSim results
  :rtype: list
  """
  rd_base_spec = 3.7e6 #geomean of SPEC CPU2017 16MB cache accesses
  wr_base_spec = 2.3e6 #geomean of SPEC CPU2017
  rd_base_graph = 4.2e7 # FB BFS
  wr_base_graph = 1.9e5 # FB BFS

  percent_write_traffic_reduction = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1.0]
  percent_write_latency_mask = [0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99, 0.999, 1.0]

  for pct_traffic in percent_write_traffic_reduction:
    for pct_mask in percent_write_latency_mask:
      #create temp write latency, scale just for eval, reset
      temp_best_write_latency = nvsim_best_case_output.write_latency
      temp_worst_write_latency = nvsim_worst_case_output.write_latency
      #set updated write latency
      nvsim_best_case_output.write_latency = temp_best_write_latency * pct_mask
      nvsim_worst_case_output.write_latency = temp_worst_write_latency * pct_mask
      #repeat for spec geomean, graph example      
      access_pattern.write_freq = wr_base_spec * pct_traffic
      access_pattern.read_freq = rd_base_spec
      access_pattern.benchmark_name = "spec_"+str(pct_traffic)+"_"+str(pct_mask)
      this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
      this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
      this_result_best_case.evaluate()
      this_result_worst_case.evaluate()
      # These print to csv
      this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
      this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)
      #graph example start
      access_pattern.write_freq = wr_base_graph * pct_traffic
      access_pattern.read_freq = rd_base_graph
      access_pattern.benchmark_name = "fbbfs_"+str(pct_traffic)+"_"+str(pct_mask)
      this_result_best_case = ExperimentResult(access_pattern, nvsim_best_case_input_cfg, nvsim_best_case_output)
      this_result_worst_case = ExperimentResult(access_pattern, nvsim_worst_case_input_cfg, nvsim_worst_case_output)
      this_result_best_case.evaluate()
      this_result_worst_case.evaluate()
      # These print to csv
      this_result_best_case.report_result_benchmark(1, results_csv, best_case_cell_path, best_case_cfg_path, access_pattern)
      this_result_worst_case.report_result_benchmark(1, results_csv, worst_case_cell_path, worst_case_cfg_path, access_pattern)
      #reset write latency
      nvsim_best_case_output.write_latency = temp_best_write_latency
      nvsim_worst_case_output.write_latency = temp_worst_write_latency

