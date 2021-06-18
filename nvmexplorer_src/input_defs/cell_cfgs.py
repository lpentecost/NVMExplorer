
#define base cell definition and then specialize per technology
#FIXME: refactor some of this to avoid duplication

class NVSimCellConfig:
  def __init__(self,
                cell_file_path="data/cell_cfgs/SRAM.cell",
		mem_cell_type="SRAM", #name of cell
		cell_area=146, #cell area in F^2
		cell_ratio=1.46, #cell aspect ratio
		access_type="CMOS" #access type, or "None"
		):

    self.cell_file_path = cell_file_path
    self.mem_cell_type = mem_cell_type
    self.cell_area = cell_area
    self.cell_ratio = cell_ratio
    self.access_type = access_type

  def generate_cell_file(self):
    cell_file = open(self.cell_file_path, "w+")
    cell_file.write("-MemCellType: "+self.mem_cell_type+"\n")
    cell_file.write("-CellArea (F^2): %d\n" % self.cell_area)
    cell_file.write("-CellAspectRatio: %f\n" % self.cell_ratio)
    cell_file.write("-AccessType: "+self.access_type+"\n")
    cell_file.close() 

class SRAMCellConfig(NVSimCellConfig):
  def __init__(self,
        cell_file_path="../../data/cell_cfgs/SRAM.cell", 
		access_CMOS_width=1.31, #width of access (F)
		nmos_width = 2.08, #(F)
		pmos_width = 1.23, #(F)
                cell_area_F2 = 0.0,
		read_mode = "voltage",
    		mem_cfg_base = '''
-DesignTarget: RAM
-DeviceRoadmap: LOP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: non-H-tree
-InternalSensing: false
-Temperature (K): 350
-BufferDesignOptimization: balanced
'''
		):
    NVSimCellConfig.__init__(self, cell_file_path=cell_file_path, cell_area=cell_area_F2)
    self.access_CMOS_width = access_CMOS_width
    self.nmos_width = nmos_width
    self.pmos_width = pmos_width
    self.read_mode = read_mode
    self.mem_cfg_base = "-MemoryCellInputFile: " + self.cell_file_path + "\n" + mem_cfg_base + "\n\n" #customize base string for each technology
    self.mlc = 1

  def append_cell_file(self):
    """ Appends necessary parameters to NVSim cell file to prepare for simulation

    :param startHnd: Start index, defaults to 1
    :type startHnd: int, optional
    :param endHnd: End index, defaults to 0xFFFF
    :type endHnd: int, optional
    :param uuids: a list of UUID strings, defaults to None
    :type uuids: list, optional
    :return: List of returned :class:`bluepy.btle.Characteristic` objects
    :rtype: list
    """
    cell_file = open(self.cell_file_path, "a+")
    cell_file.write("-AccessCMOSWidth (F): %f\n" % self.access_CMOS_width)
    cell_file.write("-SRAMCellNMOSWidth (F): %f\n" % self.nmos_width)
    cell_file.write("-SRAMCellPMOSWidth (F): %f\n" % self.pmos_width)
    cell_file.write("-ReadMode: "+self.read_mode+"\n")
    cell_file.write("-ReadVoltage (V): 1.1\n")
    cell_file.write("-MinSenseVoltage (mV): 80\n")
    cell_file.write("-Stitching: 16\n")
    cell_file.close()

