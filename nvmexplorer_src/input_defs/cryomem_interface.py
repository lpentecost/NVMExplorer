#initialize class for cryomem output class, to be extracted from parsed cryomem results and pickled as input to the analytical model
#per-technology specifications can be inherit
from nvmexplorer_src.input_defs.cell_cfgs import *

class CryoMEMInputConfig:
  def __init__(self,
                mem_cfg_file_path="../../data/mem_cfgs/cache-sram.cfg", #path to cryomem cfg input
                capacity=8,
                word_width=64,
		cell_type=CryoMEMSRAMCellConfig(), #pass the cell configuration
		process_node=45, #chosen node in nm
                temperature=350,
                banks=1,
		):
    self.mem_cfg_file_path = mem_cfg_file_path
    self.capacity = capacity
    self.word_width = word_width
    self.cell_type = cell_type
    self.process_node = process_node
    self.temperature = temperature
    self.banks = banks


  def generate_mem_cfg(self):
    """ Creates a memory config file using characteristics of :class:`CryoMEMInputConfig` object 
    to be used as an input to CryoMEM
    """
    self.process_node = self.process_node/1000
    self.capacity = self.capacity*1024*1024
    cfg_file = open(self.mem_cfg_file_path, "w+")
    cfg_file.write('-size (bytes) %d\n' % self.capacity+'\n')
    cfg_file.write('-Array Power Gating - "false"\n')
    cfg_file.write('-WL Power Gating - "false"\n')
    cfg_file.write('-CL Power Gating - "false"\n')
    cfg_file.write('-Bitline floating - "false"\n')
    cfg_file.write('-Interconnect Power Gating - "false"\n')
    cfg_file.write('-Power Gating Performance Loss 0.01\n')
    cfg_file.write('-block size (bytes) 64\n')
    cfg_file.write('-associativity 8\n')
    cfg_file.write('-read-write port 2\n')
    cfg_file.write('-exclusive read port 0\n')
    cfg_file.write('-exclusive write port 0\n')
    cfg_file.write('-single ended read ports 0\n')
    cfg_file.write('-UCA bank count %d\n' % self.banks+'\n')
    cfg_file.write('-technology (u) %f\n' % self.process_node+'\n')
    cfg_file.write('-page size (bits) 8192\n')
    cfg_file.write('-burst length 8\n')
    cfg_file.write('-internal prefetch width 8\n')
    cfg_file.write('-Data array cell type - "itrs-lop"\n')
    cfg_file.write('-Data array peripheral type - "itrs-lop"\n')
    cfg_file.write('-Tag array cell type - "itrs-lop"\n')
    cfg_file.write('-Tag array peripheral type - "itrs-lop"\n')
    cfg_file.write('-output/input bus width 64\n')
    cfg_file.write('-operating temperature (K) 360\n')
    cfg_file.write('-cache type "ram"\n')
    cfg_file.write('-tag size (b) "default"\n')
    cfg_file.write('-access mode (normal, sequential, fast) - "normal"\n')
    cfg_file.write('-design objective (weight delay, dynamic power, leakage power, cycle time, area) 100:0:0:100:0\n')
    cfg_file.write('-deviate (delay, dynamic power, leakage power, cycle time, area) 0:100:100:0:100\n')
    cfg_file.write('-NUCAdesign objective (weight delay, dynamic power, leakage power, cycle time, area) 100:100:0:0:100\n')
    cfg_file.write('-NUCAdeviate (delay, dynamic power, leakage power, cycle time, area) 10:10000:10000:10000:10000\n')
    cfg_file.write('-Optimize ED or ED^2 (ED, ED^2, NONE): "ED^2"\n')
    cfg_file.write('-Cache model (NUCA, UCA)  - "UCA"\n')
    cfg_file.write('-NUCA bank count 0\n')
    cfg_file.write('-Wire signaling (fullswing, lowswing, default) - "Global_30"\n')
    cfg_file.write('-Wire inside mat - "semi-global"\n')
    cfg_file.write('-Wire outside mat - "semi-global"\n')
    cfg_file.write('-Interconnect projection - "conservative"\n')
    cfg_file.write('-Core count 8\n')
    cfg_file.write('-Cache level (L2/L3) - "L3"\n')
    cfg_file.write('-Add ECC - "true"\n')
    cfg_file.write('-Print level (DETAILED, CONCISE) - "DETAILED"\n')
    cfg_file.write('-Print input parameters - "true"\n')
    cfg_file.write('-Force cache config - "false"\n')
    cfg_file.write('-Ndwl 1\n')
    cfg_file.write('-Ndbl 1\n')
    cfg_file.write('-Nspd 0\n')
    cfg_file.write('-Ndcm 1\n')
    cfg_file.write('-Ndsaml1 0\n')
    cfg_file.write('-Ndsam2 0\n')
    cfg_file.write('-dram_type "DDR3"\n')
    cfg_file.write('-io state "WRITE"\n')
    cfg_file.write('-addr_timing 1.0\n') 
    cfg_file.write('-mem_density 4 Gb\n')
    cfg_file.write('-bus_freq 800 MHz\n')
    cfg_file.write('-duty_cycle 1.0\n')
    cfg_file.write('-activity_dq 1.0\n')
    cfg_file.write('-activity_ca 0.5\n')
    cfg_file.write('-num_dq 72\n')
    cfg_file.write('-num_dqs 18\n')
    cfg_file.write('-num_ca 25\n')
    cfg_file.write('-num_clk  2\n')
    cfg_file.write('-num_mem_dq 2\n')
    cfg_file.write('-mem_data_width 8\n')
    cfg_file.write('-rtt_value 10000\n')
    cfg_file.write('-ron_value 34\n')
    cfg_file.write('-tflight_value\n')
    cfg_file.write('-num_bobs 1\n')
    cfg_file.write('-capacity 80\n')
    cfg_file.write('-num_channels_per_bob 1\n')
    cfg_file.write('-first metric "Cost"\n')
    cfg_file.write('-second metric "Bandwidth"\n')
    cfg_file.write('-third metric "Energy"\n')
    cfg_file.write('-DIMM model "ALL"\n')
    cfg_file.write('-mirror_in_bob "F"\n')
    cfg_file.write(self.cell_type.mem_cfg_base)
    cfg_file.close()

