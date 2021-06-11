import sys
import os


def combine_csv(cell_type, mlc, bg=0):
    """ Writes to a file in csv format the combined results from a set of experiments for a certain
    cell type and mlc configuration

    :param cell_type: String indicating the NVM technology (e.g., PCM or STT)
    :type cell_type: String
    :param mlc: int indicating the number of bits per cell
    :type mlc: int
    """
    if (bg == 0):
      output_file_name = "output/results/{}_{}BPC-combined.csv".format(cell_type, mlc)
    else:
      output_file_name = "output/results/FeFET_BG_study.csv"
    
    if os.path.exists(output_file_name):
        os.remove(output_file_name)
    
    # Combine all the CSVs into one big CSV (one big CSV per technology class)
    with open(output_file_name, 'a') as big_fp:
      for filename in os.listdir("output/results/"):
          if (bg == 0):
              if filename.endswith(".csv") and cell_type in filename and "MB" in filename:
                  if (mlc == 1): 
                      with open("output/results/" + filename, 'r') as little_fp:
                          big_fp.write(little_fp.read())
                  elif ("2BPC" in filename):
                      with open("output/results/" + filename, 'r') as little_fp:
                          big_fp.write(little_fp.read())
          else:
              if filename.endswith(".csv") and "BG" in filename:
                  with open("output/results/" + filename, 'r') as little_fp:
                      big_fp.write(little_fp.read())

    
    # Now remove all headers except for the first one 
    with open(output_file_name, 'r') as big_fp:
      lines = big_fp.readlines() 
    
    first = 0
    with open(output_file_name, 'w') as big_fp:
      for line in lines:
          if first == 0:
              big_fp.write(line)
              first = 1
          elif first == 1:
              if 'MemCellType' not in line:
                  big_fp.write(line)
    