class RRAMCellConfig(NVSimCellConfig):
  def __init__(self,
        cell_file_path="../../data/cell_cfgs/RRAM.cell", 
        # using parameters from sample RRAM cell shipped with NVSIM as defaults
	access_CMOS_width=6, #width of access (F)
        cell_area_F2= 53,
        r_on_set_v = 100000, #ohm
        r_off_set_v = 10000000, #ohm
        r_on_reset_v = 100000, #ohm
        r_off_reset_v = 10000000, #ohm
        r_on_read_v = 1000000, #ohm
        r_off_read_v = 10000000, #ohm
        r_on_half_reset = 500000, #ohm
        cap_on = '1e-16', #F
        cap_off = '1e-16', #F
	read_mode = "current",
	read_voltage = 0.4, #V
        read_power = 0.16, #uW 
        reset_mode = "voltage",
        reset_voltage = 2.0, #V
        reset_pulse = 10, #ns
        reset_energy = 0.6, #pJ
        set_mode = "voltage",
        set_voltage = 2.0, #V
        set_pulse = 10, #ns
        set_energy = 0.6, #pJ
	mlc = 1, #bits per cell
	read_floating = False,
    	mem_cfg_base = '''
-DesignTarget: RAM
-DeviceRoadmap: LOP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: H-tree
-InternalSensing: true
-Temperature (K): 350
-BufferDesignOptimization: balanced
'''
		):
    NVSimCellConfig.__init__(self, cell_file_path=cell_file_path, cell_area=cell_area_F2)
    self.mem_cell_type = "memristor"
    self.cell_file_path=cell_file_path
    self.access_CMOS_width = access_CMOS_width
    self.r_on_set_v = r_on_set_v
    self.r_off_set_v = r_off_set_v
    self.r_on_reset_v = r_on_reset_v
    self.r_off_reset_v = r_off_reset_v
    self.r_on_read_v = r_on_read_v
    self.r_off_read_v = r_off_read_v
    self.r_on_half_reset = r_on_half_reset
    self.cap_on = cap_on
    self.cap_off = cap_off
    self.read_mode = read_mode
    self.read_voltage = read_voltage
    self.read_power = read_power
    self.reset_mode = reset_mode
    self.reset_voltage = reset_voltage
    self.reset_pulse = reset_pulse
    self.reset_energy = reset_energy
    self.set_mode = set_mode
    self.set_voltage = set_voltage
    self.set_pulse = set_pulse
    self.set_energy = set_energy
    self.mlc = mlc
    if self.mlc > 1:
      self.mem_cell_type = "MLCRRAM"
    self.read_floating = read_floating
    self.mem_cfg_base = "-MemoryCellInputFile: " + self.cell_file_path + "\n" + mem_cfg_base + "\n\n" #customize base string for each technology

  def append_cell_file(self):
    cell_file = open(self.cell_file_path, "a+")
    cell_file.write("-AccessCMOSWidth (F): %f\n" % self.access_CMOS_width)
    cell_file.write("-ResistanceOnAtSetVoltage (ohm): %d\n" % self.r_on_set_v)
    cell_file.write("-ResistanceOffAtSetVoltage (ohm): %d\n" % self.r_off_set_v)
    cell_file.write("-ResistanceOnAtResetVoltage (ohm): %d\n" % self.r_on_reset_v)
    cell_file.write("-ResistanceOffAtResetVoltage (ohm): %d\n" % self.r_off_reset_v)
    cell_file.write("-ResistanceOnAtReadVoltage (ohm): %d\n" % self.r_on_read_v)
    cell_file.write("-ResistanceOffAtReadVoltage (ohm): %d\n" % self.r_off_read_v)
    cell_file.write("-ResistanceOnAtHalfResetVoltage (ohm): %d\n" % self.r_on_half_reset)
    cell_file.write("-CapacitanceOn (F): "+self.cap_on+"\n")
    cell_file.write("-CapacitanceOff (F): "+self.cap_off+"\n")
    cell_file.write("-ReadMode: "+self.read_mode+"\n")
    cell_file.write("-ReadVoltage (V): %f\n" % self.read_voltage)
    cell_file.write("-ReadPower (uW): %f\n" % self.read_power)
    cell_file.write("-ResetMode: " + self.reset_mode+"\n")
    cell_file.write("-ResetVoltage (V): "+str(self.reset_voltage) +"\n")
    cell_file.write("-ResetPulse (ns): "+ str(self.reset_pulse) +"\n")
    cell_file.write("-ResetEnergy (pJ): " + str(self.reset_energy) + "\n")
    cell_file.write("-SetMode: "+self.set_mode+"\n")
    cell_file.write("-SetVoltage (V): "+str(self.set_voltage) +"\n")
    cell_file.write("-SetPulse (ns): "+str(self.set_pulse) +"\n")
    cell_file.write("-SetEnergy (pJ): "+str(self.set_energy) + "\n")
    if self.mlc > 1:
      cell_file.write("-CellLevels: "+str(2**self.mlc) + "\n")

    cell_file.close()

