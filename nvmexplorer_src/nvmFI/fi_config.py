import torch
import numpy as np

# define different NVM fault models
nvm_model = 'rram_mlc'

# provide paths to fault model distributions stored in nvm_data directory
# for more information, please see nvmexplorer.seas.harvard.edu
nvm_dict = {'rram_mlc'  : 'mlc_rram_args.p' }

# optional print statements during nvmFI execution
Debug=True
 

if torch.cuda.is_available():
  pt_device = "cuda"
  if Debug:
    print("CUDA is available")
else:
  pt_device = "cpu"

