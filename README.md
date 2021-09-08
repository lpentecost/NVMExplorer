NVMExplorer
---------------------
by Lillian Pentecost and Alexander Hankin, 2021

This is a beta version of a broad design space exploration framework for evaluating and comparing different on-chip memory solutions (including embeddable non-volatile memory technologies such as RRAM, PCM, STT, FeFET, and CTT devices) with system-level constraints and application-level impacts in-the-loop.

Users can configure experiments with customized cell-level parameters, specific memory array design priorities and constraints, and analytically evaluate the performance and efficiency of memory solutions for specific application traffic patterns.  Documentation is a work-in-progress, but templates for various experiments, example cell confiugrations, and example application traffic are provided with sample configurations in the `config` directory.  Additionally, fault injection experiments for different NVM configurations and fault models can be developed and run within `nvmexplorer_src/nvmFI`, and surveyed cell-level parameters for various technologies are provided in `output/NVM_data` and leveraged in example studies (see sample configs for details).

Please see https://nvmexplorer.seas.harvard.edu for additional documentation and details, and get started using the instructions below.

For example studies or to cite this work, please see https://arxiv.org/abs/2109.01188


Getting Started:
--------------------

NVMExplorer relies on an extended and modified version of NVSim

Be sure to clone this repository with ``git clone --recurse-submodules https://github.com/lpentecost/NVMExplorer''

After cloning, compile nvsim_src:

> cd nvmexplorer_src/nvsim_src
>
> make

Prior to running NVMExplorer, please verify you are using Python 3.X and have the following packages available:
- pandas
- numpy

Please see additional documentation for tutorials, fault injection setup, and more information

Usage:
---------------------
> python run.py config/[config name].json

Documentation and Data Visualizations:
---------------------
http://www.nvmexplorer.seas.harvard.edu

Contact:
---------------------

Questions, comments, or feature requests?  Please reach out directly:

nvmexplorer@gmail.com


Citations:
---------------------

If you use or expand on this work, please cite NVMExplorer [https://arxiv.org/abs/2109.01188]