class STTRAMCellConfig(NVSimCellConfig):
  def __init__(self,
        cell_file_path="../../data/cell_cfgs/STTRAM.cell", 
        # using parameters from sample RRAM cell shipped with NVSIM as defaults
	access_CMOS_width=6, #width of access (F)
        cell_area_F2 = 54,
        r_on = 3000, #ohm
        r_off = 6000, #ohm
	read_mode = "current",
	read_voltage = 0.25, #V
        min_sense_voltage = 25, #mV
        read_power = 30, #uW 
        reset_mode = "current",
        reset_current = 80, #uA
        reset_pulse = 10, #ns
        reset_energy = 1, #pJ
        set_mode = "current",
        set_current = 80, #uA
        set_pulse = 10, #ns
        set_energy = 1, #pJ
	mlc = 1, #bits per cell
	read_floating = False,
    	mem_cfg_base = '''
-DesignTarget: RAM
-DeviceRoadmap: LOP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: H-tree
-InternalSensing: true
-Temperature (K): 350
-BufferDesignOptimization: balanced
'''
		):
    NVSimCellConfig.__init__(self, cell_file_path=cell_file_path, cell_area=cell_area_F2)
    self.mem_cell_type = "MRAM"
    self.cell_file_path=cell_file_path
    self.access_CMOS_width = access_CMOS_width
    self.r_on = r_on
    self.r_off = r_off
    self.read_mode = read_mode
    self.read_voltage = read_voltage
    self.min_sense_voltage = min_sense_voltage
    self.read_power = read_power
    self.reset_mode = reset_mode
    self.reset_current = reset_current
    self.reset_pulse = reset_pulse
    self.reset_energy = reset_energy
    self.set_mode = set_mode
    self.set_current = set_current
    self.set_pulse = set_pulse
    self.set_energy = set_energy
    self.mlc = mlc
    self.read_floating = read_floating
    self.mem_cfg_base = "-MemoryCellInputFile: " + self.cell_file_path + "\n" + mem_cfg_base + "\n\n" #customize base string for each technology

  def append_cell_file(self):
    cell_file = open(self.cell_file_path, "a+")
    cell_file.write("-AccessCMOSWidth (F): %f\n" % self.access_CMOS_width)
    cell_file.write("-ResistanceOn (ohm): %d\n" % self.r_on)
    cell_file.write("-ResistanceOff (ohm): %d\n" % self.r_off)
    cell_file.write("-ReadMode: "+self.read_mode+"\n")
    cell_file.write("-ReadVoltage (V): %f\n" % self.read_voltage)
    cell_file.write("-ReadPower (uW): %f\n" % self.read_power)
    cell_file.write("-ResetMode: " + self.reset_mode+"\n")
    cell_file.write("-ResetCurrent (uA): "+str(self.reset_current) +"\n")
    cell_file.write("-ResetPulse (ns): "+ str(self.reset_pulse) +"\n")
    cell_file.write("-ResetEnergy (pJ): " + str(self.reset_energy) + "\n")
    cell_file.write("-SetMode: "+self.set_mode+"\n")
    cell_file.write("-SetCurrent (uA): "+str(self.set_current) +"\n")
    cell_file.write("-SetPulse (ns): "+str(self.set_pulse) +"\n")
    cell_file.write("-SetEnergy (pJ): "+str(self.set_energy) + "\n")

    cell_file.close()

