Welcome to nvmFI, a simple interface for quantifying the impact of memory faults and failure modes on application accuracy.

nvmFI is derived from Ares [cite] and retains pyTorch compatibility to evaluate DNN weights and/or activations stored in NVMs with varying properties (e.g., fault models and MLC programming).

Dependencies include PyTorch, numpy, scipy, and (for graph analytics tasks) snapPY.

snapPY graph API is integrated to explore fault tolerance of graph analytics tasks.

Use the the data generator or bring your own data (in numpy or pyTorch tensor format) to perform fault injection according to storage mapping.

runFI.sh provides a sample injection study for a 1KB input matrix stored in 2-bit MLC RRAM.

If using nvmFI for standalone studies, please cite [] ?

Lillian Pentecost and Marco Donato, 2020
