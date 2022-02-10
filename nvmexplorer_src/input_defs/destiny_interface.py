#initialize class for destiny output class, to be extracted from parsed destiny results and pickled as input to the analytical model
#per-technology specifications can be inherit
from nvmexplorer_src.input_defs.cell_cfgs import *

class DestinyInputConfig:
  def __init__(self,
                mem_cfg_file_path="../../data/mem_cfgs/test_SRAM.cfg", #path to destiny cfg input
		process_node=45, #chosen node in nm
		opt_target="ReadLatency", #optimization target
		word_width=64, #word width in bits
		capacity=4, #capacity in MB
		cell_type=SRAMCellConfig(), #pass the cell configuration
        stacked_die_count=1,
        partition_granularity=0,
        local_tsv_projection=0,
        global_tsv_projection=0,
        tsv_redundancy=1.0,
        monolithic_layer_count=1,
        allow_difference_tag_tech=1,
        memory_cell_input_file="",
        print_all_optimals=0,
        force_bank_3d="",
        force_bank_3da="",
        force_bank_a="",
        print_level=0

		):
    self.mem_cfg_file_path = mem_cfg_file_path
    self.process_node = process_node
    self.opt_target = opt_target
    self.word_width = word_width
    self.capacity = capacity
    self.cell_type = cell_type
    self.stacked_die_count = stacked_die_count
    self.partition_granularity = partition_granularity
    self.local_tsv_projection = local_tsv_projection
    self.global_tsv_projection = global_tsv_projection
    self.tsv_redundancy = tsv_redundancy
    self.monolithic_layer_count = monolithic_layer_count
    self.allow_difference_tag_tech = allow_difference_tag_tech
    self.memory_cell_input_file = memory_cell_input_file
    self.print_all_optimals = print_all_optimals
    self.force_bank_3d = force_bank_3d
    self.force_bank_3da = force_bank_3da
    self.force_bank_a = force_bank_a
    self.print_level = print_level


  def generate_mem_cfg(self):
    """ Creates a memory config file using characteristics of :class:`DestinyInputConfig` object 
    to be used as an input to Destiny
    """
    cfg_file = open(self.mem_cfg_file_path, "w+")
    cfg_file.write(self.cell_type.mem_cfg_base)
    cfg_file.write("-ProcessNode: %d\n" % self.process_node+"\n")
    cfg_file.write("-OptimizationTarget: "+self.opt_target+"\n")
    cfg_file.write("-WordWidth (bit): %d\n" % self.word_width+"\n")
    cfg_file.write("-Capacity (MB): %d\n" % self.capacity+"\n") 
    cfg_file.write("-StackedDieCount: %d\n" % self.stacked_die_count+"\n") #- Number of dies over which the memory is distributed
    cfg_file.write("-PartitionGranularity: %d\n" % self.partition_granularity+"\n")  
    #0: Coarse granularity: This assumes that address, control, and data signals are 
    #broadcast to all stacked dies and decoded on the destination die. 
    #1: Fine granularity: This assumes that address signals are pre-decoded on a 
    #separate logic layer and the undecoded address signals are broadcast to all 
    #stacked dies. The control and data are still shared. 
    #Note that the total number of dies in fine granularity is StackedDieCount + 1
    cfg_file.write("-LocalTSVProjection: %d\n" % self.local_tsv_projection+"\n")  
    #0: Use aggressive TSV projection from ITRS for local TSVs.
    #1: Use conservative values from industry measurements for local TSVs
    #Local TSVs are used in fine granularity partitioning to route pre-decoded signals
    cfg_file.write("-GlobalTSVProjection: %d\n" % self.global_tsv_projection+"\n") 
    #0: Use aggressive TSV projection from ITRS for global TSVs
    #1: Use conservative values from industry measurements for global TSVs
    #Global TSVs are used in both fine and coarse granularity partitioning to 
    #route broadcast signals (e.g., data and control signals)
    cfg_file.write("-TSVRedundancy: %f\n" % self.tsv_redundancy+"\n") #Any floating point value from 1.0 or higher (reasonably, about 
    #2.0 is the maximum). ((TSVRedundancy - 1)*100) is the percentage of extra TSVs 
    #assumed for each TSV cluster for fault tolerance / TSV yield issues.
    cfg_file.write("-MonolithicStackCount: %d\n" % self.monolithic_layer_count+"\n") #Integer value e.g., 1, 2, 4. This is the number of memory 
    #layers on the *same* die which are monolithically stacked.
    #cfg_file.write("-AllowDifferenceTagTech: %d\n" % self.allow_difference_tag_tech+"\n") #Allow the tag array of a cache to be a different 
    #technology than the data array (e.g., SRAM tag array with STT-RAM data array).
    #cfg_file.write("-MemoryCellInputFile: ".format(self.memory_cell_input_file)+"\n") #This parameter can be specified multiple times 
    #to consider multiple different technologies in the same simulation run.
    #cfg_file.write("-PrintAllOptimals: %d\n" % self.print_all_optimals+"\n") #Print the optimal design for each optimization 
    #target (can be used to find the best of multiple technology inputs).
    #cfg_file.write("-ForceBank3D: ".format(self.force_bank_3d)+"\n") #Dimensions of each bank in terms of number of Mats in each direction.
    #cfg_file.write("-ForceBank3DA: ".format(self.force_bank_3da)+"\n") #Same as ForceBank3D, except forcing the number of active Mats is not required
    #cfg_file.write("-ForceBankA: ".format(self.force_bank_a)+"\n") #Same as ForceBank in NVSim, except forcing the number of active Mats is not required.
    cfg_file.write("-PrintLevel: %d\n" % self.print_level+"\n") #0 -> does NOT produce CACHE DATA ARRAY DETAILS and CACHE TAG ARRAY DETAILS
    #1 -> produces CACHE DATA ARRAY DETAILS and CACHE TAG ARRAY DETAILS 
    if self.cell_type.mlc > 1:
      cell_levels = 2**(self.cell_type.mlc)
      cfg_file.write("-CellLevels: %d\n" % cell_levels+"\n")
    cfg_file.close()

class DestinyOutputConfig: #initialized to 16nm SRAM, 4MB
  def __init__(self,
		exp_name="default", #name or ID
		#retain relevant Destiny configs
		input_cfg = DestinyInputConfig(),
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
    """ Prints a summary of the parsed Destiny output results
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

def parse_destiny_output(filepath='output_examples/sram_0', input_cfg=DestinyInputConfig()):
  """ Returns a :class:`DestinyOutputConfig` object which gets populated with the output results in
  parsed from file_path. 

  :param filepath: path to Destiny output file
  :type filepath: String
  :param input_cfg: :class:`DestinyIntputConfig` object that was used to create the Destiny output 
  :type input_cfg: :class:`DestinyInputConfig` object
  :return: :class:`DestinyOutputConfig` object containing parsed Destiny results
  :rtype: :class:`DestinyOutputConfig`
  """
  #initialize base
  base = DestinyOutputConfig(input_cfg=input_cfg)

  with open(filepath, 'r') as f:
    print("File path in parse_destiny_output")
    print(filepath)
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
  test_input_cfg = DestinyInputConfig()
  test_input_cfg.cell_type.generate_cell_file()
  test_input_cfg.cell_type.append_cell_file()
  
  test_input_cfg.generate_mem_cfg()

  print("Memory config generation test complete.")



