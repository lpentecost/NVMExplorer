import math
import pandas as pd
import nvmexplorer_src.input_defs


## Find technology tentpoles based on lowest/highest Mb per F^2
def form_tentpoles(data_df, cell_type, bits_per_cell):
  """ Generates best-case and worst-case NVSim cell files for a specified cell type and multi-level 
  cell configuration

  :param data_df: pandas dataframe object containing NVM spreadsheet data
  :type access_pattern: pandas dataframe
  :param cell_type: String specifying which NVM technology to use
  :type cell_type: String
  :param bits_per_cell: number of bits per cell for a potential multi-level cell configuration
  :type bits_per_cell: String
  :return: list of paths to NVSim cell files and :class:`NVSimInputConfig` objects containing NVSim input cfgs 
  for best-case and worst-case scenarios
  :rtype: list of Strings and :class:`NVSimInputConfig` objects
  """
  best_F2_per_Mb = 0.0
  best_F2_per_Mb_idx = 0
  worst_F2_per_Mb = 0.0
  worst_F2_per_Mb_idx = 0
  first = 1
 
  if (cell_type != 'SRAM'): 
      for index, row in data_df.iterrows():
          if not math.isnan(row['Cell Area [F2]']) and not math.isnan(row['Capacity [Mb]']):
              curr_F2_per_Mb = (row['Cell Area [F2]']/row['Capacity [Mb]'])
              if first == 1:
                  best_F2_per_Mb = curr_F2_per_Mb
                  best_F2_per_Mb_idx = index 
                  worst_F2_per_Mb = curr_F2_per_Mb
                  worst_F2_per_Mb_idx = index 
                  first = 0
              elif curr_F2_per_Mb < best_F2_per_Mb:
                  best_F2_per_Mb = curr_F2_per_Mb
                  best_F2_per_Mb_idx = index 
              elif curr_F2_per_Mb > worst_F2_per_Mb:
                  worst_F2_per_Mb = curr_F2_per_Mb
                  worst_F2_per_Mb_idx = index 
  
  ## Form cell cfgs and mem cfgs for best-case and worst-case default technologies
  best_case_cell_path = "data/cell_cfgs/{}_best_case.cell".format(cell_type)
  worst_case_cell_path = "data/cell_cfgs/{}_worst_case.cell".format(cell_type)
  
  if (cell_type == 'STT'):
      # STTRAM absolute best-case cell config
      best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.STTRAMCellConfig(
          cell_file_path=best_case_cell_path,
          cell_area_F2=data_df.at[best_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].min(skipna=True),
          read_power=data_df['Read Power [mW]'].min(skipna=True),
          reset_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          reset_energy=data_df['Write Energy [pJ]'].min(skipna=True),
          set_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          set_energy=data_df['Write Energy [pJ]'].min(skipna=True),
         )
      
      # STTRAM absolute worst-case cell config
      worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.STTRAMCellConfig(
          cell_file_path=worst_case_cell_path,
          cell_area_F2=data_df.at[worst_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].max(skipna=True),
          read_power=data_df['Read Power [mW]'].max(skipna=True),
          reset_pulse=data_df['Write Speed [ns]'].max(skipna=True),
          reset_energy=data_df['Write Energy [pJ]'].max(skipna=True),
          set_pulse=data_df['Write Speed [ns]'].max(skipna=True),
          set_energy=data_df['Write Energy [pJ]'].max(skipna=True),
         )
      
      best_case_cell_cfg.generate_cell_file()
      best_case_cell_cfg.append_cell_file()
      worst_case_cell_cfg.generate_cell_file()
      worst_case_cell_cfg.append_cell_file()
  
  elif (cell_type == 'PCM'):
      # STTRAM absolute best-case cell config
      best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.PCMCellConfig(
          cell_file_path=best_case_cell_path,
          cell_area_F2=data_df.at[best_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].min(skipna=True),
          reset_pulse=data_df['RESET Speed [ns]'].min(skipna=True),
          set_pulse=data_df['SET Speed [ns]'].min(skipna=True),
          reset_current=data_df['RESET current [uA]'].min(skipna=True),
          set_current=data_df['SET Current [uA]'].min(skipna=True),
         )
      
      # STTRAM absolute worst-case cell config
      worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.PCMCellConfig(
          cell_file_path=worst_case_cell_path,
          cell_area_F2=data_df.at[worst_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].max(skipna=True),
          reset_pulse=data_df['RESET Speed [ns]'].max(skipna=True),
          set_pulse=data_df['SET Speed [ns]'].max(skipna=True),
          reset_current=data_df['RESET current [uA]'].max(skipna=True),
          set_current=data_df['SET Current [uA]'].max(skipna=True),
         )
      
      best_case_cell_cfg.generate_cell_file()
      best_case_cell_cfg.append_cell_file()
      worst_case_cell_cfg.generate_cell_file()
      worst_case_cell_cfg.append_cell_file()
  
  elif (cell_type == 'CTT'): #FIXME fill in with details
    best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.CTTCellConfig()
    worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.CTTCellConfig() 
 
  elif (cell_type == 'RRAM'):
      # RRAM absolute best-case cell config
      best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.RRAMCellConfig(
          cell_file_path=best_case_cell_path,
          cell_area_F2=data_df.at[best_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].min(skipna=True),
          reset_pulse=data_df['RESET Speed [ns]'].min(skipna=True),
          set_pulse=data_df['SET Speed [ns]'].min(skipna=True),
          mlc=bits_per_cell,
         )
      
      # RRAM absolute worst-case cell config
      worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.RRAMCellConfig(
          cell_file_path=worst_case_cell_path,
          cell_area_F2=data_df.at[worst_F2_per_Mb_idx, 'Cell Area [F2]'],
          read_voltage=data_df['Read Voltage [V]'].max(skipna=True),
          reset_pulse=data_df['RESET Speed [ns]'].max(skipna=True),
          set_pulse=data_df['SET Speed [ns]'].max(skipna=True),
          mlc=bits_per_cell,
         )
      
      best_case_cell_cfg.generate_cell_file()
      best_case_cell_cfg.append_cell_file()
      worst_case_cell_cfg.generate_cell_file()
      worst_case_cell_cfg.append_cell_file()

  elif (cell_type == 'FeFET'):
      # FeFET absolute best-case cell config
      best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.FeFETCellConfig(
          cell_file_path=best_case_cell_path,
          cell_area_F2=data_df.at[best_F2_per_Mb_idx, 'Cell Area [F2]'], 
          set_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          reset_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          set_energy=data_df['Write Energy [pJ]'].min(skipna=True),
          reset_energy=data_df['Write Energy [pJ]'].min(skipna=True),
          mlc=bits_per_cell,
         )
      
      # FeFET absolute worst-case cell config
      worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.FeFETCellConfig(
          cell_file_path=worst_case_cell_path,
          cell_area_F2=data_df.at[worst_F2_per_Mb_idx, 'Cell Area [F2]'],
          set_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          reset_pulse=data_df['Write Speed [ns]'].min(skipna=True),
          set_energy=data_df['Write Energy [pJ]'].min(skipna=True),
          reset_energy=data_df['Write Energy [pJ]'].min(skipna=True),
          mlc=bits_per_cell,
         )
      
      best_case_cell_cfg.cell_ratio = 1.0
      best_case_cell_cfg.generate_cell_file()
      best_case_cell_cfg.append_cell_file()
      worst_case_cell_cfg.cell_ratio = 1.0
      worst_case_cell_cfg.generate_cell_file()
      worst_case_cell_cfg.append_cell_file()
 
  else:
      #Base SRAM cell
      best_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.SRAMCellConfig(
          cell_area_F2 = 146,
          cell_file_path=best_case_cell_path)
      worst_case_cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.SRAMCellConfig(
          cell_area_F2 = 146,
          cell_file_path=worst_case_cell_path)
      best_case_cell_cfg.generate_cell_file()
      best_case_cell_cfg.append_cell_file()
      worst_case_cell_cfg.generate_cell_file()
      worst_case_cell_cfg.append_cell_file()
  # FIXME: define best and worst case cell configs for other tech classes here
  #elif (cell_type == 'RRAM'):

  return best_case_cell_path, worst_case_cell_path, best_case_cell_cfg, worst_case_cell_cfg