class CryoMEMOutputConfig: #initialized to 16nm SRAM, 4MB
  def __init__(self,
		exp_name="default", #name or ID
		#retain relevant CryoMEM configs
		input_cfg = CryoMEMInputConfig(),
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
    """ Prints a summary of the parsed CryoMEM output results
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

def parse_cryomem_output(filepath='output_examples/sram_0', input_cfg=CryoMEMInputConfig()):
  """ Returns a :class:`CryoMEMOutputConfig` object which gets populated with the output results in
  parsed from file_path. 

  :param filepath: path to CryoMEM output file
  :type filepath: String
  :param input_cfg: :class:`CryoMEMIntputConfig` object that was used to create the CryoMEM output 
  :type input_cfg: :class:`CryoMEMInputConfig` object
  :return: :class:`CryoMEMOutputConfig` object containing parsed CryoMEM results
  :rtype: :class:`CryoMEMOutputConfig`
  """
  #initialize base
  base = CryoMEMOutputConfig(input_cfg=input_cfg)

  num_banks = 0
  block_size = 0

  with open(filepath, 'r') as f:
    lines = f.readlines()

  
  # Get rid of new lines
  lines = map(lambda x: x.rstrip(), lines)

  for line in lines:
    if 'Data array: Area (mm2)' in line and (base.area == -1):
      base.area = float(line.split(": ")[2])
    elif 'Access time (ns):' in line and (base.read_latency == -1):
      base.read_latency = float(line.split(":")[1])
      base.write_latency = float(line.split(":")[1])
    elif 'Number of banks:' in line:
      num_banks = float(line.split(":")[1])
    elif 'Area efficiency (Memory cell area/Total area) -' in line:
      base.area_efficiency = float((line.split("-")[1]).replace('%', ''))
    elif 'Block size (bytes):' in line:
      block_size = float(line.split(":")[1])
    elif 'Total dynamic read energy per access (nJ):' in line:
      base.read_energy = float(line.split(":")[1])
      base.read_energy = base.read_energy * 1000.
    elif 'Total leakage power of a bank (mW):' in line:
      base.leakage_power = float(line.split(":")[1])*num_banks
    elif 'Total dynamic write energy per access (nJ):' in line:
      base.write_energy = float(line.split(":")[1])
      base.write_energy = base.write_energy * 1000.
      
    base.read_bw = block_size/base.read_latency
    base.write_bw = block_size/base.write_latency
        
  return base

if __name__ == '__main__':
  #test mem cfg definition and output parsing
  test_input_cfg = CryoMEMInputConfig()
  test_input_cfg.cell_type.generate_cell_file()
  test_input_cfg.cell_type.append_cell_file()
  
  test_input_cfg.generate_mem_cfg()

  print("Memory config generation test complete.")



