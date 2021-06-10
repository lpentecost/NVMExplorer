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

