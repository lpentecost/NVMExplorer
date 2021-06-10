#initialize class for nvsim output class, to be extracted from parsed nvsim results and pickled as input to the analytical model
#per-technology specifications can be inherit
from nvmexplorer_src.input_defs.cell_cfgs import *

class NVSimInputConfig:
  def __init__(self,
                mem_cfg_file_path="../../data/mem_cfgs/test_SRAM.cfg", #path to nvsim cfg input
		process_node=45, #chosen node in nm
		opt_target="ReadLatency", #optimization target
		word_width=64, #word width in bits
		capacity=4, #capacity in MB
		cell_type=SRAMCellConfig() #pass the cell configuration
		):
    self.mem_cfg_file_path = mem_cfg_file_path
    self.process_node = process_node
    self.opt_target = opt_target
    self.word_width = word_width
    self.capacity = capacity
    self.cell_type = cell_type

  def generate_mem_cfg(self):
    """ Creates a memory config file using characteristics of :class:`NVSimInputConfig` object 
    to be used as an input to NVSim
    """
    cfg_file = open(self.mem_cfg_file_path, "w+")
    cfg_file.write(self.cell_type.mem_cfg_base)
    cfg_file.write("-ProcessNode: %d\n" % self.process_node+"\n")
    cfg_file.write("-OptimizationTarget: "+self.opt_target+"\n")
    cfg_file.write("-WordWidth (bit): %d\n" % self.word_width+"\n")
    cfg_file.write("-Capacity (MB): %d\n" % self.capacity+"\n") 
    if self.cell_type.mlc > 1:
      cell_levels = 2**(self.cell_type.mlc)
      cfg_file.write("-CellLevels: %d\n" % cell_levels+"\n")
    cfg_file.close()

class NVSimOutputConfig: #initialized to 16nm SRAM, 4MB
  def __init__(self,
		exp_name="default", #name or ID
		#retain relevant NVSim configs
		input_cfg = NVSimInputConfig(),
		#also define all relevant outputs
		read_latency=-1, #ns
		read_bw=-1, #GB/s
		read_energy=-1, #pJ/access
		write_latency=-1, #ns
		write_bw=-1, #GB/s
		write_energy=-1, #nJ/access
		leakage_power=-1, #mW
		area=-1, #mm^2
		area_efficiency=-1 #percentage
		):
    # define all parameters
    self.exp_name = exp_name
    self.input_cfg = input_cfg
    self.read_latency = read_latency
    self.read_bw = read_bw
    self.read_energy = read_energy
    self.write_latency = write_latency
    self.write_bw = write_bw
    self.write_energy = write_energy
    self.leakage_power = leakage_power
    self.area = area
    self.area_efficiency = area_efficiency

  def print_summary(self):
    """ Prints a summary of the parsed NVSim output results
    """
    print("Experiment Name: "+self.exp_name)
    print("Read Latency (ns): %f" % self.read_latency)
    print("Read BW (GB/s): %f" % self.read_bw)
    print("Write Latency (ns): %f" % self.write_latency)
    print("Write BW (GB/s): %f" % self.write_bw)
    print("Read Energy (pJ): %f" % self.read_energy)
    print("Write Energy (pJ): %f" % self.write_energy)
    print("Leakage Power (mW): %f" % self.leakage_power)
    print("Area (mm^2): %f" % self.area)
    print("Area Efficiency (percent): %f" % self.area_efficiency)