class PCMCellConfig(NVSimCellConfig):
  def __init__(self,
        cell_file_path="../../data/cell_cfgs/PCM.cell", 
        # using parameters from sample PCM cell shipped with NVSIM as defaults
        access_CMOS_width=6, #width of access (F)
        cell_area_F2=19,
        r_on = 1000, #ohm
        r_off = 1000000, #ohm
	read_mode = "voltage",
	read_current = 40, #uA
	read_voltage = 1, #V
        read_energy = 2, # pJ
        reset_mode = "current",
        reset_current = 10, #uA
        reset_pulse = 40, #ns
        set_mode = "current",
        set_current = 0.2, #uA
        set_pulse = 150, #ns
	mlc = 1, #bits per cell
    	mem_cfg_base = '''
-DesignTarget: RAM
-DeviceRoadmap: LOP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: H-tree
-InternalSensing: true
-Temperature (K): 350
-BufferDesignOptimization: balanced
'''
		):
    NVSimCellConfig.__init__(self, cell_file_path=cell_file_path, cell_area=cell_area_F2)
    self.mem_cell_type = "PCRAM"
    self.cell_file_path=cell_file_path
    self.access_CMOS_width = access_CMOS_width
    self.r_on = r_on
    self.r_off = r_off
    self.read_mode = read_mode
    self.read_current = read_current
    self.read_voltage = read_voltage
    self.read_energy = read_energy
    self.reset_mode = reset_mode
    self.reset_current = reset_current
    self.reset_pulse = reset_pulse
    self.set_mode = set_mode
    self.set_current = set_current
    self.set_pulse = set_pulse
    self.mlc = mlc
    self.mem_cfg_base = "-MemoryCellInputFile: " + self.cell_file_path + "\n" + mem_cfg_base + "\n\n" #customize base string for each technology

  def append_cell_file(self):
    cell_file = open(self.cell_file_path, "a+")
    cell_file.write("-AccessCMOSWidth (F): %f\n" % self.access_CMOS_width)
    cell_file.write("-ResistanceOn (ohm): %d\n" % self.r_on)
    cell_file.write("-ResistanceOff (ohm): %d\n" % self.r_off)
    cell_file.write("-ReadMode: "+self.read_mode+"\n")
    cell_file.write("-ReadVoltage (V): %f\n" % self.read_voltage)
    cell_file.write("-ReadEnergy (pJ): %f\n" % self.read_energy)
    cell_file.write("-ResetMode: " + self.reset_mode+"\n")
    cell_file.write("-ResetCurrent (uA): "+str(self.reset_current) +"\n")
    cell_file.write("-ResetPulse (ns): "+ str(self.reset_pulse) +"\n")
    cell_file.write("-SetMode: "+self.set_mode+"\n")
    cell_file.write("-SetCurrent (uA): "+str(self.set_current) +"\n")
    cell_file.write("-SetPulse (ns): "+str(self.set_pulse) +"\n")

    cell_file.close()