##TODO; also have a generator that scrapes other characteristics from survey results


## Generate cell configuration from user input
def gen_custom_cell(cell_type, custom_cell_inputs):
  """ Generates NVSim cell files for a specified cell type and input characteristics

  :param cell_type: String specifying which NVM technology to use
  :type cell_type: String
  :param custom_cell_inputs: dictionary object specifying possible input params to cell def
  :return: path to NVSim cell file and :class:`NVSimInputConfig` object containing NVSim input cfgs 
  """
  
  ## Form cell cfgs and mem cfgs for best-case and worst-case default technologies
  cell_path = "data/cell_cfgs/{}_{}.cell".format(cell_type, custom_cell_inputs["name"])
 
  # depending on cell type, initialize default cell, then over-write params as provided, then generate cell file
 
  if (cell_type == 'STT'):
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.STTRAMCellConfig(
          cell_file_path=cell_path,
         )

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]
      if "r_on" in custom_cell_inputs:
          cell_cfg.r_on = custom_cell_inputs["r_on"]  
      if "r_off" in custom_cell_inputs:
          cell_cfg.r_off = custom_cell_inputs["r_off"]  
      if "read_mode" in custom_cell_inputs:
          cell_cfg.read_mode = custom_cell_inputs["read_mode"]  
      if "read_voltage" in custom_cell_inputs:
          cell_cfg.read_voltage = custom_cell_inputs["read_voltage"]  
      if "min_sense_voltage" in custom_cell_inputs:
          cell_cfg.min_sense_voltage = custom_cell_inputs["min_sense_voltage"]  
      if "read_power" in custom_cell_inputs:
          cell_cfg.read_power = custom_cell_inputs["read_power"]  
      if "reset_mode" in custom_cell_inputs:
          cell_cfg.reset_mode = custom_cell_inputs["reset_mode"]  
      if "reset_current" in custom_cell_inputs:
          cell_cfg.reset_current = custom_cell_inputs["reset_current"]  
      if "reset_pulse" in custom_cell_inputs:
          cell_cfg.reset_pulse = custom_cell_inputs["reset_pulse"]  
      if "reset_energy" in custom_cell_inputs:
          cell_cfg.reset_energy = custom_cell_inputs["reset_energy"]  
      if "set_mode" in custom_cell_inputs:
          cell_cfg.set_mode = custom_cell_inputs["set_mode"]  
      if "set_current" in custom_cell_inputs:
          cell_cfg.set_current = custom_cell_inputs["set_current"]  
      if "set_pulse" in custom_cell_inputs:
          cell_cfg.set_pulse = custom_cell_inputs["set_pulse"]  
      if "set_energy" in custom_cell_inputs:
          cell_cfg.set_energy = custom_cell_inputs["set_energy"]  
      if "mlc" in custom_cell_inputs:
          cell_cfg.mlc = custom_cell_inputs["mlc"]  
      if "read_floating" in custom_cell_inputs:
          cell_cfg.read_floating = custom_cell_inputs["read_floating"]  

      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()
  
  elif (cell_type == 'PCM'):
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.PCMCellConfig(
          cell_file_path=cell_path,
         )

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]
      if "r_on" in custom_cell_inputs:
          cell_cfg.r_on = custom_cell_inputs["r_on"]  
      if "r_off" in custom_cell_inputs:
          cell_cfg.r_off = custom_cell_inputs["r_off"]  
      if "read_mode" in custom_cell_inputs:
          cell_cfg.read_mode = custom_cell_inputs["read_mode"]  
      if "read_voltage" in custom_cell_inputs:
          cell_cfg.read_voltage = custom_cell_inputs["read_voltage"]  
      if "read_current" in custom_cell_inputs:
          cell_cfg.read_current = custom_cell_inputs["read_current"]  
      if "read_energy" in custom_cell_inputs:
          cell_cfg.read_energy = custom_cell_inputs["read_energy"]  
      if "reset_mode" in custom_cell_inputs:
          cell_cfg.reset_mode = custom_cell_inputs["reset_mode"]  
      if "reset_current" in custom_cell_inputs:
          cell_cfg.reset_current = custom_cell_inputs["reset_current"]  
      if "reset_pulse" in custom_cell_inputs:
          cell_cfg.reset_pulse = custom_cell_inputs["reset_pulse"]  
      if "set_mode" in custom_cell_inputs:
          cell_cfg.set_mode = custom_cell_inputs["set_mode"]  
      if "set_current" in custom_cell_inputs:
          cell_cfg.set_current = custom_cell_inputs["set_current"]  
      if "set_pulse" in custom_cell_inputs:
          cell_cfg.set_pulse = custom_cell_inputs["set_pulse"]  
      if "mlc" in custom_cell_inputs:
          cell_cfg.mlc = custom_cell_inputs["mlc"]  
      
      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()
  
  elif (cell_type == 'CTT'): #FIXME fill in with details
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.CTTCellConfig()

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]

 
  elif (cell_type == 'RRAM'):
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.RRAMCellConfig(
          cell_file_path=cell_path
         )

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]
      if "r_on_set_v" in custom_cell_inputs:
          cell_cfg.r_on_set_v = custom_cell_inputs["r_on_set_v"]
      if "r_off_set_v" in custom_cell_inputs:
          cell_cfg.r_off_set_v = custom_cell_inputs["r_off_set_v"]
      if "r_on_reset_v" in custom_cell_inputs:
          cell_cfg.r_on_reset_v = custom_cell_inputs["r_on_reset_v"]
      if "r_off_reset_v" in custom_cell_inputs:
          cell_cfg.r_off_reset_v = custom_cell_inputs["r_off_reset_v"]
      if "r_on_read_v" in custom_cell_inputs:
          cell_cfg.r_on_read_v = custom_cell_inputs["r_on_read_v"]
      if "r_off_read_v" in custom_cell_inputs:
          cell_cfg.r_off_read_v = custom_cell_inputs["r_off_read_v"]
      if "r_on_half_reset" in custom_cell_inputs:
          cell_cfg.r_on_half_reset = custom_cell_inputs["r_on_half_reset"]
      if "cap_on" in custom_cell_inputs:
          cell_cfg.cap_on = custom_cell_inputs["cap_on"]
      if "cap_off" in custom_cell_inputs:
          cell_cfg.cap_off = custom_cell_inputs["cap_off"]
      if "read_mode" in custom_cell_inputs:
          cell_cfg.read_mode = custom_cell_inputs["read_mode"]  
      if "read_voltage" in custom_cell_inputs:
          cell_cfg.read_voltage = custom_cell_inputs["read_voltage"]  
      if "read_power" in custom_cell_inputs:
          cell_cfg.read_power = custom_cell_inputs["read_power"]  
      if "reset_mode" in custom_cell_inputs:
          cell_cfg.reset_mode = custom_cell_inputs["reset_mode"]  
      if "reset_voltage" in custom_cell_inputs:
          cell_cfg.reset_voltage = custom_cell_inputs["reset_voltage"]  
      if "reset_pulse" in custom_cell_inputs:
          cell_cfg.reset_pulse = custom_cell_inputs["reset_pulse"]  
      if "reset_energy" in custom_cell_inputs:
          cell_cfg.reset_energy = custom_cell_inputs["reset_energy"]  
      if "set_mode" in custom_cell_inputs:
          cell_cfg.set_mode = custom_cell_inputs["set_mode"]  
      if "set_voltage" in custom_cell_inputs:
          cell_cfg.set_voltage = custom_cell_inputs["set_voltage"]  
      if "set_pulse" in custom_cell_inputs:
          cell_cfg.set_pulse = custom_cell_inputs["set_pulse"]  
      if "set_energy" in custom_cell_inputs:
          cell_cfg.set_energy = custom_cell_inputs["set_energy"]  
      if "mlc" in custom_cell_inputs:
          cell_cfg.mlc = custom_cell_inputs["mlc"]  
      if "read_floating" in custom_cell_inputs:
          cell_cfg.read_floating = custom_cell_inputs["read_floating"]  
      
      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()

  elif (cell_type == 'FeFET'):
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.FeFETCellConfig(
          cell_file_path=cell_path
         )

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]
      if "access_Vdrop" in custom_cell_inputs:
          cell_cfg.access_Vdrop = custom_cell_inputs["access_Vdrop"]
      if "r_on_set_v" in custom_cell_inputs:
          cell_cfg.r_on_set_v = custom_cell_inputs["r_on_set_v"]
      if "r_off_set_v" in custom_cell_inputs:
          cell_cfg.r_off_set_v = custom_cell_inputs["r_off_set_v"]
      if "r_on_reset_v" in custom_cell_inputs:
          cell_cfg.r_on_reset_v = custom_cell_inputs["r_on_reset_v"]
      if "r_off_reset_v" in custom_cell_inputs:
          cell_cfg.r_off_reset_v = custom_cell_inputs["r_off_reset_v"]
      if "r_on_read_v" in custom_cell_inputs:
          cell_cfg.r_on_read_v = custom_cell_inputs["r_on_read_v"]
      if "r_off_read_v" in custom_cell_inputs:
          cell_cfg.r_off_read_v = custom_cell_inputs["r_off_read_v"]
      if "r_on_half_reset" in custom_cell_inputs:
          cell_cfg.r_on_half_reset = custom_cell_inputs["r_on_half_reset"]
      if "cap_on" in custom_cell_inputs:
          cell_cfg.cap_on = custom_cell_inputs["cap_on"]
      if "cap_off" in custom_cell_inputs:
          cell_cfg.cap_off = custom_cell_inputs["cap_off"]
      if "read_mode" in custom_cell_inputs:
          cell_cfg.read_mode = custom_cell_inputs["read_mode"]  
      if "read_voltage" in custom_cell_inputs:
          cell_cfg.read_voltage = custom_cell_inputs["read_voltage"]  
      if "read_power" in custom_cell_inputs:
          cell_cfg.read_power = custom_cell_inputs["read_power"]  
      if "reset_mode" in custom_cell_inputs:
          cell_cfg.reset_mode = custom_cell_inputs["reset_mode"]  
      if "reset_voltage" in custom_cell_inputs:
          cell_cfg.reset_voltage = custom_cell_inputs["reset_voltage"]  
      if "reset_pulse" in custom_cell_inputs:
          cell_cfg.reset_pulse = custom_cell_inputs["reset_pulse"]  
      if "reset_energy" in custom_cell_inputs:
          cell_cfg.reset_energy = custom_cell_inputs["reset_energy"]  
      if "set_mode" in custom_cell_inputs:
          cell_cfg.set_mode = custom_cell_inputs["set_mode"]  
      if "set_voltage" in custom_cell_inputs:
          cell_cfg.set_voltage = custom_cell_inputs["set_voltage"]  
      if "set_pulse" in custom_cell_inputs:
          cell_cfg.set_pulse = custom_cell_inputs["set_pulse"]  
      if "set_energy" in custom_cell_inputs:
          cell_cfg.set_energy = custom_cell_inputs["set_energy"]  
      if "mlc" in custom_cell_inputs:
          cell_cfg.mlc = custom_cell_inputs["mlc"]  

      cell_cfg.cell_ratio = 1.0
      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()
  elif (cell_type == 'eDRAM' or cell_type == '3teDRAM'):
      #Base eDRAM cell
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.eDRAMCellConfig(
          cell_area_F2 = 60,
          cell_file_path=cell_path)

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]

      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()

  else:
      #Base SRAM cell
      cell_cfg = nvmexplorer_src.input_defs.cell_cfgs.SRAMCellConfig(
          cell_area_F2 = 146,
          cell_file_path=cell_path)

      # depending on exposed parameters per technology, check and assign input values
      if "cell_size_F2" in custom_cell_inputs:
          cell_cfg.cell_area = custom_cell_inputs["cell_size_F2"]
      if "access_CMOS_width" in custom_cell_inputs:
          cell_cfg.access_CMOS_width = custom_cell_inputs["access_CMOS_width"]
      if "nmos_width" in custom_cell_inputs:
          cell_cfg.nmos_width = custom_cell_inputs["nmos_width"]
      if "pmos_width" in custom_cell_inputs:
          cell_cfg.pmos_width = custom_cell_inputs["pmos_width"]
      if "read_mode" in custom_cell_inputs:
          cell_cfg.read_mode = custom_cell_inputs["read_mode"]

      cell_cfg.generate_cell_file()
      cell_cfg.append_cell_file()

  return cell_path, cell_cfg
