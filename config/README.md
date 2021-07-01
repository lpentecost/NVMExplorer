# NVMExplorer - Config files

NVMExplorer allows for studies to be configured using a JSON format. For reference, we have included a few example config files: example_study.json, another_example_study.json, and bg_fefet_example_study.json. 
If no options are configured, default values will be used.
All available configuration options are listed below along with available values where applicable.

| Option | Description | 
| ------ | ------ |
| exp_name | user-specific ID for the study |
| read_frequency | number of reads per second |
| write_frequency | number of writes per second |
| read_size | size per read in bytes [B] |
| write_size | size per write in bytes [B] |
| working_set | total working set size in megabytes [MB] |
| cell_type | memory cell type. available options: ["STT", "PCM", "FeFET", "RRAM", "SRAM", "CTT"] |
| process_node | fabrication process node in nanometers [nm] |
| opt_target | nvsim optimization target. available options: ["ReadLatency", "ReadEDP", ...]. see nvsim submodule for full details |
| word_width | word width in bits [b] |
| capacity | capacity in megabytes [MB] |
| bits_per_cell | multi-level cell (mlc) configuration |
| traffic | type of application traffic. available options: ["generic", "graph", "dnn", "spec", "generic_write_buff"] |
| nvsim_path | absolute path for a custom nvsim |
| output_path | absolute path for a custom output directory |
| custom_cells | bool; indicates whether or not the user is providing customized cell details |

If custom_cells is set to true, please provide a list of customized cell configurations.  At a minimum, each customized cell configuration includes the cell type (e.g., "PCM", "RRAM") and a unique name to label the corresponding output files (e.g., "myFancyRRAMCell").

WIP details per techonology; see nvmexplorer_src/input_defs/cell_cfgs.py for more details

| Option | Description | Applicable Technologies |
| ------ | ----- | ----- |
| cell_type | technology type [SRAM, STT, PCM, RRAM, MLCRRAM, FeFET, MLCFeFET, CTT, MLCCTT] | ALL |
| cell_size_F2 | area of memory cell in F2 | ALL |
| access_CMOS_width | width of access transistor for CMOS access in F | ALL |
| r_on | Resistance value [ohm] of "on" or highest programmed cell state | STT, PCM |
| r_off | Resistance value [ohm] of "off" cell state | STT, PCM |
| read_mode | Select "voltage" read mode vs. "current" read mode | ALL |
| read_voltage | Read Voltage value (V) |  STT, PCM, (MLC)RRAM, (MLC)FeFET | 