class FeFETCellConfig(NVSimCellConfig):
  def __init__(self,
        cell_file_path="../../data/cell_cfgs/FeFET.cell", 
        # using parameters from ND 500domain cell (write with verify) as defaults
	access_CMOS_width=0.01, #width of access (F)
	access_Vdrop=0.01, #voltage drop access device (V)
        cell_area_F2= 15,
        r_on_set_v = 3e4, #ohm
        r_off_set_v = 3e4, #ohm
        r_on_reset_v = 2e10, #ohm
        r_off_reset_v = 2e10, #ohm
        r_on_read_v = 7e4, #ohm
        r_off_read_v = 2e10, #ohm
        r_on_half_reset = 2.3e10, #ohm
        cap_on = '1e-16', #F
        cap_off = '1e-16', #F
        read_mode = "current",
        read_voltage = -0.03, #V
        read_power = 0.0014, #uW 
        reset_mode = "voltage",
        reset_voltage = -2.0, #V
        reset_pulse = 20, #ns
        reset_energy = 0.0002, #pJ
        set_mode = "voltage",
        set_voltage = 2.0, #V
        set_pulse = 20, #ns
        set_energy = 0.0029, #pJ
	mlc = 1, #bits per cell
	read_floating = False,
    	mem_cfg_base = '''
-DesignTarget: RAM
-DeviceRoadmap: LSTP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone
-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No
-Routing: H-tree
-InternalSensing: true
-Temperature (K): 350
-BufferDesignOptimization: balanced
'''
		):
    NVSimCellConfig.__init__(self, cell_file_path=cell_file_path, cell_area=cell_area_F2)
    self.mem_cell_type = "FeFET"
    self.cell_area=cell_area_F2
    self.cell_file_path=cell_file_path
    self.access_CMOS_width = access_CMOS_width
    self.access_Vdrop = access_Vdrop
    self.r_on_set_v = r_on_set_v
    self.r_off_set_v = r_off_set_v
    self.r_on_reset_v = r_on_reset_v
    self.r_off_reset_v = r_off_reset_v
    self.r_on_read_v = r_on_read_v
    self.r_off_read_v = r_off_read_v
    self.r_on_half_reset = r_on_half_reset
    self.cap_on = cap_on
    self.cap_off = cap_off
    self.read_mode = read_mode
    self.read_voltage = read_voltage
    self.read_power = read_power
    self.reset_mode = reset_mode
    self.reset_voltage = reset_voltage
    self.reset_pulse = reset_pulse
    self.reset_energy = reset_energy
    self.set_mode = set_mode
    self.set_voltage = set_voltage
    self.set_pulse = set_pulse
    self.set_energy = set_energy
    self.mlc = mlc
    if self.mlc > 1:
      self.mem_cell_type = "MLCFeFET"
    self.read_floating = read_floating
    self.mem_cfg_base = "-MemoryCellInputFile: " + self.cell_file_path + "\n" + mem_cfg_base + "\n\n" #customize base string for each technology

  def append_cell_file(self):
    cell_file = open(self.cell_file_path, "a+")
    cell_file.write("-AccessCMOSWidth (F): %f\n" % self.access_CMOS_width)
    cell_file.write("-ResistanceOnAtSetVoltage (ohm): %d\n" % self.r_on_set_v)
    cell_file.write("-ResistanceOffAtSetVoltage (ohm): %d\n" % self.r_off_set_v)
    cell_file.write("-ResistanceOnAtResetVoltage (ohm): %d\n" % self.r_on_reset_v)
    cell_file.write("-ResistanceOffAtResetVoltage (ohm): %d\n" % self.r_off_reset_v)
    cell_file.write("-ResistanceOnAtReadVoltage (ohm): %d\n" % self.r_on_read_v)
    cell_file.write("-ResistanceOffAtReadVoltage (ohm): %d\n" % self.r_off_read_v)
    cell_file.write("-ResistanceOnAtHalfResetVoltage (ohm): %d\n" % self.r_on_half_reset)
    cell_file.write("-CapacitanceOn (F): "+self.cap_on+"\n")
    cell_file.write("-CapacitanceOff (F): "+self.cap_off+"\n")
    cell_file.write("-ReadMode: "+self.read_mode+"\n")
    cell_file.write("-ReadVoltage (V): %f\n" % self.read_voltage)
    cell_file.write("-ReadPower (uW): %f\n" % self.read_power)
    cell_file.write("-ResetMode: " + self.reset_mode+"\n")
    cell_file.write("-ResetVoltage (V): "+str(self.reset_voltage) +"\n")
    cell_file.write("-ResetPulse (ns): "+ str(self.reset_pulse) +"\n")
    cell_file.write("-ResetEnergy (pJ): " + str(self.reset_energy) + "\n")
    cell_file.write("-SetMode: "+self.set_mode+"\n")
    cell_file.write("-SetVoltage (V): "+str(self.set_voltage) +"\n")
    cell_file.write("-SetPulse (ns): "+str(self.set_pulse) +"\n")
    cell_file.write("-SetEnergy (pJ): "+str(self.set_energy) + "\n")
    if self.mlc > 1:
      cell_file.write("-CellLevels: "+str(2**self.mlc) + "\n")

    cell_file.close()

if __name__ == '__main__':
  #test cell def generation
  test_default_cell = NVSimCellConfig()
  test_default_cell.generate_cell_file()

  test_sram_cell = SRAMCellConfig()
  test_sram_cell.generate_cell_file()
  test_sram_cell.append_cell_file()

  test_rram_cell = RRAMCellConfig()
  test_rram_cell.generate_cell_file()
  test_rram_cell.append_cell_file()
  
  test_sttram_cell = STTRAMCellConfig()
  test_sttram_cell.generate_cell_file()
  test_sttram_cell.append_cell_file()

  test_pcm_cell = PCMCellConfig()
  test_pcm_cell.generate_cell_file()
  test_pcm_cell.append_cell_file()

  test_fefet_cell = FeFETCellConfig()
  test_fefet_cell.generate_cell_file()
  test_fefet_cell.append_cell_file()
  print("Cell Def Tests Complete")