def parse_nvsim_output(filepath='output_examples/sram_0', input_cfg=NVSimInputConfig()):
  """ Returns a :class:`NVSimOutputConfig` object which gets populated with the output results in
  parsed from file_path. 

  :param filepath: path to NVSim output file
  :type filepath: String
  :param input_cfg: :class:`NVSimIntputConfig` object that was used to create the NVSim output 
  :type input_cfg: :class:`NVSimInputConfig` object
  :return: :class:`NVSimOutputConfig` object containing parsed NVSim results
  :rtype: :class:`NVSimOutputConfig`
  """
  #initialize base
  base = NVSimOutputConfig(input_cfg=input_cfg)

  with open(filepath, 'r') as f:
    lines = f.readlines()

  # Get rid of new lines
  lines = map(lambda x: x.rstrip(), lines)

  for line in lines:
    if ' - Total Area =' in line and (base.area == -1):
      # sloppy fix, skip to end of line
      if "=" in line[line.index("=")+1:]:
        line = line[line.index("=")+1:]
      base.area = float(line[line.index("=")+1:][:-4])
      if line[-4:] == "um^2":
        base.area = base.area / (1000.)**2
    elif ' -  Read Latency' in line and (base.read_latency == -1):
      base.read_latency = float(line[line.index("=")+1:][:-2])
      if line[-2:] == "us": #scale to ns
        base.read_latency = base.read_latency * 1000.
      if line[-2:] == "ps": #scale to ns
        base.read_latency = base.read_latency / 1000.
      if line[-2:] == "ms": #scale to ns (yikes!)
        base.read_latency = base.read_latency * 1000000.
    elif ' - Area Efficiency =' in line:
      base.area_efficiency = float(line[line.index("=")+1:][:-1])
    elif ' - Read Bandwidth' in line:
      base.read_bw = float(line[line.index("=")+1:][:-4])
      if line[-4:] == "MB/s": #scale to GB/s
        base.read_bw = base.read_bw / 1024.
      if line[-4:] == "KB/s": #scale to GB/s
        base.read_bw = base.read_bw / 1024. / 1024.
    elif ' - Write Bandwidth' in line:
      base.write_bw = float(line[line.index("=")+1:][:-4])
      if line[-4:] == "MB/s": #scale to GB/s
        base.write_bw = base.write_bw / 1024.
      if line[-4:] == "KB/s": #scale to GB/s
        base.write_bw = base.write_bw / 1024. / 1024.
    elif ' -  Read Dynamic Energy ' in line:
      base.read_energy = float(line[line.index("=")+1:][:-2])
      if line[-2:] == "nJ": #scale to pJ
        base.read_energy = base.read_energy * 1000.
      if line[-2:] == "uJ": #scale to pJ
        base.read_energy = base.read_energy * 1000. * 1000.
    elif ' - Leakage Power ' in line:
      base.leakage_power = float(line[line.index("=")+1:][:-2])
      if line[-2:] == "uW": #scale to mW
        base.leakage_power = base.leakage_power / 1000.
    elif ' - Write Latency' in line and (base.write_latency == -1):
      base.write_latency = float(line[line.index("=")+1:][:-2])
      if line[-2:] == "us": #scale to ns
        base.write_latency = base.write_latency * 1000.
      if line[-2:] == "ps": #scale to ns
        base.write_latency = base.write_latency / 1000.
      if line[-2:] == "ms": #scale to ns (yikes!)
        base.write_latency = base.write_latency * 1000000.
    elif ' - Write Dynamic Energy ' in line:
      base.write_energy = float(line[line.index("=")+1:][:-2])
      if line[-2:] == "nJ": #scale to pJ
        base.write_energy = base.write_energy * 1000.
      if line[-2:] == "uJ": #scale to pJ
        base.write_energy = base.write_energy * 1000. * 1000.


    #separately detect any tech-specific quantities
    if input_cfg.cell_type.mem_cell_type == "SRAM":
      continue
    #FIXME set vs. reset for RRAM, support for other cells
    else:
      if ' - SET Latency' in line:
        base.write_latency = float(line[line.index("=")+1:][:-2])
        if line[-2:] == "us": #scale to ns
          base.write_latency = base.write_latency * 1000.
        if line[-2:] == "ps": #scale to ns
          base.write_latency = base.write_latency / 1000.
        if line[-2:] == "ms": #scale to ns (yikes!)
          base.write_latency = base.write_latency * 1000000.
      elif ' - SET Dynamic Energy ' in line:
        base.write_energy = float(line[line.index("=")+1:][:-2])
        if line[-2:] == "nJ": #scale to pJ
          base.write_energy = base.write_energy * 1000.
        if line[-2:] == "uJ": #scale to pJ
          base.write_energy = base.write_energy * 1000. * 1000.
        
  return base

if __name__ == '__main__':
  #test mem cfg definition and output parsing
  test_input_cfg = NVSimInputConfig()
  test_input_cfg.cell_type.generate_cell_file()
  test_input_cfg.cell_type.append_cell_file()
  
  test_input_cfg.generate_mem_cfg()

  print("Memory config generation test complete.")



